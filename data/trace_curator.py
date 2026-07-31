#!/usr/bin/env python3
"""Interactive SFT trace curator - validate simulated conversation traces field-by-field.

Usage:
    python trace_curator.py                  # Interactive judgment mode (default)
    python trace_curator.py --batch          # Auto-validate clean traces only
    python trace_curator.py --summary        # Show statistics on all traces
"""

import json
import os
import sys
from collections import defaultdict

CONV_DIR = os.path.expanduser("~/.assistant/data/conversations/")
STATE_PATH = os.path.join(CONV_DIR, "judgment_state.json")

# Corruption detection patterns (per skill)
BACKTICK_CORRUPTION = True  # User message wrapped in backticks = simulator acting as assistant
ASSISTANT_LIKE_STARTS = [
    "voici", "bien sûr", "c'est une", "je peux",
    "je vais", "merci pour", "excellent choix", "parfait"
]

ERROR_PATTERNS_IN_TOOLS = ["error", "traceback", "nameerror"]


def parse_trace_file(filepath):
    """Parse sim_*.jsonl file, returning the last (full) conversation state.

    Files may contain multiple JSON lines where each line represents a progressive
    snapshot of the conversation up to that point. The LAST line has the full state.
    """
    with open(filepath) as f:
        content = f.read()

    # Try loading entire file as one JSON object
    try:
        data = json.loads(content.strip())
        if isinstance(data, dict):
            return data.get("request_args", {}).get("messages", []) or \
                   data.get("messages", [])
    except (json.JSONDecodeError, TypeError):
        pass

    # Fall back to JSONL: take last non-empty line as full state
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    if not lines:
        return None

    try:
        obj = json.loads(lines[-1])
        return obj.get("request_args", {}).get("messages", []) or \
               obj.get("messages", [])
    except json.JSONDecodeError:
        return None


def load_judgment_state():
    """Load persisted judgment state from disk."""
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_judgment_state(state):
    """Persist judgment state to disk atomically."""
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_PATH)


def analyze_trace(messages):
    """Analyze a parsed trace for quality issues.

    Returns dict with 'errors', 'warnings', and 'is_corrupted'.
    """
    result = {"errors": [], "warnings": [], "is_corrupted": False}

    user_msgs = [m for m in messages if m.get("role") == "user"]
    tool_msgs = [m for m in messages if m.get("role") == "tool"]
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]

    # --- User message corruption check ---
    corrupted_turns = []
    for i, u in enumerate(user_msgs):
        content = u.get("content", "")

        has_backticks = content.startswith("`") and content.endswith("`")
        is_assistant_like = any(
            content.lower().startswith(p) for p in ASSISTANT_LIKE_STARTS
        )

        if has_backticks:
            corrupted_turns.append((i, "backtick_wrapped_code"))
        elif is_assistant_like:
            corrupted_turns.append((i, "assistant-like_prefix"))

    if corrupted_turns:
        result["is_corrupted"] = True
        msg = "; ".join(
            f"turn {t}: {flag}" for t, flag in corrupted_turns
        )
        result["errors"].append(f"{len(corrupted_turns)} user message(s) corrupted: {msg}")

    # --- Tool result error check ---
    error_tool_indices = []
    for i, t in enumerate(tool_msgs):
        content = (t.get("content") or "").lower()
        if any(kw in content for kw in ERROR_PATTERNS_IN_TOOLS):
            error_tool_indices.append(i)

    if error_tool_indices:
        result["warnings"].append(
            f"{len(error_tool_indices)} tool result(s) contain execution errors"
        )

    # --- Assistant response quality check ---
    empty_assistant = []
    for i, a in enumerate(messages):
        if a.get("role") != "assistant":
            continue
        content = (a.get("content") or "").strip()
        tc = a.get("tool_calls", []) or []
        # Empty assistant with no tool calls is suspicious
        if not content and not tc:
            empty_assistant.append(i)

    if empty_assistant:
        result["warnings"].append(
            f"{len(empty_assistant)} assistant message(s) with NO text AND NO tool calls"
        )

    return result


def display_trace(messages, filename=""):
    """Display a parsed trace in human-readable format."""
    user_turns = sum(1 for m in messages if m.get("role") == "user")
    tool_results = sum(1 for m in messages if m.get("role") == "tool")
    assis_responses = sum(1 for m in messages if m.get("role") == "assistant")

    print(f"\n{'='*70}")
    print(f"FILE: {filename or 'unknown'}")
    print(f"Turns: {user_turns} | Tool results: {tool_results} | Assistant: {assis_responses}")
    print(f"{'='*70}\n")

    for i, msg in enumerate(messages):
        role = msg.get("role", "?")

        if role == "system":
            continue

        elif role == "user":
            content = msg.get("content", "")
            has_backticks = content.startswith("`") and content.endswith("`")
            is_assistant_like = any(
                content.lower().startswith(p) for p in ASSISTANT_LIKE_STARTS
            )
            flags = []
            if has_backticks:
                flags.append("⚠️ CORRUPTED (backticks)")
            elif is_assistant_like:
                flags.append("⚠️ assistant-like start")

            tag = f" {flags[0]}" if flags else ""
            print(f"[{i:2d}] USER{tag}: {repr(content[:90])}")

        elif role == "assistant":
            tc = msg.get("tool_calls", []) or []
            content = (msg.get("content") or "").strip()

            if not content and not tc:
                print(f"[{i:2d}] ASSISTANT ⚠️ EMPTY: no text, no tools")
            elif content:
                tc_info = f" | {len(tc)} tool(s)" if tc else ""
                print(f"[{i:2d}] ASSISTANT: {repr(content[:90])}{tc_info}")

        elif role == "tool":
            content = msg.get("content", "") or ""
            is_error = any(kw in content.lower() for kw in ERROR_PATTERNS_IN_TOOLS)

            if is_error:
                first_line = content.split("\n")[0][:80]
                print(f"[{i:2d}] ⚠️ TOOL ERROR: {repr(first_line)}")
            else:
                preview = (
                    content[:60].replace("\n", " ")
                    + ("..." if len(content) > 60 else "")
                )
                print(f"[{i:2d}] TOOL: {preview}")


def get_all_sim_traces():
    """List all sim_*.jsonl files in the conversations directory."""
    return sorted(
        f for f in os.listdir(CONV_DIR)
        if f.startswith("sim_") and f.endswith(".jsonl")
    )


def batch_validate(state):
    """Auto-validate traces that pass quality checks without errors/warnings."""
    sim_files = get_all_sim_traces()
    pending = [f for f in sim_files if f not in state]

    print(f"Batch mode: validating {len(pending)} pending traces...\n")

    validated = 0
    rejected = 0
    skipped = 0

    import time

    for fname in pending:
        filepath = os.path.join(CONV_DIR, fname)
        messages = parse_trace_file(filepath)

        if not messages:
            state[fname] = {
                "status": "rejected",
                "reason": "parse_error",
                "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            rejected += 1
            continue

        analysis = analyze_trace(messages)

        if not analysis["errors"] and not analysis["warnings"]:
            state[fname] = {
                "status": "validated",
                "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "auto_validated": True,
                "score": 1.0,
            }
            validated += 1
        elif not analysis["errors"]:
            # Warnings only (e.g., tool errors) - mark for review
            state[fname] = {
                "status": "needs_review",
                "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "warnings": analysis["warnings"],
            }
            skipped += 1
        else:
            # Has errors - reject
            state[fname] = {
                "status": "rejected",
                "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "reasons": analysis["errors"],
            }
            rejected += 1

    save_judgment_state(state)
    return validated, rejected, skipped


def interactive_loop():
    """Interactive field-by-field judgment loop."""
    state = load_judgment_state()
    sim_files = get_all_sim_traces()
    pending = [f for f in sim_files if f not in state]

    if not pending:
        print("No traces left to judge!")
        return

    print(f"Interactive mode: {len(pending)} traces pending\n")

    import time

    for idx, fname in enumerate(pending, 1):
        filepath = os.path.join(CONV_DIR, fname)
        messages = parse_trace_file(filepath)

        if not messages:
            print(f"[{idx}/{len(pending)}] {fname} — SKIP (parse error)")
            state[fname] = {
                "status": "rejected",
                "reason": "parse_error",
                "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            save_judgment_state(state)
            continue

        print(f"\n[{idx}/{len(pending)}] {fname}")
        print("-" * 70)

        display_trace(messages, fname)

        analysis = analyze_trace(messages)

        # Print analysis summary
        if analysis["errors"]:
            for err in analysis["errors"]:
                print(f"\n⚠️ ERROR: {err}")
        if analysis["warnings"]:
            for warn in analysis["warnings"]:
                print(f"ℹ️ WARNING: {warn}")

        # Show action menu
        print("\nActions:")
        print("  [V] Validate — accept as-is, move to next")
        print("  [R] Reject — skip this trace entirely")
        print("  [S] Skip — mark for later review (won't count)")

        while True:
            try:
                action = input("\nChoose (v/r/s): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return  # Graceful exit on Ctrl+C or EOF

            if action == "v":
                state[fname] = {
                    "status": "validated",
                    "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "errors_found": len(analysis["errors"]),
                    "warnings_found": len(analysis["warnings"]),
                }
                save_judgment_state(state)
                print(f"✓ Validated: {fname}")
                break

            elif action == "r":
                state[fname] = {
                    "status": "rejected",
                    "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "reasons": analysis["errors"] + analysis["warnings"],
                }
                save_judgment_state(state)
                print(f"✗ Rejected: {fname}")
                break

            elif action == "s":
                state[fname] = {
                    "status": "needs_review",
                    "judged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                save_judgment_state(state)
                print("⏭️ Skipped (marked for later review)")
                break

            else:
                print("Invalid choice. Try v, r, or s.")


def show_summary():
    """Show statistics on all traces and judgment state."""
    state = load_judgment_state()
    sim_files = get_all_sim_traces()

    total = len(sim_files)
    statuses = defaultdict(int)
    for fname in sim_files:
        if fname in state:
            status = state[fname].get("status", "unknown")
            statuses[status] += 1
        else:
            statuses["unjudged"] += 1

    print(f"{'='*50}")
    print(f"TRACE CURATOR — SUMMARY")
    print(f"{'='*50}")
    print(f"Total sim traces: {total}")
    for status, count in sorted(statuses.items()):
        pct = count / total * 100 if total else 0
        print(f"  {status:20s}: {count:3d} ({pct:.0f}%)")

    # Per-category stats (from filenames)
    cat_stats = defaultdict(lambda: {"total": 0, "validated": 0, "rejected": 0})
    for fname in sim_files:
        parts = fname.split("_")
        if len(parts) >= 2:
            cat = parts[1]
            cat_stats[cat]["total"] += 1
            if fname in state:
                s = state[fname].get("status", "")
                if s == "validated":
                    cat_stats[cat]["validated"] += 1
                elif s == "rejected":
                    cat_stats[cat]["rejected"] += 1

    print(f"\n{'='*50}")
    print(f"PER-CATEGORY BREAKDOWN")
    print(f"{'='*50}")
    for cat in sorted(cat_stats.keys()):
        stats = cat_stats[cat]
        total_c = stats["total"]
        val_c = stats["validated"]
        rej_c = stats["rejected"]
        review_c = total_c - val_c - rej_c
        print(f"  {cat:30s}: {total_c:2d} total | ✓{val_c:2d}  ✗{rej_c:2d}  ⏳{review_c:2d}")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        state = load_judgment_state()

        if arg == "--batch":
            validated, rejected, skipped = batch_validate(state)
            print(f"\nDone! Validated: {validated}, Rejected: {rejected}, Needs review: {skipped}")
            show_summary()

        elif arg == "--summary":
            show_summary()

        else:
            print(f"Unknown argument: {arg}")
            print("Usage:")
            print("  python trace_curator.py              # Interactive judgment")
            print("  python trace_curator.py --batch      # Auto-validate clean traces")
            print("  python trace_curator.py --summary    # Show statistics")

    else:
        interactive_loop()


if __name__ == "__main__":
    main()
