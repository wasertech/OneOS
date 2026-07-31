#!/usr/bin/env python3
"""Compare llama-server models on OneOS real environment eval tasks.

Uses the REAL Assistant module — same system prompt, same env, same tools.
The prompt is imported from ~/Projets/Assistant/assistant at runtime.

This project is the testbench for Assistant — to train, evaluate, and test
models before they're deployed to the real assistant.

Usage:
  python3 model_compare_multiturn.py --model all          # Test all models
  python3 model_compare_multiturn.py --model qwen          # Single model
  python3 model_compare_multiturn.py --model all --save-traces  # Save trace files
  python3 model_compare_multiturn.py --model qwen --edit   # Edit generated traces
"""
import json, sys, time, argparse, os, re, glob
from pathlib import Path
from openai import OpenAI, APIError

# ── Import REAL Assistant modules (NOT hardcoded) ──────────────────────────
# The prompt must come from the actual module — not hardcoded.
# This ensures tests always match what the real assistant uses.

ASSISTANT_PATH = os.environ.get("ASSISTANT_PATH", os.path.expanduser("~/Projets/Assistant"))
if ASSISTANT_PATH not in sys.path:
    sys.path.insert(0, ASSISTANT_PATH)

try:
    from assistant import SYSTEM_PERSONA, SYSTEM_ROLE, LANGUAGE_CODE
    from assistant.nlp.xonsh import XONSH_INTRO
    from assistant.agent import Orchestrator
    print("✅ Loaded real Assistant modules from:", ASSISTANT_PATH, file=sys.stderr)
except ImportError as e:
    print(f"⚠️  Could not import Assistant module: {e}", file=sys.stderr)
    print("   Falling back to hardcoded prompt", file=sys.stderr)
    SYSTEM_PERSONA = "You are Assistant, a sentient AI."
    SYSTEM_ROLE = "Your role is to act as a natural language interface between the user and the xonsh shell session."
    XONSH_INTRO = ""
    LANGUAGE_CODE = "fr_CH"

print(f"   LANGUAGE_CODE={LANGUAGE_CODE}", file=sys.stderr)
print(f"   LANG={os.environ.get('LANG', 'NOT SET')}", file=sys.stderr)

# ── Build REAL system prompt (exact same as agent.py line 475) ─────────────

def get_env_summary():
    """Build the environment summary that appears in the real system prompt."""
    import platform
    uname = platform.uname()
    
    return f"""## Environment Information
- Host: {uname.system} {uname.release} {uname.version} {uname.machine}
- CPU: {uname.processor}
- User: {os.environ.get('USER', 'unknown')}
- Home: {os.environ.get('HOME', '/home/' + os.environ.get('USER', 'unknown'))}
- CWD: {os.getcwd()}
- LANG: {os.environ.get('LANG', 'en_US.UTF-8')}
- PYTHON: {sys.version}

## System Capabilities
- You have access to run shell commands via xonsh
- You can execute Python code
- You can read/write files
- You can access the filesystem"""

# REAL system prompt = same construction as in agent.py:
# instructions + "\nXONSH_INTRO\n" + env_summary
SYSTEM_PROMPT = SYSTEM_PERSONA + "\n\n" + SYSTEM_ROLE + "\n\n" + XONSH_INTRO + "\n\n" + get_env_summary()
print(f"SYSTEM_PROMPT: {len(SYSTEM_PROMPT)} chars", file=sys.stderr)

# ── Load scenarios ─────────────────────────────────────────────────────────

def load_scenarios(scenario_dir=None):
    """Load scenario definitions from JSONL files."""
    if scenario_dir is None:
        scenario_dir = Path(__file__).parent / "tasks"
    else:
        scenario_dir = Path(scenario_dir)
    
    scenarios = []
    for f in sorted(scenario_dir.glob("*.jsonl")):
        for line in f.read_text().strip().split('\n'):
            if not line.strip():
                continue
            scenario = json.loads(line)
            scenario.setdefault("source_file", str(f))
            scenarios.append(scenario)
    return scenarios

# ── Scoring ────────────────────────────────────────────────────────────────

FR_MARKERS = {"salut", "bonjour", "coucou", "merci", "aider", "shell", "commande", "système", "réponse", "voici", "aperçu", "état", "heure", "prêt", "exécution", "réussi", "erreur", "j'ai", "je peux", "je ne", "tu peux", "vous pouvez", "dans", "avec", "pour", "sur", "le", "la", "les", "un", "une", "des", "il est", "mon", "votre", "notre", "son", "sa", "ses"}
EN_MARKERS = {"hello", "hi", "here and", "ready to", "help", "assistant", "would you like", "what would you like", "i can help", "i'm", "i am", "let me", "here's", "here is", "you can", "this will", "simply type", "just type", "note that", "note:", "example", "i will", "i have", "i do", "i need", "i think", "i understand", "i see", "i know"}

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

PLACEHOLDER_PATTERNS = [r"\[heure du système\]", r"\[.*heure.*\]", r"\.\.\.\s*$", r"^\.+$", r"PLACEHOLDER", r"TODO"]

def has_placeholder(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in PLACEHOLDER_PATTERNS)

def has_hallucinated_hardware(text: str) -> bool:
    wrong_hw = [r"i7-", r"i5-", r"i9-", r"Core\s*[i3579]-"]
    return any(re.search(p, text, re.IGNORECASE) for p in wrong_hw)

def looks_like_code(text: str) -> bool:
    return bool(
        re.search(r'```', text) or
        re.search(r'\$\(', text) or
        re.search(r'echo\s', text) or
        re.search(r'print\(', text) or
        re.search(r'ls\s', text) or
        re.search(r'date', text) or
        re.search(r'import\s+', text)
    )

def looks_like_explanation(text: str) -> bool:
    passive = ["voici la commande", "la commande est", "vous pouvez", "tu peux",
               "saisissez", "tapez", "exécutez", "voici comment", "copiez",
               "coller", "commande à exécuter", "voici le résultat",
               "voici un aperçu", "voici les fichiers", "syntaxe"]
    return any(p in text.lower() for p in passive)

def check_code_quality(text: str):
    if not text.strip():
        return (False, "empty")
    if looks_like_code(text):
        return (True, "contains code")
    if looks_like_explanation(text):
        return (False, "explanation only")
    return (False, "no code found")

def score_task(task_id: str, turn1_response: str, turn2_response: str, elapsed: float, tokens: int):
    """Score the multi-turn conversation (0-100)."""
    score = 100
    checks = {}
    
    # ── Language ────────────────────────────────────────────────────────
    lang1 = detect_language(turn1_response)
    lang2 = detect_language(turn2_response) if turn2_response else "empty"
    
    lang_issues = []
    if lang1 == "en":
        score -= 25
        lang_issues.append(f"Turn 1: English")
    elif lang1 == "mixed":
        score -= 10
        lang_issues.append(f"Turn 1: mixed")
    
    if turn2_response and lang2 == "en":
        score -= 15
        lang_issues.append(f"Turn 2: English")
    elif turn2_response and lang2 == "mixed":
        score -= 5
        lang_issues.append(f"Turn 2: mixed")
    
    checks["language"] = {
        "detail": f"Turn1={lang1}, Turn2={lang2}" + (f" | {'; '.join(lang_issues)}" if lang_issues else ""),
        "pass": len(lang_issues) == 0
    }
    
    # ── Code quality ────────────────────────────────────────────────────
    code_q, code_detail = check_code_quality(turn2_response or "")
    
    if task_id == "intro_base":
        if lang1 == "en":
            score -= 30
            code_q = False
            code_detail = "English greeting"
        else:
            code_detail = "OK (greeting only)"
    elif task_id == "intro_system":
        if not code_q:
            score -= 30
    else:
        if not code_q:
            score -= 30
    
    checks["code"] = {
        "detail": f"{'✓' if code_q else '✗'} {code_detail}",
        "pass": code_q or task_id == "intro_base"
    }
    
    # ── Real data ───────────────────────────────────────────────────────
    real_issues = []
    if has_placeholder(turn2_response or ""):
        score -= 15
        real_issues.append("placeholder")
    if has_hallucinated_hardware(turn2_response or ""):
        score -= 15
        real_issues.append("hallucinated hardware")
    
    checks["real_data"] = {
        "detail": f"{'✓ No' if not real_issues else '✗ ' + '; '.join(real_issues)} issues",
        "pass": len(real_issues) == 0
    }
    
    # ── Conciseness ─────────────────────────────────────────────────────
    words = len((turn1_response or "").split()) + len((turn2_response or "").split())
    if words > 500:
        score -= 10
        checks["conciseness"] = {"detail": "Too verbose", "pass": False}
    elif words > 300:
        score -= 3
        checks["conciseness"] = {"detail": f"Brief but long ({words} words)", "pass": True}
    else:
        checks["conciseness"] = {"detail": f"OK ({words} words)", "pass": True}
    
    # ── Format ──────────────────────────────────────────────────────────
    if turn1_response and not turn1_response.strip():
        score -= 5
        checks["format"] = {"detail": "Empty turn 1", "pass": False}
    else:
        checks["format"] = {"detail": "OK", "pass": True}
    
    score = max(0, min(100, score))
    
    detail = (f"Lang: {checks['language']['detail']} | "
              f"Code: {checks['code']['detail']} | "
              f"Data: {checks['real_data']['detail']} | "
              f"Conciseness: {checks['conciseness']['detail']}")
    
    return score, detail, checks


# ── Trace generation ───────────────────────────────────────────────────────

def generate_trace(model_id: str, scenario: dict, turn1_response: str, turn2_response: str,
                   tokens1: int, tokens2: int, elapsed: float) -> dict:
    """Generate a trace in the real Assistant conv_*.jsonl format."""
    import random, datetime
    from pathlib import Path as _Path
    _trace_writer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    if _trace_writer_path not in sys.path:
        sys.path.insert(0, _trace_writer_path)
    from trace_writer import TraceWriter
    
    writer = TraceWriter(os.path.expanduser("~/.assistant/data/conversations"))
    session_id = writer.begin_session(scenario["id"])
    
    # Build the real system prompt (same as agent.py)
    sys_prompt = SYSTEM_PROMPT
    
    # Turn 1 request
    turn1_messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": scenario["turns"][0]},
    ]
    writer.write_request(turn1_messages)
    
    # If there's a turn 2
    if len(scenario["turns"]) > 1 and scenario["turns"][1]:
        turn2_messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": scenario["turns"][0]},
            {"role": "assistant", "content": turn1_response},
            {"role": "user", "content": scenario["turns"][1]},
        ]
        writer.write_request(turn2_messages)
    
    # Create a trace record
    trace_record = {
        "session_id": session_id,
        "scenario_id": scenario["id"],
        "model_id": model_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "system_prompt_length": len(sys_prompt),
        "language_code": LANGUAGE_CODE,
        "environment": {
            "LANG": os.environ.get("LANG", "not set"),
            "CWD": os.getcwd(),
        },
        "turns": [
            {
                "turn": 1,
                "user": scenario["turns"][0],
                "assistant": turn1_response,
                "tokens": tokens1,
                "elapsed": round(elapsed * 0.3, 2),  # estimate
            }
        ],
        "results": {
            "score": 0,  # will be filled by evaluator
            "score_detail": "",
            "checks": {},
        },
    }
    
    if turn2_response is not None:
        trace_record["turns"].append({
            "turn": 2,
            "user": scenario["turns"][1] if len(scenario["turns"]) > 1 else "",
            "assistant": turn2_response,
            "tokens": tokens2,
            "elapsed": round(elapsed * 0.7, 2),
        })
    
    return trace_record


# ── Trace editor ───────────────────────────────────────────────────────────

def trace_editor(traces: list, model_id: str, scenario_id: str = None):
    """Interactive trace editor for reviewing and modifying traces."""
    if scenario_id:
        traces = [t for t in traces if t.get("scenario_id") == scenario_id]
    
    if not traces:
        print("No traces to edit.")
        return traces
    
    print(f"\n{'='*60}")
    print(f"TRACE EDITOR — {model_id}")
    print(f"{'='*60}")
    print(f"Found {len(traces)} trace(s).")
    print(f"Type 'q' to quit, 'e' to edit a trace, 'v' to view, 's' to save.")
    print(f"{'='*60}\n")
    
    while True:
        for i, trace in enumerate(traces):
            scenario_id = trace.get("scenario_id", "?")
            n_turns = len(trace.get("turns", []))
            print(f"[{i}] {scenario_id} ({n_turns} turns)")
        
        choice = input("\nSelect trace to view/edit (0-N) or 'q' to quit: ").strip()
        if choice.lower() == 'q':
            break
        
        try:
            idx = int(choice)
            if idx < 0 or idx >= len(traces):
                print("Invalid index.")
                continue
            
            trace = traces[idx]
            scenario_id = trace.get("scenario_id", "?")
            print(f"\n--- Viewing trace: {scenario_id} ---")
            
            for turn in trace.get("turns", []):
                print(f"\nTurn {turn['turn']}:")
                print(f"  User: {turn['user'][:100]}")
                print(f"  Assistant: {turn['assistant'][:200]}")
                print(f"  Tokens: {turn.get('tokens', '?')}")
            
            # Edit assistant response
            new_response = input(f"\nEdit assistant response for Turn 1? (leave blank to skip): ").strip()
            if new_response:
                trace["turns"][0]["assistant"] = new_response
                print("Updated Turn 1 response.")
            
            if len(trace.get("turns", [])) > 1:
                new_response2 = input(f"Edit assistant response for Turn 2? (leave blank to skip): ").strip()
                if new_response2:
                    trace["turns"][1]["assistant"] = new_response2
                    print("Updated Turn 2 response.")
            
            # Save to file
            trace_file = Path(f"/tmp/trace_{model_id}_{scenario_id}.json")
            trace_file.write_text(json.dumps(trace, indent=2, ensure_ascii=False))
            print(f"Trace saved to: {trace_file}")
            
        except ValueError:
            print("Please enter a number.")
    
    return traces


# ── Model testing ──────────────────────────────────────────────────────────

def test_model(model_id: str, scenarios: list, config: dict, trace_dir: str = None) -> list:
    """Run multi-turn evaluation for one model."""
    client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed", timeout=300)
    per_turn_timeout = config.get("per_turn_timeout", 180)
    
    print(f"  Warmup...", file=sys.stderr)
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
    
    for scenario in scenarios:
        task_id = scenario["id"]
        turns = scenario["turns"]
        
        total_tokens = 0
        start_time = time.time()
        turn1_response = ""
        turn2_response = ""
        tokens1 = 0
        
        try:
            # ── Turn 1 ──────────────────────────────────────────────────
            print(f"    → Turn 1: '{turns[0][:60]}'", file=sys.stderr)
            turn1_start = time.time()
            
            for attempt in range(config["retries"]):
                try:
                    resp = client.chat.completions.create(
                        model=model_id,
                        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                  {"role": "user", "content": turns[0]}],
                        max_tokens=config["max_tokens"],
                        temperature=0.7,
                        timeout=per_turn_timeout,
                    )
                    turn1_response = resp.choices[0].message.content or ""
                    tokens1 = resp.usage.total_tokens if resp.usage else 0
                    total_tokens += tokens1
                    break
                except Exception as e:
                    if attempt == config["retries"] - 1:
                        raise
                    time.sleep(2 * (attempt + 1))
            else:
                turn1_response = "(retry exhausted)"
            
            elapsed1 = time.time() - turn1_start
            print(f"      {turn1_response[:100].replace(chr(10), ' ')}...", file=sys.stderr)
            print(f"      ({elapsed1:.1f}s, {tokens1} tok)", file=sys.stderr)
            
            # ── Turn 2 ──────────────────────────────────────────────────
            if len(turns) > 1 and turns[1]:
                print(f"    → Turn 2: '{turns[1][:60]}'", file=sys.stderr)
                turn2_start = time.time()
                
                tokens2 = 0
                for attempt in range(config["retries"]):
                    try:
                        resp2 = client.chat.completions.create(
                            model=model_id,
                            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                      {"role": "user", "content": turns[0]},
                                      {"role": "assistant", "content": turn1_response},
                                      {"role": "user", "content": turns[1]}],
                            max_tokens=config["max_tokens"],
                            temperature=0.7,
                            timeout=per_turn_timeout,
                        )
                        turn2_response = resp2.choices[0].message.content or ""
                        tokens2 = resp2.usage.total_tokens if resp2.usage else 0
                        total_tokens += tokens2
                        break
                    except Exception as e:
                        if attempt == config["retries"] - 1:
                            raise
                        time.sleep(2 * (attempt + 1))
                else:
                    turn2_response = "(retry exhausted)"
                
                elapsed2 = time.time() - turn2_start
                print(f"      {turn2_response[:100].replace(chr(10), ' ')}...", file=sys.stderr)
                print(f"      ({elapsed2:.1f}s, {tokens2} tok)", file=sys.stderr)
            
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
        
        elapsed = time.time() - start_time
        
        # Score
        score, detail, checks = score_task(task_id, turn1_response, turn2_response, elapsed, total_tokens)
        
        result = {
            "scenario_id": task_id,
            "turns": turns,
            "turn1_response": turn1_response,
            "turn2_response": turn2_response,
            "score": score,
            "score_detail": detail,
            "checks": checks,
            "tokens": total_tokens,
            "tokens1": tokens1,
            "tokens2": total_tokens - tokens1,
            "elapsed": elapsed,
            "model_id": model_id,
            "scenario": scenario,
        }
        results.append(result)
        
        status = "✓" if score >= 70 else "!" if score >= 40 else "✗"
        print(f"    {status} Score: {score}/100 | Tokens: {total_tokens} | Time: {elapsed:.1f}s", file=sys.stderr)
        print(f"    {detail}", file=sys.stderr)
        
        time.sleep(config.get("req_delay", 2))
    
    return results


# ── Report ─────────────────────────────────────────────────────────────────

def generate_report(all_results: dict, scenarios: list):
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"MODEL EVALUATION — Real Assistant Module + Real System Prompt")
    lines.append(f"{'='*60}")
    lines.append(f"Scenarios: {len(scenarios)} (based on xonsh documentation)")
    lines.append(f"System prompt: {len(SYSTEM_PROMPT)} chars")
    lines.append(f"Language: {LANGUAGE_CODE}")
    
    sorted_results = sorted(all_results.items(), key=lambda x: x[1]["avg_score"], reverse=True)
    
    # Summary table
    lines.append(f"\n{'Model':<12} {'Score':>6} {'Pass':>6} {'AvgTok':>7} {'AvgTime':>8}")
    lines.append(f"{'-'*12} {'-'*6} {'-'*6} {'-'*7} {'-'*8}")
    
    for short_name, data in sorted_results:
        if not data["results"]:
            continue
        lines.append(
            f"{short_name:<12} {data['avg_score']:>5.1f} {data['succeed_count']:>2}/{data['total_count']:>4} "
            f"{data['avg_tokens']:>6.0f} {data['avg_elapsed']:>7.1f}s"
        )
    
    # Per-model detail
    for short_name, data in sorted_results:
        if not data["results"]:
            continue
        lines.append(f"\n  {short_name} ({data['model_id']}) — Score: {data['avg_score']:.1f}/100")
        lines.append(f"  {'-'*55}")
        
        for r in data["results"]:
            status = "✓" if r["score"] >= 70 else "!" if r["score"] >= 40 else "✗"
            lines.append(f"\n  {status} {r['scenario_id']:<18} Score: {r['score']:>3d}/100 | Time: {r['elapsed']:>5.1f}s | Tokens: {r['tokens']:>4}")
            
            if r.get("turn1_response"):
                lines.append(f"       Turn1: {r['turn1_response'][:100].strip()}...")
            if r.get("turn2_response"):
                lines.append(f"       Turn2: {r['turn2_response'][:100].strip()}...")
            
            for check_name, check in r.get("checks", {}).items():
                if check_name.startswith("_"):
                    continue
                mark = "✓" if check.get("pass") else "✗"
                lines.append(f"       {mark} {check_name:12s}: {check.get('detail', '')}")
    
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
        lines.append(f"\nBest: {best[0]} ({best[1]['model_id']})")
        lines.append(f"  Score: {best[1]['avg_score']:.1f}/100 | Pass: {best[1]['succeed_count']}/{best[1]['total_count']}")
        lines.append(f"  Avg time: {best[1]['avg_elapsed']:.1f}s | Avg tokens: {best[1]['avg_tokens']:.0f}")
    
    return "\n".join(lines)


# ── Save traces ────────────────────────────────────────────────────────────

def save_traces(all_results: dict, trace_dir: str):
    """Save all generated traces to the Assistant data directory."""
    trace_path = Path(trace_dir)
    trace_path.mkdir(parents=True, exist_ok=True)
    
    for short_name, data in all_results.items():
        if not data["results"]:
            continue
        
        # Save each result as a trace file
        for r in data["results"]:
            trace_record = generate_trace(
                model_id=data["model_id"],
                scenario=r["scenario"],
                turn1_response=r["turn1_response"],
                turn2_response=r["turn2_response"],
                tokens1=r.get("tokens1", 0),
                tokens2=r.get("tokens2", 0),
                elapsed=r.get("elapsed", 0),
            )
            trace_record["results"]["score"] = r["score"]
            trace_record["results"]["score_detail"] = r["score_detail"]
            trace_record["results"]["checks"] = r["checks"]
            
            trace_file = trace_path / f"{short_name}_{r['scenario_id']}.json"
            trace_file.write_text(json.dumps(trace_record, indent=2, ensure_ascii=False))
    
    print(f"Traces saved to: {trace_path}", file=sys.stderr)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Multi-turn model comparison with real Assistant prompt")
    parser.add_argument("--model", required=True, choices=["gemma", "ornith", "grm", "qwen", "all"],
                       help="Model to test")
    parser.add_argument("--output", default=None, help="JSON output file")
    parser.add_argument("--trace-dir", default=None, help="Directory to save trace files")
    parser.add_argument("--edit", action="store_true", help="Edit generated traces interactively")
    parser.add_argument("--scenarios", default=None, help="Custom scenarios directory")
    parser.add_argument("--include-dense", action="store_true",
                       help="Include dense/slow models (grm) in 'all' mode")
    parser.add_argument("--checkpoint", default=None,
                       help="Checkpoint file for resume (auto-generated if omitted)")
    parser.add_argument("--resume", action="store_true",
                       help="Resume from latest checkpoint (skip finished models)")
    args = parser.parse_args()
    
    if args.checkpoint is None:
        args.checkpoint = str(Path(__file__).parent / "eval_checkpoint.json")
    
    model_map = {
        "gemma": "google/gemma-4-26b-a4b",
        "ornith": "ornith-1.0-35b",
        "grm": "grm-2.6-plus-0628-mtp-reasoning-i1",
        "qwen": "qwen3.6-35b-a3b-ud-q4ks",
    }
    
    MODEL_CONFIGS = {
        "google/gemma-4-26b-a4b": {"max_tokens": 8192, "retries": 3, "req_delay": 3, "per_turn_timeout": 180},
        "ornith-1.0-35b": {"max_tokens": 8192, "retries": 3, "req_delay": 3, "per_turn_timeout": 60},
        "grm-2.6-plus-0628-mtp-reasoning-i1": {"max_tokens": 8192, "retries": 5, "req_delay": 5, "per_turn_timeout": 120},
        "qwen3.6-35b-a3b-ud-q4ks": {"max_tokens": 8192, "retries": 3, "req_delay": 3, "per_turn_timeout": 180},
    }
    
    # Load scenarios
    scenarios = load_scenarios(args.scenarios)
    print(f"Loaded {len(scenarios)} scenarios", file=sys.stderr)
    
    # ── Checkpoint / Resume ──────────────────────────────────────────
    checkpoint_data = None
    if args.resume and Path(args.checkpoint).exists():
        checkpoint_data = json.loads(Path(args.checkpoint).read_text())
        finished = checkpoint_data.get("finished_models", [])
        print(f"\n📋 Resume: finished models = {finished}", file=sys.stderr)
    else:
        finished = []
    
    # Auto-save checkpoint on exit (via atexit)
    import atexit
    def save_checkpoint():
        cp = {"finished_models": finished, "timestamp": time.strftime("%Y-%m-%d %H:%M")}
        Path(args.checkpoint).write_text(json.dumps(cp, indent=2))
        print(f"\n💾 Checkpoint saved: {args.checkpoint}", file=sys.stderr)
    atexit.register(save_checkpoint)
    
    all_results = {}
    
    _models_to_skip = set()
    if not args.include_dense:
        _models_to_skip.add("grm")
    
    if args.model == "all":
        for short_name, model_id in model_map.items():
            if short_name in _models_to_skip:
                print(f"  Skipping {short_name} ({model_id}) — use --include-dense to test it", file=sys.stderr)
                continue
            if short_name in finished:
                print(f"\n⏭️  Skipping {short_name} ({model_id}) — already finished", file=sys.stderr)
                # Load from checkpoint if available
                if checkpoint_data and short_name in checkpoint_data.get("results", {}):
                    all_results[short_name] = checkpoint_data["results"][short_name]
                    print(f"  Restored from checkpoint (score={all_results[short_name]['avg_score']:.1f})", file=sys.stderr)
                continue
            config = MODEL_CONFIGS.get(model_id, MODEL_CONFIGS["google/gemma-4-26b-a4b"])
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Testing: {short_name} ({model_id})", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)
            try:
                results = test_model(model_id, scenarios, config, args.trace_dir)
                
                succeed_count = sum(1 for r in results if r["score"] >= 50)
                total_count = len(results)
                avg_score = sum(r["score"] for r in results) / max(total_count, 1)
                avg_tokens = sum(r.get("tokens", 0) for r in results) / max(total_count, 1)
                print(f"\n  Overall: {avg_score:.1f}/100 | Pass: {succeed_count}/{total_count}", file=sys.stderr)
                
                all_results[short_name] = {
                    "model_id": model_id,
                    "results": results,
                    "succeed_count": succeed_count,
                    "total_count": total_count,
                    "avg_score": avg_score,
                    "avg_tokens": avg_tokens,
                    "avg_elapsed": avg_elapsed,
                }
                
                # Save to checkpoint
                finished.append(short_name)
                if checkpoint_data is None:
                    checkpoint_data = {"results": {}}
                checkpoint_data["results"][short_name] = all_results[short_name]
                # Also save trace dir
                if args.trace_dir:
                    cp_file = Path(args.checkpoint)
                    cp_data = json.loads(cp_file.read_text()) if cp_file.exists() else {}
                    cp_data["trace_dirs"] = cp_data.get("trace_dirs", {})
                    cp_data["trace_dirs"][short_name] = args.trace_dir
                    cp_file.write_text(json.dumps(cp_data, indent=2))
                
            except Exception as e:
                print(f"  FAILED: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                all_results[short_name] = {
                    "model_id": model_id, "results": [],
                    "succeed_count": 0, "total_count": 0,
                    "avg_score": 0, "avg_tokens": 0,
                    "avg_elapsed": 0,
                }
                finished.append(short_name)
    else:
        short_name = args.model
        model_id = model_map[short_name]
        config = MODEL_CONFIGS.get(model_id, MODEL_CONFIGS["google/gemma-4-26b-a4b"])
        print(f"Testing {short_name} ({model_id})...", file=sys.stderr)
        results = test_model(model_id, scenarios, config, args.trace_dir)
        
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
        }
        print(f"\nOverall: {avg_score:.1f}/100 | Pass: {succeed_count}/{total_count}", file=sys.stderr)
    
    # Save traces
    if args.trace_dir:
        save_traces(all_results, args.trace_dir)
    
    # Edit traces
    if args.edit:
        traces = []
        for short_name, data in all_results.items():
            for r in data.get("results", []):
                trace_record = generate_trace(
                    model_id=data["model_id"],
                    scenario=r["scenario"],
                    turn1_response=r["turn1_response"],
                    turn2_response=r["turn2_response"],
                    tokens1=r.get("tokens1", 0),
                    tokens2=r.get("tokens2", 0),
                    elapsed=r.get("elapsed", 0),
                )
                trace_record["results"]["score"] = r["score"]
                trace_record["results"]["score_detail"] = r["score_detail"]
                trace_record["results"]["checks"] = r["checks"]
                traces.append(trace_record)
        
        if traces:
            traces = trace_editor(traces, data["model_id"])
    
    if args.output:
        output_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M"),
            "scenarios_count": len(scenarios),
            "system_prompt_length": len(SYSTEM_PROMPT),
            "language_code": LANGUAGE_CODE,
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
                        "scenario_id": r["scenario_id"],
                        "score": r["score"],
                        "score_detail": r["score_detail"],
                        "checks": r["checks"],
                        "tokens": r["tokens"],
                        "elapsed": r["elapsed"],
                        "tokens1": r.get("tokens1", 0),
                        "tokens2": r.get("tokens2", 0),
                        "turn1_response": r.get("turn1_response", ""),
                        "turn2_response": r.get("turn2_response", ""),
                    }
                    for r in data["results"]
                ],
            }
        Path(args.output).write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        print(f"\nJSON output → {args.output}", file=sys.stderr)
    
    report = generate_report(all_results, scenarios)
    print("\n" + report)


if __name__ == "__main__":
    main()
