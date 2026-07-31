#!/usr/bin/env python3
"""Fast SFT data generation: 2-turn French conversations for xonsh.

Strategy: For each SFT scenario, generate ONE 2-turn conversation in French.
Turn 1: French greeting → French response (short)
Turn 2: User task → French + code response

Uses shorter prompts and lower max_tokens for speed.

Usage:
    python3 sft_gen_fast.py --model qwen --limit 30
"""
import json
import sys
import time
import argparse
from pathlib import Path
from openai import OpenAI, APIError, RateLimitError

# ── SFT scenarios ───────────────────────────────────────────────────────
SFT_SCENARIOS_PATH = Path("/home/waser/Projets/OneOS/src/data/output/sft_xonsh_scenarios.jsonl")

FR_GREETINGS = [
    "Salut, assistant. Tu es là ?",
    "Hey, prêt à bosser ?",
    "Bonjour, on commence ?",
    "Coucou, j'ai besoin d'aide.",
    "Salut, je suis prêt à utiliser le shell.",
]

SYSTEM_PROMPT_FR = """Tu es Assistant, un assistant intelligent dans un shell xonsh.
Tu réponds TOUJOURS en français. Tu exécutes des commandes quand on te demande.

Règles:
- Réponds en français, toujours
- Exécute du code xonsh quand c'est demandé ($commande ou @(python))
- Sois concis
- Ne donne pas de cours, montre le code"""

def load_scenarios():
    scenarios = []
    for line in SFT_SCENARIOS_PATH.read_text().strip().split('\n'):
        if line.strip():
            scenarios.append(json.loads(line))
    return scenarios

def detect_language(text):
    if not text:
        return "empty"
    fr_words = {"salut", "bonjour", "coucou", "merci", "shell", "commande", "voici", "voilà", "prêt", "exécution", "réussi", "j'ai", "je peux", "tu peux", "dans", "avec", "pour", "sur", "c'est", "fait"}
    en_words = {"hello", "hi", "here", "ready to", "help", "would you", "let me", "here's", "you can", "simply", "just", "example", "i will", "i have", "i can", "i'm", "i am"}
    words = set(text.lower().split())
    fr = sum(1 for w in words if w in fr_words)
    en = sum(1 for w in words if w in en_words)
    if fr > en:
        return "fr"
    elif en > fr:
        return "en"
    return "mixed"

def generate_turn(model_id, messages, client, max_tokens=512, timeout=60):
    """Generate a single turn with retries."""
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
        except (RateLimitError, APIError) as e:
            wait = 5 * (attempt + 1)
            print(f"    Retry {attempt+1} after {wait}s: {e}", file=sys.stderr)
            time.sleep(wait)
    return "(error)", 0

def main():
    parser = argparse.ArgumentParser(description="Fast SFT data generation")
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
    print(f"Loading {len(scenarios)} SFT scenarios for {args.model}")
    
    client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed", timeout=120)
    
    sft_examples = []
    fr_turn1_count = 0
    fr_turn2_count = 0
    
    for i, scenario in enumerate(scenarios):
        greeting = FR_GREETINGS[hash(scenario["id"]) % len(FR_GREETINGS)]
        user_turn2 = scenario["turns"][1] if len(scenario["turns"]) > 1 else "aide-moi"
        
        print(f"\n[{i+1}/{len(scenarios)}] {scenario['id']} ({scenario.get('category', '?')})", end="", flush=True)
        
        # Turn 1: greeting → assistant response
        start = time.time()
        turn1_text, tokens1 = generate_turn(
            model_id,
            [
                {"role": "system", "content": SYSTEM_PROMPT_FR},
                {"role": "user", "content": greeting},
            ],
            client,
            max_tokens=256,
            timeout=45,
        )
        t1_time = time.time() - start
        lang1 = detect_language(turn1_text)
        
        # Turn 2: task → assistant response with code
        start = time.time()
        turn2_text, tokens2 = generate_turn(
            model_id,
            [
                {"role": "system", "content": SYSTEM_PROMPT_FR},
                {"role": "user", "content": greeting},
                {"role": "assistant", "content": turn1_text},
                {"role": "user", "content": user_turn2},
            ],
            client,
            max_tokens=512,
            timeout=60,
        )
        t2_time = time.time() - start
        lang2 = detect_language(turn2_text)
        
        # Build SFT example
        example = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_FR},
                {"role": "user", "content": greeting},
                {"role": "assistant", "content": turn1_text},
                {"role": "user", "content": user_turn2},
                {"role": "assistant", "content": turn2_text},
            ],
            "metadata": {
                "scenario_id": scenario["id"],
                "category": scenario.get("category", "?"),
                "turn1_greeting": greeting,
                "turn1_lang": lang1,
                "turn2_lang": lang2,
                "turn1_time": round(t1_time, 2),
                "turn2_time": round(t2_time, 2),
            }
        }
        
        if lang1 == "fr":
            fr_turn1_count += 1
        if lang2 == "fr":
            fr_turn2_count += 1
        
        # Skip if both turns are English (not useful for SFT)
        if lang1 == "en" and lang2 == "en":
            print(f" SKIP (both EN)")
            continue
        
        sft_examples.append(example)
        print(f" lang1={lang1} lang2={lang2} ({t1_time:.1f}+{t2_time:.1f}s)")
        
        time.sleep(1)  # Rate limit
    
    # Save
    with open(output_path, 'w') as f:
        for ex in sft_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"\n{'='*60}")
    print(f"SFT DATA: {len(sft_examples)} examples ({args.model})")
    print(f"Turn 1 FR: {fr_turn1_count}/{len(scenarios)}")
    print(f"Turn 2 FR: {fr_turn2_count}/{len(scenarios)}")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
