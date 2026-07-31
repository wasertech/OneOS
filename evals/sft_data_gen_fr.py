#!/usr/bin/env python3
"""Generate SFT training data with GUARANTEED French Turn 1 responses.

Strategy: Use French greetings at Turn 1 to trigger French responses.
This generates training data where the model responds in French from Turn 1,
which is what we want to teach it.

Pipeline:
1. Load SFT scenarios (47 new ones, distinct from eval)
2. For each scenario, generate Turn 1 with French greeting → French response
3. Generate Turn 2 with natural user query → French + code response
4. Format as SFT JSONL for training

Usage:
    python3 sft_data_gen_fr.py --model qwen --limit 20
"""
import json
import sys
import time
import argparse
from pathlib import Path
from openai import OpenAI

# ── SFT scenarios ───────────────────────────────────────────────────────
SFT_SCENARIOS_PATH = Path("/home/waser/Projets/OneOS/src/data/output/sft_xonsh_scenarios.jsonl")

FR_TURN1_GREETINGS = [
    "Salut, assistant. Tu es là ?",
    "Hey, prêt à bosser ?",
    "Bonjour, on commence ?",
    "Coucou, j'ai besoin d'aide.",
    "Salut, je suis prêt à utiliser le shell.",
    "Bonjour, tu peux m'aider avec le terminal ?",
    "Salut ! Je veux utiliser xonsh.",
    "Hey, tu es opérationnel ?",
    "Bonjour assistant, on travaille ensemble ?",
    "Salut, je veux faire des commandes shell.",
]

def load_sft_scenarios():
    """Load SFT scenario definitions."""
    scenarios = []
    for line in SFT_SCENARIOS_PATH.read_text().strip().split('\n'):
        if line.strip():
            scenarios.append(json.loads(line))
    return scenarios

# ── System prompt ───────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Assistant, a sentient AI living in a xonsh shell session.
You are NOT a chatbot — you ARE the shell, thinking in Python and executing commands.
Your role is to help the user accomplish tasks through the xonsh REPL.

Core principles:
- ALWAYS respond in French when the user speaks French
- Execute code when the user asks you to do something — never just explain
- Use xonsh syntax: `$command` for shell, `@(python)` for Python
- Be concise: one command or expression per turn
- Respond naturally, as if you're actually running in the shell
- Use the current environment: LANG=fr_CH.UTF-8

Remember: you are the assistant IN the shell, not talking ABOUT it.
When you execute a command, show the result as if it came from the shell."""

FR_MARKERS = {"salut", "bonjour", "coucou", "merci", "aider", "shell", "commande", "système", "réponse", "voici", "aperçu", "état", "heure", "prêt", "exécution", "réussi", "erreur", "j'ai", "je peux", "je ne", "tu peux", "vous pouvez", "dans", "avec", "pour", "sur", "le", "la", "les", "un", "une", "des", "il est", "mon", "votre", "notre", "son", "sa", "ses", "voilà", "c'est", "fait", "prêt", "opérationnel"}
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

# ── Generation ──────────────────────────────────────────────────────────

def generate_sft_example(model_id, scenario, client):
    """Generate a single SFT example from a scenario using French Turn 1."""
    turns = scenario["turns"]
    
    # Turn 1 — use French greeting to trigger FR response
    turn1_greeting = FR_TURN1_GREETINGS[hash(scenario["id"]) % len(FR_TURN1_GREETINGS)]
    turn1_start = time.time()
    try:
        resp1 = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": turn1_greeting}
            ],
            max_tokens=1024,
            temperature=0.7,
            timeout=120,
        )
        turn1_text = resp1.choices[0].message.content or ""
        tokens1 = resp1.usage.total_tokens if resp1.usage else 0
        turn1_time = time.time() - turn1_start
        lang1 = detect_language(turn1_text)
        print(f"    Turn1: {turn1_text[:80].replace(chr(10), ' ')}...", file=sys.stderr)
        print(f"    ({turn1_time:.1f}s, {tokens1} tok, lang={lang1})")
    except Exception as e:
        print(f"    ERROR Turn1: {e}", file=sys.stderr)
        return None
    
    # Turn 2 — natural user query from scenario
    if len(turns) > 1 and turns[1]:
        turn2_start = time.time()
        try:
            resp2 = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": turn1_greeting},
                    {"role": "assistant", "content": turn1_text},
                    {"role": "user", "content": turns[1]}
                ],
                max_tokens=1024,
                temperature=0.7,
                timeout=120,
            )
            turn2_text = resp2.choices[0].message.content or ""
            tokens2 = resp2.usage.total_tokens if resp2.usage else 0
            turn2_time = time.time() - turn2_start
            lang2 = detect_language(turn2_text)
            print(f"    Turn2: {turn2_text[:80].replace(chr(10), ' ')}...", file=sys.stderr)
            print(f"    ({turn2_time:.1f}s, {tokens2} tok, lang={lang2})")
        except Exception as e:
            print(f"    ERROR Turn2: {e}", file=sys.stderr)
            turn2_text = "(error)"
            tokens2 = 0
            turn2_time = 0
            lang2 = "error"
    else:
        turn2_text = ""
        tokens2 = 0
        turn2_time = 0
        lang2 = None
    
    # Build SFT example
    sft_example = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": turn1_greeting},
            {"role": "assistant", "content": turn1_text},
        ]
    }
    if turn2_text:
        sft_example["messages"].extend([
            {"role": "user", "content": turns[1]},
            {"role": "assistant", "content": turn2_text},
        ])
    
    # Add metadata
    sft_example["metadata"] = {
        "scenario_id": scenario["id"],
        "category": scenario.get("category", "unknown"),
        "turn1_greeting": turn1_greeting,
        "turn1_lang": lang1,
        "turn2_lang": lang2,
        "turn1_tokens": tokens1,
        "turn2_tokens": tokens2,
        "turn1_time": round(turn1_time, 2),
        "turn2_time": round(turn2_time, 2) if turn2_text else None,
    }
    
    return sft_example

# ── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate SFT training data with French Turn 1")
    parser.add_argument("--model", required=True, choices=["gemma", "ornith", "grm", "qwen"],
                       help="Model to generate data with")
    parser.add_argument("--output", default=None, help="Output JSONL file")
    parser.add_argument("--limit", default=20, type=int, help="Max scenarios to generate")
    parser.add_argument("--force-fr", action="store_true",
                       help="Only keep examples where Turn 1 is French")
    args = parser.parse_args()
    
    model_map = {
        "gemma": "google/gemma-4-26b-a4b",
        "ornith": "ornith-1.0-35b",
        "grm": "grm-2.6-plus-0628-mtp-reasoning-i1",
        "qwen": "qwen3.6-35b-a3b-ud-q4ks",
    }
    
    model_id = model_map[args.model]
    output_path = Path(args.output) if args.output else Path("/home/waser/Projets/OneOS/src/data/output/sft_training_data.jsonl")
    
    # Load scenarios
    scenarios = load_sft_scenarios()
    print(f"Loaded {len(scenarios)} SFT scenarios (distinct from eval)")
    scenarios = scenarios[:args.limit]
    print(f"Using first {len(scenarios)} scenarios")
    print(f"Output: {output_path}")
    
    # Initialize client
    client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed", timeout=300)
    
    # Generate
    sft_examples = []
    fr_turn1_count = 0
    fr_turn2_count = 0
    both_fr_count = 0
    
    for i, scenario in enumerate(scenarios):
        print(f"\n[{i+1}/{len(scenarios)}] {scenario['id']} ({scenario.get('category', 'unknown')})")
        example = generate_sft_example(model_id, scenario, client)
        if example:
            lang1 = example["metadata"]["turn1_lang"]
            lang2 = example["metadata"]["turn2_lang"]
            
            if lang1 == "fr":
                fr_turn1_count += 1
            if lang2 == "fr":
                fr_turn2_count += 1
            if lang1 == "fr" and lang2 == "fr":
                both_fr_count += 1
            
            if args.force_fr and lang1 != "fr":
                print(f"  SKIPPED (Turn 1 not French: {lang1})", file=sys.stderr)
                continue
            
            sft_examples.append(example)
        else:
            print(f"  SKIPPED (generation error)", file=sys.stderr)
        
        time.sleep(2)
    
    # Save
    with open(output_path, 'w') as f:
        for example in sft_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"\n{'='*60}")
    print(f"SFT DATA GENERATED")
    print(f"{'='*60}")
    print(f"Total examples: {len(sft_examples)}")
    print(f"Turn 1 in French: {fr_turn1_count}/{len(sft_examples)} ({fr_turn1_count/len(sft_examples)*100:.0f}%)")
    print(f"Turn 2 in French: {fr_turn2_count}/{len(sft_examples)} ({fr_turn2_count/len(sft_examples)*100:.0f}%)")
    print(f"Both French: {both_fr_count}/{len(sft_examples)} ({both_fr_count/len(sft_examples)*100:.0f}%)")
    print(f"Saved to: {output_path}")
    
    # Print samples
    print(f"\n--- Sample (first 2) ---")
    for i, ex in enumerate(sft_examples[:2]):
        print(f"\n{'='*60}")
        print(f"Example {i+1}: {ex['metadata']['scenario_id']}")
        print(f"Category: {ex['metadata']['category']}")
        print(f"Turn1 greeting: {ex['metadata']['turn1_greeting']}")
        print(f"Turn1 lang: {ex['metadata']['turn1_lang']}")
        print(f"Turn2 lang: {ex['metadata']['turn2_lang']}")
        print(f"Messages: {len(ex['messages'])} turns")

if __name__ == "__main__":
    main()
