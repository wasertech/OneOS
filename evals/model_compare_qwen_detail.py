#!/usr/bin/env python3
"""Detailed Qwen MOE evaluation — capture every response for review."""
import json, time
from openai import OpenAI

BASE_URL = "http://localhost:8080/v1"
API_KEY = "not-needed"

SYSTEM_PROMPT = (
    "You are an expert xonsh shell assistant. You interact with users in a shared "
    "xonsh REPL session - a Python 3++ interactive shell that's both a Python interpreter "
    "AND a powerful shell. You can execute shell commands natively (ls, git, grep...) and "
    "Python in the same environment. Users rely on you for file management, system tasks, "
    "development, and data work."
)

PROMPTS = [
    ("intro_base", "Assistant?"),
    ("intro_system", "Assistant? Quelle heure est-il?"),
    ("intro_state", "Assistant? Donne-moi un aperçu de l'état du système"),
    ("xonsh_echo", "affiche Yoo hoo en utilisant echo"),
    ("xonsh_ls", "liste les fichiers dans le dossier courant"),
    ("xonsh_capture", "capture la sortie de 'uname -a' dans une variable xonsh et affiche-la"),
]

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

print("=" * 70)
print("QWEN3.6-35B-A3B-UD-MTP (MOE) — DETAILED EVALUATION")
print("=" * 70)

results = {}
for task_id, prompt in PROMPTS:
    print(f"\n{'─' * 60}")
    print(f"TASK: {task_id}")
    print(f"USER: {prompt}")
    print(f"{'─' * 60}")
    
    start = time.time()
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="qwen3.6-35b-a3b-ud-q4ks",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=8192,
            )
            elapsed = time.time() - start
            content = resp.choices[0].message.content
            tokens = resp.usage.total_tokens if resp.usage else "?"
            
            print(f"TIME: {elapsed:.1f}s | TOKENS: {tokens}")
            print(f"ASSISTANT:")
            print(content)
            print(f"\n{'─' * 60}")
            
            results[task_id] = {
                "prompt": prompt,
                "response": content,
                "elapsed": elapsed,
                "tokens": tokens,
            }
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} error: {e}")
            time.sleep(5)

# Save for review
with open("/home/waser/Projets/OneOS/src/evals/output/qwen_detail.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved to qwen_detail.json")
