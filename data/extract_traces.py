"""Trace Validator & Curator — CLI tool for managing SFT training data.

A comprehensive command-line interface for loading, inspecting, analyzing, and
curating simulated conversation traces into production-ready SFT datasets.

Subcommands:
    list        List available traces with stats
    inspect     Deep inspection of a single trace's turns & content
    analyze     Run quality analysis on one or all traces
    refine      Propose refinements to fix detected issues (dry-run)
    fix         Apply refinements in-place and export validated samples
    judge       Launch interactive judgment wizard (default when no args)

Examples:
    python data/extract_traces.py list --trace-dir ~/.assistant/data/conversations
    python data/extract_traces.py inspect sim_py_collections_20260706_xxx.jsonl
    python data/extract_traces.py analyze --category data_science
    python data/extract_traces.py refine sim_ds_numpy_images_xxx.jsonl
    python data/extract_traces.py fix --status validated --output ./curated/
    python data/extract_traces.py judge  # Interactive wizard

Usage:
    python data/extract_traces.py <subcommand> [options]
"""

import json
import glob
import os
import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone


# ============================================================================
# State persistence — judgment state survives between sessions
# ============================================================================

STATE_FILE = os.path.expanduser("~/.assistant/data/conversations/judgment_state.json")


def load_judgment_state():
    """Load persisted judgment state from disk."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load state file ({e}), starting fresh.", file=sys.stderr)
    return {}


def save_judgment_state(state):
    """Save judgment state to disk."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_trace_status(filepath, state):
    """Get judgment status for a trace from persisted state."""
    basename = os.path.basename(filepath)
    entry = state.get(basename, {})
    return entry.get("status", "pending")


def update_trace_state(state, filepath, updates):
    """Update judgment state for a single trace."""
    basename = os.path.basename(filepath)
    if basename not in state:
        state[basename] = {}
    state[basename].update(updates)
    save_judgment_state(state)


# ============================================================================
# Data model — one "sample" = one complete conversation trace
# ============================================================================

def _infer_category(filename: str) -> str:
    """Infer scenario category from filename prefix."""
    name = os.path.basename(filename)
    cat_map = {
        "ds_": "data_science",
        "conv_": "natural_conversation",
        "dbg_": "debugging",
        "git_": "git_workflow",
        "fm_": "file_management",
        "sysmon_": "system_monitoring",
        "py_": "python_scripting",
        "web_": "web_research",
        "build_": "build_test",
        "env_": "env_shell",
    }
    for prefix, cat in cat_map.items():
        if name.startswith(f"sim_{prefix}") or name.startswith(prefix):
            return cat
    return "unknown"


def _infer_scenario_name(filename: str) -> str:
    """Extract scenario name from sim_<name>_timestamp_suffix.jsonl."""
    base = os.path.basename(filename).replace(".jsonl", "")
    parts = base.split("_")
    if len(parts) >= 3:
        return "_".join(parts[1:-2])
    return base


def _extract_turns_from_messages(messages):
    """Parse a flat messages list into Turn objects.

    Handles the case where the LLM emits 2 assistant msgs per turn:
      - Assistant #1: tool_calls present, content empty/whitespace-only
      - Tool result(s)
      - Assistant #2: no tool_calls, text response (the "explains" msg)
    These are merged into a single Turn with the text appended to assistant_content.

    Also handles cases where the LLM puts BOTH tool_calls and explanatory text
    in a single assistant message — that's already handled correctly by the
    existing logic.
    """
    from dataclasses import dataclass, field

    @dataclass
    class Turn:
        user_content: str = ""
        assistant_content: str = ""
        tool_calls: list[dict] = field(default_factory=list)
        tool_results: list[str] = field(default_factory=list)

        def has_xonsh(self):
            for tc in self.tool_calls:
                fn = tc.get("function", {}).get("name", "")
                if fn == "xonsh":
                    return True
            return False

    turns = []
    current = Turn()

    for m in messages:
        role = m.get("role", "")

        if role == "system":
            continue  # Skip system prompt — we use our own template

        elif role == "user":
            # New user message → flush the previous turn and start a new one
            if current.user_content or current.tool_calls:
                turns.append(current)
            current = Turn(user_content=m.get("content", ""))

        elif role == "assistant":
            tc_raw = m.get("tool_calls", [])
            has_tools = bool(tc_raw)

            # Case 1: First assistant message in this logical turn — collect tools + text
            if not current.tool_calls and not current.tool_results:
                current.assistant_content = m.get("content", "") or ""
                for tc in tc_raw:
                    normalized = {}
                    if isinstance(tc, dict):
                        normalized = tc
                    else:
                        # OpenAI Python SDK object
                        normalized = {
                            "id": getattr(tc, "id", ""),
                            "type": getattr(tc, "type", "function"),
                            "function": {
                                "name": getattr(tc.function, "name", "") if hasattr(tc, "function") else "",
                                "arguments": getattr(tc.function, "arguments", "{}") if hasattr(tc, "function") else "{}",
                            },
                        }
                    current.tool_calls.append(normalized)

            # Case 2: Assistant message AFTER tool results — this is the explanatory
            # text that the model emits as a second assistant msg (no tool calls).
            # Merge it into the current turn's assistant_content.
            elif current.tool_results and not has_tools:
                extra_text = m.get("content", "") or ""
                if extra_text.strip():
                    if current.assistant_content.strip():
                        current.assistant_content += "\n\n" + extra_text.strip()
                    else:
                        current.assistant_content = extra_text

            # Case 3: Assistant message with tool_calls but we already have tool results —
            # the model put both tools AND explanatory text in one message. Merge them.
            elif has_tools and current.tool_results:
                extra_text = m.get("content", "") or ""
                if extra_text.strip():
                    if current.assistant_content.strip():
                        current.assistant_content += "\n\n" + extra_text.strip()
                    else:
                        current.assistant_content = extra_text
                # Keep the tool_calls (they're already in current from a previous msg)

        elif role == "tool":
            current.tool_results.append(m.get("content", ""))

    # Don't forget last turn
    if current.user_content or current.tool_calls:
        turns.append(current)

    # Inject explanatory text for turns that have tool calls but no assistant content
    # (the simulator often emits empty assistant messages after tool calls)
    for turn in turns:
        if turn.tool_calls and not turn.assistant_content.strip():
            explanations = []
            for r in turn.tool_results:
                r_str = str(r).strip()
                if len(r_str) > 500:
                    r_str = r_str[:497] + "..."
                explanations.append(f"[Tool output: {r_str}]")

            tc_names = [tc.get('function', {}).get('name', 'unknown') for tc in turn.tool_calls]
            if explanations:
                result_line = "\n".join(explanations)
                turn.assistant_content = f"Executed {' and '.join(tc_names)}.\n{result_line}"
            else:
                turn.assistant_content = f"[Tool output generated by {tc_names[0]}]"

    return turns


def _load_single_trace(filepath, category_filter=None):
    """Load a single trace file into TraceSample."""
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        if not lines:
            return None

        record = json.loads(lines[-1])
        messages = record.get("request_args", {}).get("messages", [])
        turns = _extract_turns_from_messages(messages)

        has_real_content = False
        for t in turns:
            content = (t.user_content + t.assistant_content).lower()
            if "error" not in content and len(content.strip()) > 10:
                has_real_content = True
                break

        if not has_real_content:
            return None

        cat = _infer_category(filepath)
        if category_filter and cat != category_filter:
            return None

        from dataclasses import dataclass, field

        @dataclass
        class Turn:
            user_content: str = ""
            assistant_content: str = ""
            tool_calls: list[dict] = field(default_factory=list)
            tool_results: list[str] = field(default_factory=list)

            def has_xonsh(self):
                for tc in self.tool_calls:
                    fn = tc.get("function", {}).get("name", "")
                    if fn == "xonsh":
                        return True
                return False

        @dataclass
        class TraceSample:
            source_file: str = ""
            scenario_name: str = ""
            category: str = ""
            system_prompt: str = ""
            turns: list[Turn] = field(default_factory=list)
            status: str = "pending"

            @property
            def has_xonsh_turns(self):
                return any(t.has_xonsh() for t in self.turns)

            @property
            def total_tool_calls(self):
                return sum(len(t.tool_calls) for t in self.turns)

        sample = TraceSample(
            source_file=os.path.basename(filepath),
            scenario_name=_infer_scenario_name(filepath),
            category=cat,
            system_prompt="",
            turns=turns,
            status="pending",
        )
        return sample

    except (json.JSONDecodeError, IOError, IndexError) as e:
        print(f"  Error loading {filepath}: {e}", file=sys.stderr)
        return None


def _load_traces_from_dir(trace_dir, category_filter=None):
    """Load all sim_*.jsonl and conv_*.jsonl traces from directory."""
    pattern = os.path.join(trace_dir, "*.jsonl")
    files = sorted(glob.glob(pattern))

    samples = []
    errors = 0

    for fpath in files:
        sample = _load_single_trace(fpath, category_filter)
        if sample is not None:
            samples.append(sample)
        else:
            errors += 1

    return samples, errors


# ============================================================================
# Quality analyzer (reuses logic from trace_analyzer.py)
# ============================================================================

def _analyze_sample_quality(sample):
    """Run quality analysis on a single sample. Returns dict with score and issues."""
    gaps = []
    total_tool_calls = sum(len(t.tool_calls) for t in sample.turns)
    total_results = sum(len(t.tool_results) for t in sample.turns)

    # Check for API errors
    for turn in sample.turns:
        if "(error: LLM API call failed" in str(turn.user_content):
            gaps.append({"turn": 0, "severity": "critical", "type": "api_error"})
        if "(error: LLM API call failed" in str(turn.assistant_content):
            gaps.append({"turn": 0, "severity": "critical", "type": "api_error"})

    # Check tool result quality
    error_results = sum(
        1 for t in sample.turns
        for r in t.tool_results
        if "Exception" in str(r) or "Error" in str(r) or "Traceback" in str(r)
    )

    if total_results > 0:
        error_ratio = error_results / total_results
        if error_ratio > 0.5:
            gaps.append({
                "turn": -1, "severity": "critical", "type": "tool_errors",
                "detail": f"{error_ratio:.0%} tool errors ({error_results}/{total_results})"
            })

    # Check for corrupted user prompts
    assistant_phrases = ["voici", "bien sûr", "excellente", "merci pour", "c'est une"]
    for turn in sample.turns:
        content_lower = turn.user_content.lower().strip()
        if any(content_lower.startswith(phrase) for phrase in assistant_phrases):
            gaps.append({"turn": 0, "severity": "critical", "type": "corrupted_prompt"})

    # Check minimum length
    real_turns = sum(1 for t in sample.turns if t.user_content.strip() and len(t.user_content.strip()) > 5)
    if real_turns < 2:
        gaps.append({"turn": 0, "severity": "warning", "type": "too_short"})

    # Compute score (start at 1.0, deduct per gap)
    score = 1.0
    for g in gaps:
        if g["severity"] == "critical":
            score -= 0.25
        elif g["severity"] == "warning":
            score -= 0.1

    return {
        "score": max(0.0, round(score, 3)),
        "gaps": gaps,
        "num_turns": len(sample.turns),
        "num_tool_calls": total_tool_calls,
        "has_xonsh": sample.has_xonsh_turns,
    }


# ============================================================================
# Refinement logic (clean corrupted prompts, filter error results)
# ============================================================================

def _apply_refinements(sample):
    """Apply quality refinements to a sample in-place. Returns list of changes."""
    changes = []

    # Clean corrupted user prompts
    for turn in sample.turns:
        lines = turn.user_content.strip().split("\n")
        if not lines:
            continue

        first = lines[0].strip()
        assistant_phrases = ["voici", "bien sûr", "excellente", "merci pour", "c'est une"]

        was_corrupted = False
        for phrase in assistant_phrases:
            if turn.user_content.lower().startswith(phrase):
                # Keep only the first line (actual user request)
                if len(first) < 200 and ("`" in first or "?" in first):
                    turn.user_content = first
                    changes.append(f"Cleaned corrupted prompt in {sample.scenario_name}")
                    was_corrupted = True
                    break

        # Fix assistant content that contains raw xonsh code instead of explanation:
        if turn.tool_calls and turn.assistant_content.strip():
            content = turn.assistant_content.strip()
            code_indicators = [
                "import ", "from ", "open(", "print(", "def ", "@", "\nclass ",
                "__init__", "self.", "np.", "pd.", "df."
            ]
            if any(content.startswith(kw) for kw in code_indicators):
                turn.assistant_content = "[Tool output generated successfully]"
                changes.append(f"Replaced raw xonsh code in assistant_content for {sample.scenario_name}")

        # Filter error tool results and deduplicate (keep only successful ones)
        if turn.tool_results:
            clean_results = []
            for r in turn.tool_results:
                if "Exception" in str(r) or "Traceback" in str(r):
                    continue

                r_str = str(r).strip()

                is_dup = False
                for cr in clean_results:
                    cr_str = str(cr)
                    if r_str in cr_str or cr_str in r_str:
                        is_dup = True
                        break

                if not is_dup:
                    clean_results.append(r)

            if len(clean_results) != len(turn.tool_results):
                changes.append(f"Filtered {len(turn.tool_results) - len(clean_results)} error/duplicate results")
                turn.tool_results = clean_results

    return changes


# ============================================================================
# Subcommand implementations
# ============================================================================

def _wrap_text(text, width=80):
    """Simple word-wrap for terminal display."""
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > width:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " " + word
            else:
                current_line = word

    if current_line:
        lines.append(current_line)

    return lines or [""]


def cmd_list(args):
    """List available traces with summary stats."""
    trace_dir = os.path.expanduser(args.trace_dir or "~/.assistant/data/conversations")
    output_dir = os.path.expanduser(args.output or "./data/output/")

    samples, errors = _load_traces_from_dir(trace_dir, args.category)

    print(f"Trace directory: {trace_dir}", file=sys.stderr)
    print(f"Loaded: {len(samples)} traces (skipped {errors} errors)", file=sys.stderr)

    if not samples:
        print("No valid traces found.", file=sys.stderr)
        return

    # Category breakdown
    cats = {}
    for s in samples:
        cats[s.category] = cats.get(s.category, 0) + 1

    print("\nBy category:", file=sys.stderr)
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}", file=sys.stderr)

    # Summary stats
    total_turns = sum(len(s.turns) for s in samples)
    xonsh_count = sum(1 for s in samples if s.has_xonsh_turns)
    total_tc = sum(s.total_tool_calls for s in samples)

    print(f"\nTotal turns: {total_turns}", file=sys.stderr)
    print(f"Traces with xonsh code: {xonsh_count}/{len(samples)}", file=sys.stderr)
    print(f"Total tool calls: {total_tc}", file=sys.stderr)


def cmd_inspect(args):
    """Deep inspection of a single trace."""
    trace_file = args.trace_file

    if not os.path.isabs(trace_file):
        if not os.path.exists(trace_file):
            trace_dir = os.path.expanduser(args.trace_dir or "~/.assistant/data/conversations")
            trace_file = os.path.join(trace_dir, trace_file)

    sample = _load_single_trace(trace_file, args.category)
    if sample is None:
        print(f"Error: Could not load trace '{args.trace_file}'", file=sys.stderr)
        return

    print("=" * 70, file=sys.stderr)
    print(f"SCENARIO: {sample.scenario_name}", file=sys.stderr)
    print(f"CATEGORY: {sample.category}", file=sys.stderr)
    print(f"SOURCE:   {sample.source_file}", file=sys.stderr)
    print(f"STATUS:   {sample.status.upper()}", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    quality = _analyze_sample_quality(sample)
    print(
        f"\nTurns: {quality['num_turns']} | Tool calls: {quality['num_tool_calls']} | "
        f"Has xonsh: {quality['has_xonsh']} | Score: {quality['score']:.1%}",
        file=sys.stderr,
    )

    for ti, turn in enumerate(sample.turns):
        print(f"\n--- TURN {ti + 1}/{len(sample.turns)} ---", file=sys.stderr)

        if turn.user_content.strip():
            print("\n[USER]", file=sys.stderr)
            for chunk in _wrap_text(turn.user_content, 80):
                print(f"  {chunk}", file=sys.stderr)

        if turn.assistant_content and turn.assistant_content.strip():
            print("\n[ASSISTANT]", file=sys.stderr)
            for chunk in _wrap_text(turn.assistant_content[:500], 80):
                print(f"  {chunk}", file=sys.stderr)

        if turn.tool_calls:
            xonsh_codes = []
            for tc in turn.tool_calls:
                fn_name = tc.get("function", {}).get("name", "")
                args_str = tc.get("function", {}).get("arguments", "{}")
                try:
                    args_obj = json.loads(args_str) if isinstance(args_str, str) else args_str
                    code = args_obj.get("code", "").strip()
                    if code:
                        xonsh_codes.append(code)
                except (json.JSONDecodeError, TypeError):
                    pass

            for ci, code in enumerate(xonsh_codes):
                label = f"XONSH CODE #{ci + 1}:" if len(xonsh_codes) > 1 else "XONSH CODE:"
                print(f"\n[{label}]", file=sys.stderr)
                for chunk in _wrap_text(code[:600], 80):
                    print(f"  {chunk}", file=sys.stderr)

        if turn.tool_results:
            for ri, result in enumerate(turn.tool_results):
                label = f"EXECUTION RESULT #{ri + 1}:" if len(turn.tool_results) > 1 else "EXECUTION RESULT:"
                print(f"\n[{label}]", file=sys.stderr)
                for chunk in _wrap_text(result[:800], 80):
                    print(f"  {chunk}", file=sys.stderr)

    # Quality summary
    if quality["gaps"]:
        print("\n" + "=" * 70, file=sys.stderr)
        print("QUALITY ISSUES:", file=sys.stderr)
        for g in quality["gaps"]:
            sev = "CRITICAL" if g["severity"] == "critical" else "WARNING"
            detail = f" — {g['detail']}" if "detail" in g else ""
            print(f"  [{sev}] {g['type']} (turn {g.get('turn', '?')}){detail}", file=sys.stderr)


def cmd_analyze(args):
    """Run quality analysis on all traces."""
    trace_dir = os.path.expanduser(args.trace_dir or "~/.assistant/data/conversations")
    output_dir = os.path.expanduser(args.output or "./data/output/")

    samples, errors = _load_traces_from_dir(trace_dir, args.category)

    results = []
    for s in samples:
        quality = _analyze_sample_quality(s)
        results.append((s, quality))

    print(f"Analyzed {len(results)} traces:", file=sys.stderr)
    print("-" * 70, file=sys.stderr)

    results.sort(key=lambda x: x[1]["score"])

    for sample, quality in results:
        score = quality["score"]
        bar_len = int(score * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        issue_summary = ""
        if quality["gaps"]:
            types = set(g["type"] for g in quality["gaps"])
            issue_summary = f" | issues: {', '.join(types)}"

        print(
            f"[{bar}] {sample.scenario_name:<40} {score:.1%}{issue_summary}",
            file=sys.stderr,
        )

    if args.output:
        os.makedirs(output_dir, exist_ok=True)
        analysis_path = os.path.join(output_dir, "analysis.jsonl")
        with open(analysis_path, "w", encoding="utf-8") as f:
            for sample, quality in results:
                entry = {
                    "scenario": sample.scenario_name,
                    "category": sample.category,
                    "source_file": sample.source_file,
                    "score": quality["score"],
                    "num_turns": quality["num_turns"],
                    "num_tool_calls": quality["num_tool_calls"],
                    "gaps": quality["gaps"],
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"\nAnalysis saved to {analysis_path}", file=sys.stderr)


def cmd_refine(args):
    """Propose and apply refinements to fix issues."""
    trace_dir = os.path.expanduser(args.trace_dir or "~/.assistant/data/conversations")
    output_dir = os.path.expanduser(args.output or "./data/output/")

    samples, errors = _load_traces_from_dir(trace_dir, args.category)

    if not samples:
        print("No traces to refine.", file=sys.stderr)
        return

    applied_count = 0
    total_changes = 0
    for sample in samples:
        changes = _apply_refinements(sample)
        if changes:
            applied_count += 1
            total_changes += len(changes)
            print(
                f"Applied {len(changes)} change(s) to '{sample.scenario_name}':",
                file=sys.stderr,
            )
            for change in changes[:5]:
                print(f"  - {change}", file=sys.stderr)

    print(
        f"\nRefined {applied_count}/{len(samples)} traces ({total_changes} total changes)",
        file=sys.stderr,
    )


def cmd_fix(args):
    """Apply refinements AND export validated samples to JSONL."""
    trace_dir = os.path.expanduser(args.trace_dir or "~/.assistant/data/conversations")
    output_dir = os.path.expanduser(args.output or "./data/output/")

    samples, errors = _load_traces_from_dir(trace_dir, args.category)

    if not samples:
        print("No valid traces found.", file=sys.stderr)
        return

    results = []
    for s in samples:
        quality = _analyze_sample_quality(s)
        results.append((s, quality))

    good_count = sum(1 for _, q in results if q["score"] >= 0.75)
    warn_count = sum(1 for _, q in results if 0.5 <= q["score"] < 0.75)
    bad_count = sum(1 for _, q in results if q["score"] < 0.5)

    print(f"Quality distribution: {good_count} good, {warn_count} warnings, {bad_count} critical", file=sys.stderr)

    refined_samples = []
    for sample, quality in results:
        changes = _apply_refinements(sample)
        if quality["score"] >= 0.5 and not any(
            g["type"] == "corrupted_prompt" for g in quality["gaps"]
        ):
            refined_samples.append(sample)

    print(f"\nRefined {len(refined_samples)} samples (>=0.5 score, no corrupted prompts)", file=sys.stderr)

    os.makedirs(output_dir, exist_ok=True)

    from trace_writer import build_system_prompt as SYSTEM_PROMPT

    exported = 0
    export_path = os.path.join(output_dir, f"{args.status}.jsonl")

    for sample in refined_samples:
        def clean_prompt(content):
            lines = content.strip().split("\n")
            if not lines:
                return ""
            first = lines[0].strip()
            assistant_phrases = ["voici", "bien sûr", "excellente", "merci pour"]
            content_lower = content.lower().strip()
            if any(content_lower.startswith(p) for p in assistant_phrases):
                result_lines = []
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if not stripped and i > 0:
                        break
                    result_lines.append(line)
                return "\n".join(result_lines).strip()
            return content.strip()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for turn in sample.turns:
            cleaned_user = clean_prompt(turn.user_content)
            if cleaned_user.strip():
                messages.append({"role": "user", "content": cleaned_user})

            assistant_msg = {"role": "assistant"}
            if turn.assistant_content and turn.assistant_content.strip():
                assistant_msg["content"] = turn.assistant_content
            else:
                assistant_msg["content"] = None

            if turn.tool_calls:
                assistant_msg["tool_calls"] = turn.tool_calls
            messages.append(assistant_msg)

            for idx, result in enumerate(turn.tool_results):
                tool_msg = {"role": "tool", "content": result}
                if idx < len(turn.tool_calls):
                    tc_id = turn.tool_calls[idx].get("id", "")
                    if tc_id:
                        tool_msg["tool_call_id"] = tc_id
                messages.append(tool_msg)

        sft_sample = {
            "messages": messages,
            "metadata": {
                "source_file": sample.source_file,
                "scenario_name": sample.scenario_name,
                "category": sample.category,
                "num_turns": len(sample.turns),
                "has_xonsh": sample.has_xonsh_turns,
                "total_tool_calls": sample.total_tool_calls,
            },
        }

        with open(export_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(sft_sample, ensure_ascii=False) + "\n")
            exported += 1

    print(f"Exported {exported} samples to {export_path}", file=sys.stderr)


# ============================================================================
# Interactive Judgment Wizard — field-by-field validation with action menu
# ============================================================================

def cmd_judge(args):
    """Launch interactive judgment wizard.

    Phase 1: Build raw index of ALL traces (sim + conv)
    Phase 2: Build reconstructed compact index, filter pending only
    Phase 3: Field-by-field judgment loop with action execution & confirmation
    """
    trace_dir = os.path.expanduser(args.trace_dir or "~/.assistant/data/conversations")
    output_dir = os.path.expanduser(args.output or "./data/output/")

    # Load persisted state
    state = load_judgment_state()

    print("=" * 70, file=sys.stderr)
    print(" TRACE JUDGMENT WIZARD", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"Trace directory: {trace_dir}", file=sys.stderr)
    print(file=sys.stderr)

    # ── Phase 1: Build Raw Index ────────────────────────────────────────
    print("Phase 1: Building raw index...", file=sys.stderr)
    all_samples, errors = _load_traces_from_dir(trace_dir, args.category)

    if not all_samples:
        print("No valid traces found. Nothing to judge.", file=sys.stderr)
        return

    # Annotate with persisted status and quality scores
    for sample in all_samples:
        sample.status = get_trace_status(sample.source_file, state)
        quality = _analyze_sample_quality(sample)
        sample._quality = quality  # Attach quality to sample

    raw_index_stats = {
        "total": len(all_samples),
        "pending": sum(1 for s in all_samples if s.status == "pending"),
        "validated": sum(1 for s in all_samples if s.status == "validated"),
        "refused": sum(1 for s in all_samples if s.status == "refused"),
    }

    print(f"  Total traces: {raw_index_stats['total']}", file=sys.stderr)
    print(f"  Pending:      {raw_index_stats['pending']}", file=sys.stderr)
    print(f"  Validated:    {raw_index_stats['validated']}", file=sys.stderr)
    print(f"  Refused:      {raw_index_stats['refused']}", file=sys.stderr)
    print(file=sys.stderr)

    # ── Phase 2: Build Reconstructed Index (Working Set = pending only) ─
    print("Phase 2: Building reconstructed index (pending only)...", file=sys.stderr)
    working_set = [s for s in all_samples if s.status == "pending"]

    # Sort by quality score ascending (worst first — tackle hard cases early)
    working_set.sort(key=lambda s: s._quality["score"])

    print(f"  Working set: {len(working_set)} traces to judge", file=sys.stderr)
    print(file=sys.stderr)

    if not working_set:
        print("No pending traces. All traces have been judged!", file=sys.stderr)
        return

    # ── Phase 3: Interactive Judgment Loop ──────────────────────────────
    print("Phase 3: Starting field-by-field judgment...", file=sys.stderr)
    print("-" * 70, file=sys.stderr)

    for trace_idx, sample in enumerate(working_set):
        _judge_trace(sample, state, output_dir, trace_idx + 1, len(working_set))


def _judge_trace(sample, state, output_dir, current_num, total_num):
    """Judge a single trace field-by-field with action menu."""
    quality = sample._quality

    print(f"\n{'='*70}", file=sys.stderr)
    print(f" TRACE {current_num}/{total_num}: {sample.scenario_name}", file=sys.stderr)
    print(f" Category: {sample.category} | Score: {quality['score']:.1%}", file=sys.stderr)

    if quality["gaps"]:
        for g in quality["gaps"]:
            sev = "CRITICAL" if g["severity"] == "critical" else "WARNING"
            detail = f" — {g['detail']}" if "detail" in g else ""
            print(f"  [{sev}] {g['type']} (turn {g.get('turn', '?')}){detail}", file=sys.stderr)

    print(f"{'='*70}", file=sys.stderr)

    # Iterate through each turn and its fields
    for turn_idx, turn in enumerate(sample.turns):
        _judge_turn_fields(sample, turn, turn_idx, state)

    # After all turns — ask final verdict on the trace
    print(f"\n--- Final verdict for '{sample.scenario_name}' ---", file=sys.stderr)
    print("  [V] Validate entire trace", file=sys.stderr)
    print("  [R] Refuse entire trace", file=sys.stderr)
    print("  [S] Skip (mark as pending)", file=sys.stderr)

    try:
        choice = input("\nYour choice: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nInterrupted — saving state...", file=sys.stderr)
        return

    if choice == "v":
        sample.status = "validated"
        update_trace_state(state, sample.source_file, {
            "status": "validated",
            "judged_at": datetime.now(timezone.utc).isoformat(),
            "quality_score": quality["score"],
        })
        print("  ✓ Trace VALIDATED", file=sys.stderr)
    elif choice == "r":
        sample.status = "refused"
        update_trace_state(state, sample.source_file, {
            "status": "refused",
            "judged_at": datetime.now(timezone.utc).isoformat(),
            "quality_score": quality["score"],
        })
        print("  ✗ Trace REFUSED", file=sys.stderr)
    else:
        print("  ⊘ Trace SKIPPED (remains pending)", file=sys.stderr)


def _judge_turn_fields(sample, turn, turn_idx, state):
    """Judge each field in a turn with action menu."""
    fields = [
        ("USER PROMPT", turn.user_content),
        ("ASSISTANT RESPONSE", turn.assistant_content[:1000]),  # Truncate long responses
    ]

    if turn.tool_calls:
        for tc_idx, tc in enumerate(turn.tool_calls):
            fn_name = tc.get("function", {}).get("name", "unknown")
            args_str = tc.get("function", {}).get("arguments", "{}")
            fields.append((f"TOOL CALL #{tc_idx+1} ({fn_name})", args_str))

    if turn.tool_results:
        for tr_idx, result in enumerate(turn.tool_results):
            fields.append((f"EXECUTION RESULT #{tr_idx+1}", result[:800]))

    for field_name, field_content in fields:
        print(f"\n--- Turn {turn_idx + 1}/{len(sample.turns)} — {field_name} ---", file=sys.stderr)

        # Display content (wrapped)
        display_text = field_content if field_content else "(empty)"
        for line in _wrap_text(display_text[:600], 78):
            print(f"  {line}", file=sys.stderr)

        # Action menu
        print("\nActions:", file=sys.stderr)
        print("  [V] Validate this field", file=sys.stderr)
        print("  [E] Edit content (opens editor)", file=sys.stderr)
        print("  [D] Delegate to subagent for improvement", file=sys.stderr)
        print("  [S] Skip (review later)", file=sys.stderr)

        try:
            choice = input("\nYour action: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nInterrupted — saving state...", file=sys.stderr)
            return

        if choice == "v":
            print("  ✓ Field validated", file=sys.stderr)

        elif choice == "e":
            # Open editor for manual edit
            import tempfile
            import subprocess

            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
                tf.write(field_content)
                tmp_path = tf.name

            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, tmp_path])

            with open(tmp_path, "r", encoding="utf-8") as tf:
                new_content = tf.read()

            os.unlink(tmp_path)

            # Show diff summary
            old_len = len(field_content)
            new_len = len(new_content)
            print(f"\n  Content changed: {old_len} → {new_len} chars", file=sys.stderr)

            # Confirmation
            try:
                confirm = input("  Apply changes? [Y/n]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                confirm = "y"

            if confirm != "n":
                # Update the field in place
                if "USER PROMPT" in field_name:
                    turn.user_content = new_content
                elif "ASSISTANT RESPONSE" in field_name:
                    turn.assistant_content = new_content
                print("  ✓ Changes applied", file=sys.stderr)
            else:
                print("  ⊘ Changes discarded", file=sys.stderr)

        elif choice == "d":
            # Delegate to subagent — this is a placeholder for when running in Hermes context
            print("\n  ⚠ Subagent delegation requires Hermes agent context.", file=sys.stderr)
            print("  In CLI mode, use 'python data/extract_traces.py refine' instead.", file=sys.stderr)

        else:
            print("  ⊘ Field skipped", file=sys.stderr)


# ============================================================================
# Main entry point — CLI argument parser with subcommands
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Trace Validator & Curator — manage SFT training data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                                          # List all traces
  %(prog)s inspect sim_py_collections_20260706_xxx.jsonl  # Inspect one trace
  %(prog)s analyze --category data_science              # Analyze by category
  %(prog)s refine                                       # Apply refinements to all
  %(prog)s fix --status validated                       # Fix + export validated samples
  %(prog)s judge                                        # Interactive judgment wizard
        """,
    )

    parser.add_argument(
        "--trace-dir", "-t",
        type=str,
        default=os.path.expanduser("~/.assistant/data/conversations"),
        help="Path to trace files directory (default: ~/.assistant/data/conversations)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./data/output/",
        help="Output directory for JSONL files (default: ./data/output/)",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

    # list subcommand
    list_parser = subparsers.add_parser("list", help="List available traces with stats")
    list_parser.add_argument(
        "--category", "-c", type=str, default=None, choices=[
            "data_science", "natural_conversation", "debugging",
            "git_workflow", "file_management", "system_monitoring",
            "python_scripting", "web_research", "build_test", "env_shell",
        ], help="Only load traces from this category")

    # inspect subcommand
    inspect_parser = subparsers.add_parser("inspect", help="Deep inspection of a trace")
    inspect_parser.add_argument("trace_file", help="Trace filename to inspect")
    inspect_parser.add_argument(
        "--category", "-c", type=str, default=None, choices=[
            "data_science", "natural_conversation", "debugging",
            "git_workflow", "file_management", "system_monitoring",
            "python_scripting", "web_research", "build_test", "env_shell",
        ], help="Only load traces from this category")

    # analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Run quality analysis on all traces")
    analyze_parser.add_argument(
        "--category", "-c", type=str, default=None, choices=[
            "data_science", "natural_conversation", "debugging",
            "git_workflow", "file_management", "system_monitoring",
            "python_scripting", "web_research", "build_test", "env_shell",
        ], help="Only load traces from this category")

    # refine subcommand
    refine_parser = subparsers.add_parser("refine", help="Apply quality refinements to all traces")
    refine_parser.add_argument(
        "--category", "-c", type=str, default=None, choices=[
            "data_science", "natural_conversation", "debugging",
            "git_workflow", "file_management", "system_monitoring",
            "python_scripting", "web_research", "build_test", "env_shell",
        ], help="Only load traces from this category")

    # fix subcommand (refine + export)
    fix_parser = subparsers.add_parser("fix", help="Apply refinements and export to JSONL")
    fix_parser.add_argument(
        "--status", "-s", choices=["validated"], default="validated",
        help="Which status group to export (default: validated)")
    fix_parser.add_argument(
        "--category", "-c", type=str, default=None, choices=[
            "data_science", "natural_conversation", "debugging",
            "git_workflow", "file_management", "system_monitoring",
            "python_scripting", "web_research", "build_test", "env_shell",
        ], help="Only load traces from this category")
    fix_parser.add_argument(
        "--output", "-o", type=str, default="./data/output/",
        help="Output directory for JSONL files (default: ./data/output/)")

    # judge subcommand — interactive wizard
    judge_parser = subparsers.add_parser("judge", help="Launch interactive judgment wizard")
    judge_parser.add_argument(
        "--category", "-c", type=str, default=None, choices=[
            "data_science", "natural_conversation", "debugging",
            "git_workflow", "file_management", "system_monitoring",
            "python_scripting", "web_research", "build_test", "env_shell",
        ], help="Only judge traces from this category")

    args = parser.parse_args()

    # Default to judge wizard when no subcommand provided
    if not args.subcommand:
        print("No subcommand specified — launching interactive judgment wizard.", file=sys.stderr)
        args.subcommand = "judge"

    # Route to subcommand handler
    handlers = {
        "list": cmd_list,
        "inspect": cmd_inspect,
        "analyze": cmd_analyze,
        "refine": cmd_refine,
        "fix": cmd_fix,
        "judge": cmd_judge,
    }

    handler = handlers.get(args.subcommand)
    if handler:
        try:
            handler(args)
        except KeyboardInterrupt:
            print("\n\nInterrupted — judgment state saved.", file=sys.stderr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
