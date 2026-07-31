#!/usr/bin/env python3
"""Verify OneOS simulation traces against eval criteria T0–T6.

Usage:
    python3 evals/verify_trace.py <trace.jsonl> [--verbose]
    python3 evals/verify_trace.py <dir/> [--verbose]
"""
import json, sys, os, re
from pathlib import Path

# ── temporal/locale marker regexes ──────────────────────────────────────────
TIME_PATTERNS = [
    r'\b\d{1,2}[:h]\d{2}\b',       # 23:59, 14h30
    r'\b(AM|PM)\b', r'\b(am|pm)\b',
    r'\b(matin|soir|nuit|aprè[ms]|midi|afternoon|evening|morning|night)\b',
    r'\b(aujourd\'hui|today|ce soir|tonight|ce matin)\b',
    r'\b\d{1,2}\s*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b',
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b',
    r'\b(202[4-9]|203[0-9])\b',
    r'\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b',
    r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
    r'\b(heure|heureux|minute)\s+(locale|actuelle|courante)\b',
    r'\bfuseau\b', r'\b(timezone|UTC|[+-]\d{2}:\d{2})\b',
]
LOCALE_PATTERNS = [
    r'\b(Suisse|France|Belgique|Canada|france|suisse)\b',
    r'\b(langue|lang|locale|LANG|LC_)\b',
    r'\b(français|anglais|allemand|fran[cç]ais|english|french)\b',
    r'\b(Europe/Paris|Europe/Zurich|Europe/London|America/New_York)\b',
    r'\b(vaud|lausanne|genève|zurich|berne)\b',
]
SYSTEM_PATTERNS = [
    r'\b(hostname|machine|hôte|[Hh]ost)\b',
    r'\b(Linux|Windows|macOS|Darwin)\b',
    r'\b(xonsh|shell|REPL|repl)\b',
    r'\b(OS|operating system|système)\b',
    r'\b(kernel|noyau)\b',
    r'\b(arch|x86_64|amd64|aarch64)\b',
    r'\b(mémoire|memory|RAM|disque|disk)\b',
    r'\b(processeur|cpu|processor|GPU|gpu)\b',
    r'\b(environnement|environment|env)\b',
    r'\b(Destiny|TITAN|RTX|Threadripper)\b',
]

def count_markers(text: str, patterns: list) -> list:
    return [p for p in patterns if re.search(p, text, re.IGNORECASE)]

def normalize_trace(trace: dict) -> tuple:
    """Normalize trace to standard format with messages and metadata."""
    # Simulator format: {"request_args": {"messages": [...]}}
    if "request_args" in trace:
        req = trace.get("request_args", {})
        msgs = req.get("messages", [])
        meta = {"source": "simulator", "scenario_name": "unknown", "category": "unknown"}
        # Extract metadata if available in request_args
        for k in ("category", "scenario_name", "num_turns", "total_tool_calls",
                   "source_file", "model", "temperature", "max_tokens"):
            if k in req and k not in meta:
                meta[k] = req[k]
        return msgs, meta
    # Standard format: {"messages": [...], "metadata": {...}}
    msgs = trace.get("messages", [])
    meta = trace.get("metadata", {})
    return msgs, meta

def verify_trace(trace: dict, verbose: bool = False) -> dict:
    msgs, meta = normalize_trace(trace)
    cat = meta.get("category", "unknown")
    results = {}

    # ── T0: Intro awareness ─────────────────────────────────────────────────
    intro_idx = None
    for i, m in enumerate(msgs):
        if m.get("role") == "user" and ("assistant" in (m.get("content") or "").lower() or m.get("content","").strip() == "Assistant?" or m.get("content","").strip().startswith("Assistant")):
            intro_idx = i
            break
    t0 = {"pass": False, "detail": "", "markers": {}}
    if intro_idx is not None and intro_idx + 1 < len(msgs):
        reply = msgs[intro_idx + 1].get("content") or ""
        time_m = count_markers(reply, TIME_PATTERNS)
        locale_m = count_markers(reply, LOCALE_PATTERNS)
        system_m = count_markers(reply, SYSTEM_PATTERNS)
        t0["markers"] = {"time": len(time_m), "locale": len(locale_m), "system": len(system_m), "total": len(time_m)+len(locale_m)+len(system_m)}
        t0["detail"] = f"intro reply ({len(reply)} chars): {reply[:120]}"
        t0["pass"] = t0["markers"]["total"] >= 2
        if verbose:
            t0["time_markers"] = time_m
            t0["locale_markers"] = locale_m
            t0["system_markers"] = system_m
    else:
        t0["detail"] = "no intro turn found"
    results["T0_intro"] = t0

    # ── T1: Tool choice ────────────────────────────────────────────────────
    tool_calls = []
    tool_names = set()
    has_web_search = False
    has_xonsh = False
    for m in msgs:
        tcs = m.get("tool_calls")
        if tcs:
            for tc in tcs:
                fn = tc.get("function", {}).get("name", "")
                tool_calls.append(fn)
                tool_names.add(fn)
                if fn == "web_search": has_web_search = True
                if fn == "xonsh": has_xonsh = True

    t1 = {"pass": True, "detail": "", "tool_calls": len(tool_calls), "tools_used": sorted(tool_names)}
    # shell tasks should NOT use web_search
    if cat in ("shell", "file_management", "system_monitoring", "git_workflow") and has_web_search:
        t1["pass"] = False
        t1["detail"] = f"web_search used in {cat} task"
    elif has_web_search and has_xonsh:
        t1["detail"] = f"mixed tools ({len(tool_calls)} calls)"
    elif has_xonsh:
        t1["detail"] = f"all xonsh calls ({len(tool_calls)} calls)"
    elif len(tool_calls) == 0:
        t1["detail"] = "no tool calls (task may not need tools)"
    else:
        t1["detail"] = f"no xonsh tool used — tools: {sorted(tool_names)}"
        if cat != "natural_conversation":
            t1["pass"] = False
    results["T1_tool_choice"] = t1

    # ── T2: Syntax execution ────────────────────────────────────────────────
    xonsh_calls = 0; xonsh_errors = 0; xonsh_timeouts = 0
    for m in msgs:
        if m.get("role") == "tool":
            content = str(m.get("content", ""))
            name = m.get("name", "")
            if name == "xonsh" or "xonsh" in name:
                xonsh_calls += 1
                if "(timeout" in content.lower() or "error" in content.lower() or m.get("is_error"):
                    xonsh_errors += 1
                    if "(timeout" in content.lower():
                        xonsh_timeouts += 1
    # also check assistant tool_calls that attempted xonsh
    for m in msgs:
        tcs = m.get("tool_calls")
        if tcs:
            for tc in tcs:
                if tc.get("function", {}).get("name") == "xonsh":
                    xonsh_calls = max(xonsh_calls, 1)

    t2 = {"pass": True, "detail": "", "xonsh_calls": xonsh_calls, "xonsh_errors": xonsh_errors, "xonsh_timeouts": xonsh_timeouts}
    if xonsh_calls > 0:
        success_rate = 1.0 - (xonsh_errors / xonsh_calls) if xonsh_calls > 0 else 1.0
        t2["success_rate"] = round(success_rate, 3)
        if xonsh_timeouts > 0:
            t2["detail"] = f"{xonsh_errors}/{xonsh_calls} errors ({xonsh_timeouts} timeouts)"
        else:
            t2["detail"] = f"{xonsh_errors}/{xonsh_calls} errors"
        if success_rate < 0.5:
            t2["pass"] = False
    else:
        t2["detail"] = "no xonsh calls to evaluate"
        t2["success_rate"] = 1.0
    results["T2_execution"] = t2

    # ── T3: Final response ──────────────────────────────────────────────────
    # Find last assistant message with substantive content after last tool result
    last_tool_idx = -1
    for i in range(len(msgs) - 1, -1, -1):
        if msgs[i].get("role") == "tool":
            last_tool_idx = i
            break
    has_tool_result = last_tool_idx >= 0

    t3 = {"pass": True, "detail": "", "has_tools": has_tool_result, "tool_result_found": False, "final_response_found": False}
    if has_tool_result:
        t3["tool_result_found"] = True
        final_responses = []
        for m in msgs[last_tool_idx + 1:]:
            if m.get("role") == "assistant":
                content = (m.get("content") or "")
                if len(content.strip()) > 5:
                    final_responses.append(content)
        # Also check for messages after the last tool call+result pair
        # Sometimes final response is before tool results in the msg list
        t3["final_responses_count"] = len(final_responses)
        if final_responses:
            t3["final_response_found"] = True
            last = final_responses[-1]
            t3["detail"] = f"response ({len(last)} chars): {last[:100]}"
        else:
            t3["pass"] = False
            t3["detail"] = "no assistant response with >5 chars after tool results"
    else:
        t3["detail"] = "no tool results in trace"
    results["T3_final_response"] = t3

    # ── T4: Format compliance ──────────────────────────────────────────────
    rules = {"passed": 0, "failed": 0, "rules": {}}
    # Rule 1: msg[0] is system
    if len(msgs) > 0 and msgs[0].get("role") == "system":
        rules["passed"] += 1
        rules["rules"]["sys_msg_first"] = True
    else:
        rules["failed"] += 1
        rules["rules"]["sys_msg_first"] = False
    # Rule 2: intro user msg exists (Assistant? or scenario prompt)
    has_user = any(m.get("role") == "user" for m in msgs)
    if has_user:
        rules["passed"] += 1
        rules["rules"]["user_present"] = True
    else:
        rules["failed"] += 1
        rules["rules"]["user_present"] = False
    # Rule 3: tool-call msgs have content="" or None
    tcs_with_content = 0
    total_tcs = 0
    for m in msgs:
        if m.get("tool_calls"):
            total_tcs += 1
            if m.get("content") not in (None, "", {}, "None"):
                tcs_with_content += 1
    if total_tcs == 0:
        rules["passed"] += 1
        rules["rules"]["tool_call_content"] = "no tool calls"
    elif tcs_with_content == 0:
        rules["passed"] += 1
        rules["rules"]["tool_call_content"] = True
    else:
        rules["failed"] += 1
        rules["rules"]["tool_call_content"] = f"{tcs_with_content}/{total_tcs} had content"
    # Rule 4: trace ends on assistant or tool (not tool result on its own)
    if msgs:
        last_role = msgs[-1].get("role")
        if last_role in ("assistant", "tool"):  # tool result is OK, but ideally assistant
            rules["passed"] += 1
        else:
            rules["failed"] += 1
        rules["rules"]["last_role"] = last_role
    else:
        rules["failed"] += 1
        rules["rules"]["last_role"] = "empty"
    # Rule 5: after tool call comes tool result
    tool_follows = True
    for i, m in enumerate(msgs):
        if m.get("tool_calls"):
            tc_ids = [tc.get("id") for tc in m["tool_calls"]]
            next_msgs = msgs[i+1:]
            found = [False] * len(tc_ids)
            for j, tid in enumerate(tc_ids):
                for nm in next_msgs:
                    if nm.get("role") == "tool" and nm.get("tool_call_id") == tid:
                        found[j] = True
                        break
            if not all(found):
                tool_follows = False
                break
    if tool_follows:
        rules["passed"] += 1
        rules["rules"]["tool_call_result"] = True
    else:
        rules["failed"] += 1
        rules["rules"]["tool_call_result"] = False

    total_rules = rules["passed"] + rules["failed"]
    t4 = {"pass": rules["passed"] >= total_rules * 0.8 if total_rules > 0 else True,
          "detail": f"{rules['passed']}/{total_rules} rules passed",
          "rules": rules["rules"]}
    results["T4_format"] = t4

    # ── T5: Anti-loop ──────────────────────────────────────────────────────
    t5 = {"pass": True, "detail": "", "loops_detected": False}
    # Check retry metadata if present
    if "retries" in meta or "total_retries" in meta or "turns_removed" in meta:
        retries = meta.get("total_retries", 0) or meta.get("retries", 0)
        removed = meta.get("turns_removed", 0)
        if retries > 2 or removed > 0:
            t5["pass"] = False
            t5["loops_detected"] = True
            t5["detail"] = f"retries={retries} turns_removed={removed}"
        else:
            t5["detail"] = f"retries={retries} turns_removed={removed}"
    else:
        t5["detail"] = "no retry metadata in trace"
    # Check for same-error pattern in tool results
    if xonsh_errors >= 3:
        t5["pass"] = False
        t5["loops_detected"] = True
        t5["detail"] += f" + {xonsh_errors} xonsh errors"
    results["T5_anti_loop"] = t5

    # ── T6: Token efficiency ───────────────────────────────────────────────
    total_chars = sum(len(m.get("content") or "") for m in msgs)
    est_tokens = total_chars // 4
    tools_used = len([m for m in msgs if m.get("tool_calls") and any(tc for tc in m["tool_calls"])])
    tokens_per_action = est_tokens / (tools_used + 1) if tools_used > 0 else est_tokens

    t6 = {"pass": True, "detail": "",
          "est_tokens": est_tokens, "tool_calls": tools_used,
          "tokens_per_action": round(tokens_per_action, 1),
          "total_chars": total_chars}
    # Flag anomalies: too few (< 300 total) or too many (> 3000 total)
    if est_tokens < 300 and tools_used > 0:
        t6["pass"] = False
        t6["detail"] = f"very low tokens ({est_tokens}) for {tools_used} tool calls"
    elif est_tokens > 3000 and tools_used <= 3:
        t6["pass"] = False
        t6["detail"] = f"very high tokens ({est_tokens}) for only {tools_used} tool calls"
    else:
        t6["detail"] = f"{est_tokens} total → {tokens_per_action:.0f} tok/action"
    results["T6_efficiency"] = t6

    # ── Overall ─────────────────────────────────────────────────────────────
    pass_count = sum(1 for r in results.values() if r.get("pass"))
    total_checks = len(results)
    results["_meta"] = {
        "source": meta.get("source_file", "unknown"),
        "category": cat,
        "scenario": meta.get("scenario_name", "unknown"),
        "turns": meta.get("num_turns", 0),
        "total_tool_calls": meta.get("total_tool_calls", 0),
        "overall_score": round(pass_count / total_checks, 2),
        "checks_passed": pass_count,
        "checks_total": total_checks,
    }
    return results


def main():
    import glob
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]

    if not paths:
        print("Usage: verify_trace.py <trace.jsonl|dir/>")
        sys.exit(1)

    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files.extend(sorted(p.glob("*.jsonl")))
        else:
            files.append(p)

    for fpath in files:
        try:
            traces = []
            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        traces.append(json.loads(line))
        except Exception as e:
            print(f"\n### {fpath} — ERROR: {e}")
            continue

        for i, trace in enumerate(traces):
            r = verify_trace(trace, verbose=verbose)
            meta = r["_meta"]
            status = "✅" if meta["overall_score"] >= 0.8 else "⚠️" if meta["overall_score"] >= 0.5 else "❌"
            print(f"\n{status} [{meta['source']}] score={meta['overall_score']:.0%} ({meta['checks_passed']}/{meta['checks_total']})")
            for key in sorted(r.keys()):
                if key.startswith("T") and "_" in key:
                    v = r[key]
                    mark = "✅" if v.get("pass") else "⚠️" if "pass" in v else "❌"
                    detail = v.get("detail", "")
                    print(f"  {mark} {key}: {detail[:100]}")
                    if verbose and key == "T0_intro" and v.get("markers"):
                        print(f"       markers: {v['markers']}")

if __name__ == "__main__":
    main()