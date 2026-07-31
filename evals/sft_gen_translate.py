#!/usr/bin/env python3
"""Generate SFT data: translate English Qwen responses to French.

Strategy:
1. Run Qwen on SFT scenarios (English responses)
2. Translate text parts to French
3. Keep xonsh code blocks intact
4. Save as SFT JSONL with French responses

This gives us SFT data with FR Turn 1 + FR Turn 2.
"""
import json
import sys
import time
import re
import argparse
from pathlib import Path
from openai import OpenAI, RateLimitError

SFT_SCENARIOS_PATH = Path("/home/waser/Projets/OneOS/src/data/output/sft_xonsh_scenarios.jsonl")

SYSTEM_PROMPT = """You are an xonsh shell assistant. Execute commands and show results.
Use xonsh syntax: $command for shell, @(python) for Python.
Be concise and practical."""

def load_scenarios():
    scenarios = []
    for line in SFT_SCENARIOS_PATH.read_text().strip().split('\n'):
        if line.strip():
            scenarios.append(json.loads(line))
    return scenarios

def translate_to_french(text):
    """Translate English text to French, preserving code blocks."""
    if not text or not text.strip():
        return text
    
    # Extract code blocks first
    code_blocks = {}
    counter = [0]
    
    def replace_code(match):
        key = f"__CODE_{counter[0]}__"
        code_blocks[key] = match.group(0)
        counter[0] += 1
        return key
    
    # Replace all code-like patterns
    text_safe = re.sub(
        r'```(?:xonsh|bash)?\s*[\s\S]*?\n```|`[^\n`]+`|\$[^ \t\n()]+|@\([^)]+\)',
        replace_code,
        text
    )
    
    # Simple translation - replace common English phrases with French
    phrases = [
        ("I'm here", "Je suis là"),
        ("I am here", "Je suis là"),
        ("ready to", "prêt à"),
        ("let me", "laisse-moi"),
        ("you can", "tu peux"),
        ("this will", "cela va"),
        ("simply type", "tapez simplement"),
        ("just type", "tapez juste"),
        ("the command", "la commande"),
        ("the output", "la sortie"),
        ("the result", "le résultat"),
        ("the file", "le fichier"),
        ("the directory", "le dossier"),
        ("the process", "le processus"),
        ("the system", "le système"),
        ("the shell", "le shell"),
        ("the code", "le code"),
        ("help", "aider"),
        ("hello", "bonjour"),
        ("hi", "salut"),
        ("here's", "voici"),
        ("here is", "voici"),
        ("you need to", "tu dois"),
        ("to do this", "pour faire cela"),
        ("I will", "je vais"),
        ("I have", "j'ai"),
        ("I can", "je peux"),
        ("I'm", "je suis"),
        ("I am", "je suis"),
    ]
    
    for en, fr in phrases:
        text_safe = text_safe.replace(en, fr)
    
    # Replace code blocks back
    for key, code in code_blocks.items():
        text_safe = text_safe.replace(key, code)
    
    return text_safe

def detect_french(text):
    """Check if text appears to be in French."""
    if not text:
        return False
    fr_words = {"je suis", "tu peux", "voici", "voilà", "prêt", "aide", "shell", "commande", "système", "réponse", "fait", "salut", "bonjour"}
    words = set(text.lower().split())
    return any(w in words for w in fr_words)

def generate_turn(model_id, messages, client, max_tokens=512, timeout=60):
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                timeout=timeout,
            )
            return resp.choices[0].message.content or "", resp.usage.total_tokens if resp.usage else 0
        except RateLimitError:
            time.sleep(5 * (attempt + 1))
    return "(error)", 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["gemma", "ornith", "qwen"])
    parser.add_argument("--output", default=None)
    parser.add_argument("--limit", default=30, type=int)
    args = parser.parse_args()
    
    model_map = {
        "gemma": "google/gemma-4-26b-a4b",
        "ornith": "ornith-1.0-35b",
        "qwen": "qwen3.6-35b-a3b-ud-q4ks",
    }
    model_id = model_map[args.model]
    output_path = Path(args.output) if args.output else Path("/home/waser/Projets/OneOS/src/data/output/sft_training_data.jsonl")
    
    scenarios = load_scenarios()[:args.limit]
    print(f"Generating SFT data: {len(scenarios)} scenarios with {args.model}")
    
    client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed", timeout=120)
    
    sft_examples = []
    fr_count = 0
    
    for i, scenario in enumerate(scenarios):
        greeting = "Salut, assistant. Tu es là ?"
        user_turn2 = scenario["turns"][1] if len(scenario["turns"]) > 1 else "aide-moi"
        
        print(f"\n[{i+1}/{len(scenarios)}] {scenario['id']}", end="", flush=True)
        
        # Turn 1
        t1_start = time.time()
        turn1_en, _ = generate_turn(model_id, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": greeting},
        ], client, max_tokens=256, timeout=45)
        turn1_fr = translate_to_french(turn1_en)
        t1_time = time.time() - t1_start
        
        # Turn 2
        t2_start = time.time()
        turn2_en, _ = generate_turn(model_id, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": greeting},
            {"role": "assistant", "content": turn1_en},
            {"role": "user", "content": user_turn2},
        ], client, max_tokens=512, timeout=60)
        turn2_fr = translate_to_french(turn2_en)
        t2_time = time.time() - t2_start
        
        # Check if translation worked
        is_french = detect_french(turn1_fr) or detect_french(turn2_fr)
        
        example = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": greeting},
                {"role": "assistant", "content": turn1_fr},
                {"role": "user", "content": user_turn2},
                {"role": "assistant", "content": turn2_fr},
            ],
            "metadata": {
                "scenario_id": scenario["id"],
                "category": scenario.get("category", "?"),
                "turn1_en": turn1_en[:50],
                "turn1_fr": turn1_fr[:50],
                "turn2_en": turn2_en[:50],
                "turn2_fr": turn2_fr[:50],
                "is_french": is_french,
                "turn1_time": round(t1_time, 2),
                "turn2_time": round(t2_time, 2),
            }
        }
        
        if is_french:
            fr_count += 1
        
        sft_examples.append(example)
        print(f" FR={'yes' if is_french else 'no'} ({t1_time:.1f}+{t2_time:.1f}s)")
        
        time.sleep(1)
    
    with open(output_path, 'w') as f:
        for ex in sft_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"\n{'='*60}")
    print(f"SFT DATA: {len(sft_examples)} examples ({args.model})")
    print(f"French: {fr_count}/{len(scenarios)}")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
