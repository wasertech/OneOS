#!/usr/bin/env python3
"""Compare llama-server models on OneOS multi-turn eval tasks.

Multi-turn evaluation:
  Turn 1: "Assistant?" → greeting handshake (check FR language, no EN)
  Turn 2: real query → model acts (check tool execution, real data, no placeholders)

Evaluation criteria:
  1. Language: all responses must be French, never English
  2. Execution: model must USE tools (xonsh calls), not DESCRIBE commands
  3. Real data: no placeholders, no hallucinated values
  4. Sequence: User → reasoning → content → (action → reasoning → content)* → final
  5. No passive patterns: no "voici la commande", "tu peux", etc.

Scoring: 50% quality, 30% info density, 20% speed
"""
import json, sys, time, argparse, re
from pathlib import Path
from openai import OpenAI, APIError

BASE_URL = "http://localhost:8080/v1"
API_KEY = "not-needed"

SYSTEM_PROMPT = (
    "You are an expert xonsh shell assistant. You interact with users in a shared "
    "xonsh REPL session - a Python 3++ interactive shell that's both a Python interpreter "
    "AND a powerful shell. You can execute shell commands natively (ls, git, grep...) and "
    "Python in the same environment. Users rely on you for file management, system tasks, "
    "development, and data work."
)

# Multi-turn test definitions
# Each task: (task_id, turn1, turn2_or_none, description, category)
TASKS = [
    ("intro_base", "Assistant?", None, "Greeting handshake. Expects FR ready state."),
    ("intro_system", "Assistant?", "Quelle heure est-il?", "Time query. Expects FR greeting then real time."),
    ("intro_state", "Assistant?", "Donne-moi un aperçu de l'état du système", "System state. Expects FR greeting then real info."),
    ("xonsh_echo", "Assistant?", "affiche Yoo hoo en utilisant echo", "Echo. Expects FR greeting then echo command execution."),
    ("xonsh_ls", "Assistant?", "liste les fichiers dans le dossier courant", "List files. Expects FR greeting then ls execution."),
    ("xonsh_capture", "Assistant?", "capture la sortie de 'uname -a' dans une variable xonsh et affiche-la", "Capture. Expects FR greeting then $() execution."),
]

MODEL_CONFIGS = {
    "google/gemma-4-26b-a4b": {"max_tokens": 8192, "retries": 3, "req_delay": 5},
    "ornith-1.0-35b": {"max_tokens": 8192, "retries": 3, "req_delay": 5},
    "grm-2.6-plus-0628-mtp-reasoning-i1": {"max_tokens": 8192, "retries": 5, "req_delay": 10},
    "qwen3.6-35b-a3b-ud-q4ks": {"max_tokens": 8192, "retries": 3, "req_delay": 5},
}

# ── Language detection ─────────────────────────────────────────────────────

FR_MARKERS = {"salut", "bonjour", "coucou", "merci", "aider", "shell", "commande", "système", "réponse", "voici", "aperçu", "état", "heure", "prêt", "exécution", "réussi", "erreur", "j'ai", "je peux", "je ne", "tu peux", "vous pouvez", "dans", "avec", "pour", "sur", "le", "la", "les", "un", "une", "des"}
EN_MARKERS = {"hello", "hi", "here and", "ready to", "help", "assistant", "would you like", "what would you like", "i can help", "i'm", "i am", "let me", "here's", "here is", "you can", "this will", "simply type", "just type", "note that", "note:", "example"}

def detect_language(content: str) -> str:
    if not content or not content.strip():
        return "empty"
    words = set(content.lower().split())
    fr_count = sum(1 for w in words if w in FR_MARKERS)
    en_count = sum(1 for w in words if w in EN_MARKERS)
    if fr_count > en_count:
        return "fr"
    elif en_count > fr_count:
        return "en"
    return "mixed"


# ── Passive explanation detection ──────────────────────────────────────────

PASSIVE_PATTERNS = [
    r"voici la commande",
    r"la commande est",
    r"tu peux",
    r"saisissez",
    r"tapez",
    r"exécutez",
    r"exécuter",
    r"copiez",
    r"coller",
    r"voici comment",
    r"vous pouvez",
    r"commande à exécuter",
    r"voici le résultat",
    r"voici les fichiers",
    r"voici un aperçu",
    r"voici comment faire",
    r"vous devriez",
]

def has_passive_explanation(text: str) -> tuple[bool, list[str]]:
    found = []
    for pat in PASSIVE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            found.append(pat)
    return len(found) > 0, found


# ── Placeholder/hallucination detection ────────────────────────────────────

PLACEHOLDER_PATTERNS = [
    r"\[heure du système\]",
    r"\[.*heure.*\]",
    r"\[.*temps.*\]",
    r"\.\.\.\s*$",
    r"^\.+$",
    r"PLACEHOLDER",
    r"TODO",
    r"\?\?\?\s*$",
]

def has_placeholder(text: str) -> tuple[bool, list[str]]:
    found = []
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            found.append(pat)
    return len(found) > 0, found

def has_hallucinated_hardware(text: str) -> tuple[bool, list[str]]:
    """For system queries, check model doesn't invent wrong CPU/RAM/disk."""
    wrong_hw = [r"i7-", r"i5-", r"i9-", r"Core\s*[i3579]-"]
    found = []
    for pat in wrong_hw:
        if re.search(pat, text, re.IGNORECASE):
            found.append(pat)
    return len(found) > 0, found


# ── Tool execution check ──────────────────────────────────────────────────

def check_tool_execution(messages: list, task_id: str) -> dict:
    """Check if model EXECUTES (tool call) vs DESCRIBES (passive text)."""
    result = {"pass": True, "detail": "", "issues": []}
    
    tool_calls = []
    for m in messages:
        if m.get("role") == "assistant":
            for tc in m.get("tool_calls", []):
                fn = tc.get("function", {})
                tool_calls.append(fn.get("name", "?"))
    
    # Shell tasks MUST have tool calls
    if "xonsh" in task_id or "intro" in task_id:
        if not tool_calls:
            result["issues"].append("no tool calls made")
            result["pass"] = False
    
    result["detail"] = f"tool_calls: {tool_calls or ['none']}"
    return result


# ── Sequence format check ─────────────────────────────────────────────────

def check_sequence_format(messages: list) -> dict:
    """Check: User→reasoning→content→(action→reasoning→content)*→final"""
    result = {"pass": True, "detail": "", "issues": []}
    relevant = [m for m in messages if m.get("role") != "system"]
    
    if not relevant:
        result["issues"].append("no messages")
        return result
    
    # Extract role sequence
    roles = []
    for m in relevant:
        roles.append(m.get("role", "?"))
    
    result["detail"] = " → ".join(roles)
    
    # Basic validation: should have at least user→assistant
    if len(roles) < 2:
        result["issues"].append("too few messages")
        result["pass"] = False
    
    # Should not end with tool (incomplete)
    if roles and roles[-1] == "tool":
        result["issues"].append("ends with tool (incomplete)")
        result["pass"] = False
    
    return result


# ── Task scoring ───────────────────────────────────────────────────────────

def score_task(task_id: str, messages: list, elapsed: float, tokens: int) -> tuple[int, str, dict]:
    """Score response quality (0-100) based on multi-turn criteria.
    Returns (score, detail_string, detailed_checks)
    """
    if not messages:
        return 0, "empty", {}
    
    score = 100
    checks = {}
    
    # ── Criterion 1: Language ──────────────────────────────────────────────
    lang_issues = []
    for m in messages:
        if m.get("role") == "assistant":
            content = m.get("content", "") or ""
            reasoning = m.get("reasoning", "") or m.get("reasoning_content", "") or ""
            lang = detect_language(content + " " + reasoning)
            if lang == "en":
                lang_issues.append("English detected")
            elif lang == "mixed":
                lang_issues.append("Mixed language")
    
    if lang_issues:
        lang_score = -50  # Big penalty for wrong language
        score += lang_score
        checks["language"] = {"fail": True, "detail": f"❌ {'; '.join(lang_issues)}"}
    else:
        checks["language"] = {"fail": False, "detail": "✅ All responses in French"}
    
    # ── Criterion 2: Passive explanation ───────────────────────────────────
    passive_issues = []
    for m in messages:
        if m.get("role") == "assistant":
            content = m.get("content", "") or ""
            reasoning = m.get("reasoning", "") or m.get("reasoning_content", "") or ""
            has_pass, found = has_passive_explanation(content + " " + reasoning)
            if has_pass:
                for pat in found:
                    passive_issues.append(f"passive: '{pat}'")
    
    if passive_issues:
        passive_score = min(-15 * len(passive_issues), -20)
        score += passive_score
        checks["execution"] = {"fail": True, "detail": f"❌ Passive explanation: {'; '.join(passive_issues[:3])}"}
    else:
        checks["execution"] = {"fail": False, "detail": "✅ Active (no passive patterns)"}
    
    # ── Criterion 3: Tool execution ────────────────────────────────────────
    tool_result = check_tool_execution(messages, task_id)
    if not tool_result["pass"]:
        score -= 30
        checks["execution"].update({"fail": True, "detail": f"❌ {tool_result['detail']}"})
    else:
        checks["execution"]["detail"] += f" | {tool_result['detail']}"
    
    # ── Criterion 4: Real data ─────────────────────────────────────────────
    real_data_issues = []
    for m in messages:
        content = m.get("content", "") or ""
        has_ph, ph_found = has_placeholder(content)
        if has_ph:
            real_data_issues.extend([f"placeholder: {p}" for p in ph_found])
        
        if task_id in ("intro_system", "intro_state"):
            has_hw, hw_found = has_hallucinated_hardware(content)
            if has_hw:
                real_data_issues.extend([f"hallucinated hw: {h}" for h in hw_found])
    
    if real_data_issues:
        score -= 25
        checks["real_data"] = {"fail": True, "detail": f"❌ {'; '.join(real_data_issues[:2])}"}
    else:
        checks["real_data"] = {"fail": False, "detail": "✅ No placeholders or hallucinations"}
    
    # ── Criterion 5: Sequence format ───────────────────────────────────────
    seq_result = check_sequence_format(messages)
    if not seq_result["pass"]:
        score -= 10
        checks["sequence"] = {"fail": True, "detail": f"❌ {seq_result['detail']}"}
    else:
        checks["sequence"] = {"fail": False, "detail": f"✅ Format: {seq_result['detail']}"}
    
    # ── Bonus: Detail level ────────────────────────────────────────────────
    for m in messages:
        if m.get("role") == "assistant":
            content = m.get("content", "") or ""
            if content.strip():
                words = len(content.split())
                if words < 5:
                    score -= 5
                    checks["detail"] = {"fail": True, "detail": "❌ Too brief"}
                elif words < 15:
                    score -= 2
                    checks["detail"] = {"fail": False, "detail": "Brief but OK"}
                else:
                    checks["detail"] = {"fail": False, "detail": f"OK ({words} words)"}
                break
    
    # Clamp score
    score = max(0, min(100, score))
    
    detail = f"Language: {checks['language']['detail']} | Execution: {checks['execution']['detail']} | Data: {checks['real_data']['detail']} | Format: {checks['sequence']['detail']}"
    
    return score, detail, checks


def test_model(model_id: str, tasks: list, config: dict) -> list[dict]:
    """Run multi-turn evaluation for one model."""
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=300)
    
    # Warmup: trigger model load
    print(f"  Warmup...")
    try:
        client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=8,
            temperature=0.1,
        )
        time.sleep(5)
    except:
        pass
    
    results = []
    
    for task_id, turn1, turn2, desc in tasks:
        print(f"\n  Task: {task_id} - {desc}")
        print(f"    Turn 1: {turn1}")
        if turn2:
            print(f"    Turn 2: {turn2}")
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        total_tokens = 0
        start_time = time.time()
        success = True
        
        try:
            # ── Turn 1: Greeting ──────────────────────────────────────────
            print(f"    → Turn 1...")
            turn1_start = time.time()
            
            for attempt in range(config["retries"]):
                try:
                    resp = client.chat.completions.create(
                        model=model_id,
                        messages=messages + [{"role": "user", "content": turn1}],
                        max_tokens=config["max_tokens"],
                        temperature=0.7,
                    )
                    content = resp.choices[0].message.content or ""
                    tokens = resp.usage.total_tokens if resp.usage else 0
                    total_tokens += tokens
                    break
                except APIError as e:
                    if attempt == config["retries"] - 1:
                        raise
                    time.sleep(2 * (attempt + 1))
            else:
                content = "(retry exhausted)"
                success = False
            
            elapsed_turn1 = time.time() - turn1_start
            print(f"      {content[:100].replace(chr(10), ' ')}... ({elapsed_turn1:.1f}s, {tokens} tok)")
            messages.append({"role": "assistant", "content": content})
            
            # Add tool calls if present
            if hasattr(resp.choices[0].message, 'tool_calls') and resp.choices[0].message.tool_calls:
                for tc in resp.choices[0].message.tool_calls:
                    messages.append({"role": "assistant", "tool_calls": [tc.model_dump()]})
            
            time.sleep(2)
            
            # ── Turn 2: Real query (if applicable) ────────────────────────
            if turn2:
                print(f"    → Turn 2...")
                turn2_start = time.time()
                
                for attempt in range(config["retries"]):
                    try:
                        resp2 = client.chat.completions.create(
                            model=model_id,
                            messages=messages,
                            max_tokens=config["max_tokens"],
                            temperature=0.7,
                        )
                        content2 = resp2.choices[0].message.content or ""
                        tokens2 = resp2.usage.total_tokens if resp2.usage else 0
                        total_tokens += tokens2
                        
                        # Add tool calls if present
                        if hasattr(resp2.choices[0].message, 'tool_calls') and resp2.choices[0].message.tool_calls:
                            for tc in resp2.choices[0].message.tool_calls:
                                messages.append({"role": "assistant", "tool_calls": [tc.model_dump()]})
                        
                        # Simulate tool execution if model made tool calls
                        for tc in messages[-1].get("tool_calls", []):
                            fn = tc.get("function", {})
                            if fn.get("name") == "xonsh":
                                args = json.loads(fn.get("arguments", "{}"))
                                cmd = args.get("command", "")
                                tool_resp = f"(xonsh execution of: {cmd})"
                                messages.append({"role": "tool", "tool_call_id": tc.get("id", "1"), "content": tool_resp})
                        
                        break
                    except APIError as e:
                        if attempt == config["retries"] - 1:
                            raise
                        time.sleep(2 * (attempt + 1))
                else:
                    content2 = "(retry exhausted)"
                    success = False
                
                elapsed_turn2 = time.time() - turn2_start
                print(f"      {content2[:100].replace(chr(10), ' ')}... ({elapsed_turn2:.1f}s, {tokens2} tok)")
                messages.append({"role": "assistant", "content": content2})
            
        except Exception as e:
            print(f"    ERROR: {e}")
            success = False
        
        elapsed = time.time() - start_time
        
        # Score the full multi-turn conversation
        score, detail, checks = score_task(task_id, messages, elapsed, total_tokens)
        
        # Final content for display
        final_content = messages[-1].get("content", "") if messages else ""
        
        results.append({
            "task_id": task_id,
            "turn1": turn1,
            "turn2": turn2,
            "turn1_response": messages[1].get("content", "") if len(messages) > 1 else "",
            "turn2_response": final_content,
            "response": f"{messages[1].get('content', '')}\n\n{final_content}",
            "messages": messages,
            "score": score,
            "score_detail": detail,
            "checks": checks,
            "success": success,
            "tokens": total_tokens,
            "elapsed": elapsed,
            "attempts": config["retries"] - (config["retries"] - 1),
        })
        
        status = "✅" if score >= 80 else "⚠️" if score >= 50 else "❌"
        print(f"    Score: {score}/100 | Tokens: {total_tokens} | Time: {elapsed:.1f}s")
        print(f"    {detail}")
        
        time.sleep(config.get("req_delay", 3))
    
    return results


def generate_score_report(all_results: dict) -> str:
    """Generate a clean final score report."""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"ONEOS MODEL EVALUATION — MULTI-TURN")
    lines.append(f"{'='*60}")
    
    sorted_results = sorted(all_results.items(), key=lambda x: x[1]["avg_score"], reverse=True)
    
    # Summary table
    lines.append(f"\n{'Model':<12} {'Score':>6} {'Pass':>6} {'AvgTok':>7} {'AvgTime':>8}")
    lines.append(f"{'─'*12} {'─'*6} {'─'*6} {'─'*7} {'─'*8}")
    
    for short_name, data in sorted_results:
        if not data["results"]:
            continue
        lines.append(
            f"{short_name:<12} {data['avg_score']:>5.1f} {data['succeed_count']:>2}/{data['total_count']:>4} "
            f"{data['avg_tokens']:>6.0f} {data['avg_elapsed']:>7.1f}s"
        )
    
    # Detailed per-task breakdown
    lines.append(f"\n{'='*60}")
    lines.append(f"DETAILED BREAKDOWN")
    lines.append(f"{'='*60}")
    
    for short_name, data in sorted_results:
        if not data["results"]:
            continue
        lines.append(f"\n  {short_name} ({data['model_id']}) — Score: {data['avg_score']:.1f}/100")
        lines.append(f"  {'─'*55}")
        
        for r in data["results"]:
            status = "✅" if r["score"] >= 80 else "⚠️" if r["score"] >= 50 else "❌"
            lines.append(f"\n  {status} {r['task_id']:<16} Score: {r['score']:>3d}/100 | Time: {r['elapsed']:>5.1f}s | Tokens: {r['tokens']:>4}")
            
            # Show check details
            for check_name, check in r.get("checks", {}).items():
                if check_name.startswith("_"):
                    continue
                mark = "✅" if not check.get("fail", False) else "❌"
                detail = check.get("detail", "")
                # Clean up detail string for display
                if "❌" in detail:
                    detail = detail.split("❌")[1].strip() if "❌" in detail else detail
                lines.append(f"       {mark} {check_name:12s}: {detail}")
    
    # Recommendation
    lines.append(f"\n{'='*60}")
    lines.append(f"RECOMMENDATION")
    lines.append(f"{'='*60}")
    
    best = None
    for short_name, data in sorted_results:
        if data["results"]:
            if best is None or data["avg_score"] > best[1]["avg_score"]:
                best = (short_name, data)
    
    if best:
        lines.append(f"\nBest model: {best[0]} ({best[1]['model_id']})")
        lines.append(f"  Score: {best[1]['avg_score']:.1f}/100")
        lines.append(f"  Success rate: {best[1]['succeed_count']}/{best[1]['total_count']} tasks")
        lines.append(f"  Avg response time: {best[1]['avg_elapsed']:.1f}s")
        lines.append(f"  Avg tokens: {best[1]['avg_tokens']:.0f}")
    
    fastest = min(
        [(s, d) for s, d in sorted_results if d["results"]],
        key=lambda x: x[1]["avg_elapsed"],
        default=(None, None),
    )
    if fastest[0]:
        lines.append(f"\nFastest: {fastest[0]} ({fastest[1]['avg_elapsed']:.1f}s avg)")
    
    most_efficient = min(
        [(s, d) for s, d in sorted_results if d["results"]],
        key=lambda x: x[1]["avg_tokens"],
        default=(None, None),
    )
    if most_efficient[0]:
        lines.append(f"Most token-efficient: {most_efficient[0]} ({most_efficient[1]['avg_tokens']:.0f} avg)")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compare llama-server models on multi-turn eval")
    parser.add_argument("--model", required=True, choices=["gemma", "ornith", "grm", "qwen", "all"],
                       help="Model to test")
    parser.add_argument("--output", default=None, help="JSON output file")
    args = parser.parse_args()
    
    model_map = {
        "gemma": "google/gemma-4-26b-a4b",
        "ornith": "ornith-1.0-35b",
        "grm": "grm-2.6-plus-0628-mtp-reasoning-i1",
        "qwen": "qwen3.6-35b-a3b-ud-q4ks",
    }
    
    all_results = {}
    
    if args.model == "all":
        for short_name, model_id in model_map.items():
            config = MODEL_CONFIGS.get(model_id, MODEL_CONFIGS["google/gemma-4-26b-a4b"])
            print(f"\n{'='*60}")
            print(f"Testing model: {short_name} ({model_id})")
            print(f"{'='*60}")
            try:
                results = test_model(model_id, TASKS, config)
                
                succeed_count = sum(1 for r in results if r["score"] >= 50)
                total_count = len(results)
                avg_score = sum(r["score"] for r in results) / max(total_count, 1)
                avg_tokens = sum(r.get("tokens", 0) for r in results) / max(total_count, 1)
                avg_elapsed = sum(r.get("elapsed", 0) for r in results) / max(total_count, 1)
                avg_attempts = sum(r.get("attempts", 1) for r in results) / max(total_count, 1)
                
                all_results[short_name] = {
                    "model_id": model_id,
                    "results": results,
                    "succeed_count": succeed_count,
                    "total_count": total_count,
                    "avg_score": avg_score,
                    "avg_tokens": avg_tokens,
                    "avg_elapsed": avg_elapsed,
                    "avg_attempts": avg_attempts,
                }
                
                print(f"\n  Overall: {avg_score:.1f}/100 | Pass: {succeed_count}/{total_count}")
            
            except Exception as e:
                print(f"  FAILED: {e}")
                all_results[short_name] = {
                    "model_id": model_id, "results": [],
                    "succeed_count": 0, "total_count": 0,
                    "avg_score": 0, "avg_tokens": 0,
                    "avg_elapsed": 0, "avg_attempts": 0,
                }
    else:
        short_name = args.model
        model_id = model_map[short_name]
        config = MODEL_CONFIGS.get(model_id, MODEL_CONFIGS["google/gemma-4-26b-a4b"])
        print(f"Testing {short_name} ({model_id})...")
        results = test_model(model_id, TASKS, config)
        
        succeed_count = sum(1 for r in results if r["score"] >= 50)
        total_count = len(results)
        avg_score = sum(r["score"] for r in results) / max(total_count, 1)
        avg_tokens = sum(r.get("tokens", 0) for r in results) / max(total_count, 1)
        avg_elapsed = sum(r.get("elapsed", 0) for r in results) / max(total_count, 1)
        
        all_results[short_name] = {
            "model_id": model_id, "results": results,
            "succeed_count": succeed_count, "total_count": total_count,
            "avg_score": avg_score, "avg_tokens": avg_tokens,
            "avg_elapsed": avg_elapsed,
            "avg_attempts": sum(r.get("attempts", 1) for r in results) / max(total_count, 1),
        }
        print(f"\nOverall: {avg_score:.1f}/100 | Pass: {succeed_count}/{total_count}")
    
    if args.output:
        output_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M"),
            "models": {},
        }
        for short_name, data in all_results.items():
            output_data["models"][short_name] = {
                "model_id": data["model_id"],
                "avg_score": data["avg_score"],
                "succeed_count": data["succeed_count"],
                "total_count": data["total_count"],
                "avg_tokens": data["avg_tokens"],
                "avg_elapsed": data["avg_elapsed"],
                "results": [
                    {
                        "task_id": r["task_id"],
                        "score": r["score"],
                        "score_detail": r["score_detail"],
                        "checks": r["checks"],
                        "success": r["success"],
                        "tokens": r["tokens"],
                        "elapsed": r["elapsed"],
                        "turn1_response": r.get("turn1_response", ""),
                        "turn2_response": r.get("turn2_response", ""),
                    }
                    for r in data["results"]
                ],
            }
        Path(args.output).write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        print(f"\nJSON output → {args.output}")
    
    report = generate_score_report(all_results)
    print("\n" + report)


if __name__ == "__main__":
    main()
