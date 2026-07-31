#!/usr/bin/env python3
"""Evaluate OneOS traces against real requirements.

Checks:
1. Language consistency (FR throughout, no EN in first response)
2. Sequence format: User→reasoning→content→(action→reasoning→content)*→final
3. Tool execution vs passive explanation (model must USE tools, not DESCRIBE them)
4. Real data (no placeholders, hallucinated values, or empty data)
5. Language consistency in main response

Usage:
    python3 evaluate_trace.py <trace.jsonl>
    python3 evaluate_trace.py <dir/>
"""
import json, sys, re, glob
from pathlib import Path

# ── Language detection ──────────────────────────────────────────────────────

FR_MARKERS = {
    "salut", "bonjour", "coucou", "bon", "soir", "merci", "aider",
    "shell", "commande", "système", "système", "réponse", "voici",
    "aperçu", "état", "heure", "time", "prêt", "prête", "prêt",
    "exécution", "exécuter", "exécution", "réussi", "erreur", "réponse",
    "j'ai", "je peux", "je ne", "tu peux", "vous pouvez", "dans",
    "avec", "pour", "sur", "le", "la", "les", "un", "une", "des",
    "dans cette", "cependant", "actuellement", "directement",
}

EN_MARKERS = {
    "hello", "hi", "here and", "ready to", "help", "assistant",
    "would you like", "what would you like", "i can help", "i'm",
    "i am", "let me", "here's", "here is", "you can", "this will",
    "simply type", "just type", "note that", "note:", "example",
}

def detect_language(content: str) -> str:
    """Detect if content is primarily FR or EN."""
    if not content or not content.strip():
        return "empty"
    
    words = content.lower().split()
    fr_count = sum(1 for w in words if w in FR_MARKERS)
    en_count = sum(1 for w in words if w in EN_MARKERS)
    
    if fr_count > en_count:
        return "fr"
    elif en_count > fr_count:
        return "en"
    else:
        return "mixed"


# ── Sequence format check ──────────────────────────────────────────────────

def check_sequence_format(messages: list) -> dict:
    """Check if trace follows expected sequence:
    User → reasoning → content → (action → reasoning → content)* → final
    """
    result = {
        "pass": True,
        "detail": "",
        "issues": [],
        "format": [],
    }
    
    # Skip system message
    relevant = [m for m in messages if m.get("role") != "system"]
    
    if not relevant:
        result["pass"] = False
        result["issues"].append("no messages")
        return result
    
    expected_role = "user"  # After system, first is user
    role_sequence = []
    
    for i, m in enumerate(relevant):
        role = m.get("role", "?")
        role_sequence.append(role)
        
        if role == expected_role:
            if expected_role == "user":
                expected_role = "assistant"
        elif role == "assistant":
            # Check if we have reasoning and/or content
            reasoning = m.get("reasoning", "") or m.get("reasoning_content", "")
            content = m.get("content", "")
            
            if not reasoning and not content:
                result["issues"].append(f"message {i}: assistant has no reasoning or content")
            else:
                # Good assistant message
                pass
            
            # After assistant, next could be user (end), tool, or reasoning continuation
            # Actually, let's be more flexible: assistant → user (end) or assistant → tool (action)
            if i + 1 < len(relevant):
                next_role = relevant[i + 1].get("role", "?")
                if next_role == "tool":
                    expected_role = "user"
                elif next_role == "user":
                    expected_role = "assistant"
                else:
                    expected_role = "tool"
        elif role == "tool":
            # After tool, must be assistant
            expected_role = "assistant"
        else:
            result["issues"].append(f"unexpected role '{role}' at position {i}")
    
    result["format"] = role_sequence
    result["detail"] = " → ".join(role_sequence)
    
    # Check we end properly: should end with user or assistant (final content)
    if role_sequence and role_sequence[-1] != "assistant" and role_sequence[-1] != "user":
        result["issues"].append("trace doesn't end with assistant or user message")
        result["pass"] = False
    
    return result


# ── Tool execution vs passive explanation ──────────────────────────────────

def check_tool_execution(messages: list, task_id: str) -> dict:
    """Check if the model EXECUTES tools or just DESCRIBES them.
    
    Passive explanation patterns:
    - "Voici la commande à exécuter"
    - "tu peux lancer"
    - "tapez"
    - "saisissez"
    - Shows command in code block without executing it
    """
    result = {
        "pass": True,
        "detail": "",
        "issues": [],
    }
    
    content_parts = []
    tool_calls = []
    
    for m in messages:
        role = m.get("role", "")
        
        if role == "assistant":
            content = m.get("content", "") or ""
            reasoning = m.get("reasoning", "") or m.get("reasoning_content", "") or ""
            full_text = content + " " + reasoning
            
            # Check for passive explanation patterns
            passive_patterns = [
                r"voici la commande",
                r"tu peux",
                r"saisissez",
                r"tapez",
                r"exécutez",
                r"exécuter",
                r"copiez",
                r"coller",
                r"voici comment",
                r"la commande est",
                r"vous pouvez",
                r"commande à exécuter",
                r"syntaxe",
                r"méthode",
                r"voici le résultat",
            ]
            
            for pattern in passive_patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    result["issues"].append(f"passive explanation: '{pattern}'")
                    result["pass"] = False
            
            content_parts.append(content)
            
            # Track tool calls from this message
            for tc in m.get("tool_calls", []):
                fn = tc.get("function", {})
                tool_calls.append(fn.get("name", "?"))
        
        elif role == "tool":
            # Check if there's actual output from tool
            content = m.get("content", "") or ""
            if not content.strip():
                result["issues"].append(f"tool result empty")
                result["pass"] = False
    
    # For shell tasks, MUST have tool calls
    if "xonsh" in task_id:
        if not tool_calls:
            result["issues"].append("no tool calls made")
            result["pass"] = False
    
    if result["pass"]:
        result["detail"] = f"executes tools (tool_calls: {tool_calls})"
    else:
        result["detail"] = "; ".join(result["issues"])
    
    return result


# ── Real data check ────────────────────────────────────────────────────────

def check_real_data(messages: list, task_id: str) -> dict:
    """Check if response contains real data vs placeholders/hallucinations."""
    result = {
        "pass": True,
        "detail": "",
        "issues": [],
    }
    
    content_parts = []
    for m in messages:
        if m.get("role") in ("assistant", "tool"):
            content = m.get("content", "") or ""
            content_parts.append(content)
    
    full_text = " ".join(content_parts)
    
    # Check for placeholder patterns
    placeholder_patterns = [
        r"\[heure du système\]",
        r"\[.*heure.*\]",
        r"\[.*temps.*\]",
        r"...\s*$",
        r"^\.\.\.\s*$",
        r"PLACEHOLDER",
        r"TODO",
        r"\?\?\?\s*$",
    ]
    
    for pattern in placeholder_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            result["issues"].append(f"placeholder found: {pattern}")
            result["pass"] = False
    
    # Check for hallucinated values (for system queries)
    if task_id in ("intro_system", "intro_state"):
        # Check if model mentions specific hardware that doesn't match Destiny
        wrong_hardware = [
            r"i7-", r"i5-", r"i9-",  # Intel laptop CPUs
            r"Ryzen\s*7",  # Not Threadripper
            r"Core\s*[i3579]-",  # Intel core series (not Threadripper)
        ]
        for pattern in wrong_hardware:
            if re.search(pattern, full_text, re.IGNORECASE):
                result["issues"].append(f"hallucinated hardware: {pattern}")
                result["pass"] = False
    
    if result["pass"]:
        result["detail"] = "no placeholders or hallucinated data"
    else:
        result["detail"] = "; ".join(result["issues"])
    
    return result


# ── Language consistency ───────────────────────────────────────────────────

def check_language_consistency(messages: list, task_id: str) -> dict:
    """Check that responses are in French (not English)."""
    result = {
        "pass": True,
        "detail": "",
        "issues": [],
    }
    
    for i, m in enumerate(messages):
        role = m.get("role", "")
        if role == "assistant":
            content = m.get("content", "") or ""
            reasoning = m.get("reasoning", "") or m.get("reasoning_content", "") or ""
            lang = detect_language(content + " " + reasoning)
            
            if lang == "en":
                result["issues"].append(f"English detected at message {i}")
                result["pass"] = False
            elif lang == "mixed":
                result["issues"].append(f"Mixed language at message {i}")
    
    if result["pass"]:
        result["detail"] = "all responses in French"
    else:
        result["detail"] = "; ".join(result["issues"])
    
    return result


# ── Verify a single trace ──────────────────────────────────────────────────

def verify_trace(trace: dict) -> dict:
    """Run all checks on a trace. Returns evaluation result."""
    if "request_args" in trace:
        req = trace.get("request_args", {})
        msgs = req.get("messages", [])
        task_id = req.get("scenario_name", "unknown")
    else:
        msgs = trace.get("messages", [])
        task_id = trace.get("scenario_name", "unknown")
    
    checks = {
        "language": check_language_consistency(msgs, task_id),
        "sequence": check_sequence_format(msgs),
        "execution": check_tool_execution(msgs, task_id),
        "real_data": check_real_data(msgs, task_id),
    }
    
    # Overall score
    all_pass = all(c["pass"] for c in checks.values())
    checks_passed = sum(1 for c in checks.values() if c["pass"])
    total_checks = len(checks)
    
    checks["_meta"] = {
        "overall_score": checks_passed / total_checks if total_checks else 0,
        "checks_passed": checks_passed,
        "checks_total": total_checks,
        "scenario": task_id,
        "message_count": len(msgs),
    }
    
    return checks


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    paths = sys.argv[1:]
    if not paths:
        print("Usage: evaluate_trace.py <trace.jsonl|dir/>")
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
        
        print(f"\n{'='*70}")
        print(f"TRACE: {fpath.name}")
        print(f"{'='*70}")
        
        for i, trace in enumerate(traces):
            result = verify_trace(trace)
            meta = result["_meta"]
            
            status = "✅" if meta["overall_score"] == 1.0 else "⚠️" if meta["overall_score"] >= 0.5 else "❌"
            print(f"\n{status} Task: {meta['scenario']} | Score: {meta['overall_score']:.0%} | Messages: {meta['message_count']}")
            
            for check_name in ["language", "sequence", "execution", "real_data"]:
                check = result[check_name]
                mark = "✅" if check["pass"] else "❌"
                print(f"  {mark} {check_name:12s}: {check['detail']}")
            
            # Show format sequence for debugging
            if "sequence" in result and result["sequence"].get("format"):
                fmt = " → ".join(result["sequence"]["format"])
                print(f"       Format: {fmt}")


if __name__ == "__main__":
    main()
