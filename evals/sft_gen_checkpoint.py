#!/usr/bin/env python3
"""Generate SFT training data with checkpoint/resume.

47 scenarios SFT (distincts de l'eval) → Qwen génère → checkpoint après chaque
→ Abort/reprise possible à tout moment

Usage:
    python3 sft_gen_checkpoint.py --model qwen --limit 47
    python3 sft_gen_checkpoint.py --resume
    python3 sft_gen_checkpoint.py --resume --limit 20
"""
import json, sys, time, argparse
from pathlib import Path
from openai import OpenAI, RateLimitError, APIError

SFT_SCENARIOS = Path("/home/waser/Projets/OneOS/src/data/output/sft_xonsh_scenarios.jsonl")
CHECKPOINT_FILE = Path("/home/waser/Projets/OneOS/src/data/output/sft_checkpoint.json")
OUTPUT_FILE = Path("/home/waser/Projets/OneOS/src/data/output/sft_training_data.jsonl")

SYSTEM_PROMPT = """Tu es Assistant, un assistant dans un shell xonsh.
Réponds en français. Exécute du code xonsh quand on te demande.
Règles:
- Réponds en français
- Code: $command pour shell, @(python) pour Python
- Sois concis"""

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text()).get("completed", [])
    return []

def save_checkpoint(completed, results):
    json.dump({
        "completed": completed,
        "results": results,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }, CHECKPOINT_FILE.open("w"), ensure_ascii=False, indent=2)

def load_results():
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text()).get("results", {})
    return {}

def translate(text):
    if not text:
        return text
    # Key phrases only
    pairs = [
        ("I'm here", "Je suis là"), ("I am here", "Je suis là"),
        ("ready to", "prêt à"), ("let me", "laisse-moi"),
        ("you can", "tu peux"), ("this will", "cela va"),
        ("simply type", "tapez simplement"), ("just type", "tapez juste"),
        ("the command", "la commande"), ("the output", "la sortie"),
        ("the result", "le résultat"), ("the file", "le fichier"),
        ("the directory", "le dossier"), ("the process", "le processus"),
        ("the system", "le système"), ("the shell", "le shell"),
        ("the code", "le code"), ("the error", "l'erreur"),
        ("the message", "le message"), ("the answer", "la réponse"),
        ("the data", "les données"), ("the number", "le nombre"),
        ("the time", "l'heure"), ("the date", "la date"),
        ("the path", "le chemin"), ("the value", "la valeur"),
        ("the function", "la fonction"), ("the variable", "la variable"),
        ("I will", "je vais"), ("I have", "j'ai"), ("I can", "je peux"),
        ("I'm", "je suis"), ("I am", "je suis"),
        ("to run", "pour exécuter"), ("to execute", "pour exécuter"),
        ("to create", "pour créer"), ("to modify", "pour modifier"),
        ("to delete", "pour supprimer"), ("to list", "pour lister"),
        ("to find", "pour trouver"), ("to check", "pour vérifier"),
        ("to show", "pour montrer"), ("to view", "pour afficher"),
        ("to display", "pour afficher"), ("to read", "pour lire"),
        ("to write", "pour écrire"), ("to copy", "pour copier"),
        ("to move", "pour déplacer"), ("to rename", "pour renommer"),
        ("to search", "pour chercher"), ("to replace", "pour remplacer"),
        ("to count", "pour compter"), ("to sort", "pour trier"),
        ("to filter", "pour filtrer"), ("to generate", "pour générer"),
        ("to parse", "pour analyser"), ("to convert", "pour convertir"),
        ("to install", "pour installer"), ("to update", "pour mettre à jour"),
        ("to stop", "pour arrêter"), ("to start", "pour démarrer"),
        ("to restart", "pour redémarrer"), ("to kill", "pour tuer"),
        ("to test", "pour tester"), ("to verify", "pour vérifier"),
        ("to validate", "pour valider"), ("to debug", "pour déboguer"),
        ("to fix", "pour corriger"), ("to resolve", "pour résoudre"),
        ("to manage", "pour gérer"), ("to control", "pour contrôler"),
        ("to configure", "pour configurer"), ("to set", "pour définir"),
        ("to build", "pour construire"), ("to launch", "pour lancer"),
        ("to open", "pour ouvrir"), ("to close", "pour fermer"),
        ("to load", "pour charger"), ("to save", "pour sauvegarder"),
        ("to restore", "pour restaurer"), ("to recover", "pour récupérer"),
        ("to connect", "pour connecter"), ("to disconnect", "pour déconnecter"),
        ("to bind", "pour lier"), ("to mount", "pour monter"),
        ("to extract", "pour extraire"), ("to compress", "pour compresser"),
        ("to encrypt", "pour chiffrer"), ("to decrypt", "pour déchiffrer"),
        ("to deploy", "pour déployer"), ("to publish", "pour publier"),
        ("to share", "pour partager"), ("to document", "pour documenter"),
        ("to explain", "pour expliquer"), ("to demonstrate", "pour démontrer"),
        ("to show", "pour montrer"), ("to display", "pour afficher"),
        ("to present", "pour présenter"), ("to focus", "pour se concentrer"),
        ("to target", "pour cibler"), ("to trigger", "pour déclencher"),
        ("to activate", "pour activer"), ("to enable", "pour activer"),
        ("to disable", "pour désactiver"), ("to turn on", "pour allumer"),
        ("to turn off", "pour éteindre"), ("to toggle", "pour basculer"),
        ("to reverse", "pour inverser"), ("to undo", "pour annuler"),
        ("to cancel", "pour annuler"), ("to abort", "pour annuler"),
        ("to halt", "pour arrêter"), ("to pause", "pour mettre en pause"),
        ("to resume", "pour reprendre"), ("to continue", "pour continuer"),
        ("to progress", "pour progresser"), ("to develop", "pour développer"),
        ("to evolve", "pour évoluer"), ("to migrate", "pour migrer"),
        ("to adapt", "pour adapter"), ("to transform", "pour transformer"),
        ("to customize", "pour personnaliser"), ("to organize", "pour organiser"),
        ("to categorize", "pour catégoriser"), ("to classify", "pour classer"),
        ("to synchronize", "pour synchroniser"), ("to sync", "pour synchroniser"),
        ("to merge", "pour fusionner"), ("to split", "pour diviser"),
        ("to divide", "pour diviser"), ("to combine", "pour combiner"),
        ("to append", "pour ajouter"), ("to insert", "pour insérer"),
        ("to erase", "pour effacer"), ("to clear", "pour effacer"),
        ("to reset", "pour réinitialiser"), ("to initialize", "pour initialiser"),
        ("to configure", "pour configurer"), ("to release", "pour publier"),
        ("to distribute", "pour distribuer"), ("to describe", "pour décrire"),
        ("to illustrate", "pour illustrer"), ("to highlight", "pour mettre en évidence"),
        ("to emphasize", "pour souligner"), ("to stress", "pour insister"),
        ("to aim", "pour viser"), ("to fire", "pour lancer"),
        ("to protect", "pour protéger"), ("to guard", "pour garder"),
        ("to hide", "pour cacher"), ("to block", "pour bloquer"),
        ("to slow", "pour ralentir"), ("to delay", "pour retarder"),
        ("to halt", "pour arrêter"), ("to stop", "pour arrêter"),
        ("to end", "pour terminer"), ("to finish", "pour finir"),
        ("to complete", "pour compléter"), ("to conclude", "pour conclure"),
        ("to answer", "pour répondre"), ("to reply", "pour répondre"),
        ("to act", "pour agir"), ("to perform", "pour exécuter"),
        ("to create", "pour créer"), ("to produce", "pour produire"),
        ("to build", "pour construire"), ("to assemble", "pour assembler"),
        ("to design", "pour concevoir"), ("to plan", "pour planifier"),
        ("to order", "pour commander"), ("to group", "pour grouper"),
        ("to accept", "pour accepter"), ("to reject", "pour rejeter"),
        ("to refuse", "pour refuser"), ("to deny", "pour nier"),
        ("to capture", "pour capturer"), ("to collect", "pour collecter"),
        ("to gather", "pour rassembler"), ("to accumulate", "pour accumuler"),
        ("to store", "pour stocker"), ("to keep", "pour garder"),
        ("to hold", "pour maintenir"), ("to retain", "pour conserver"),
        ("to preserve", "pour préserver"), ("to maintain", "pour maintenir"),
        ("to support", "pour soutenir"), ("to defend", "pour défendre"),
        ("to fight", "pour combattre"), ("to compete", "pour concourir"),
        ("to challenge", "pour défier"), ("to risk", "pour risquer"),
        ("to invest", "pour investir"), ("to spend", "pour dépenser"),
        ("to save", "pour économiser"), ("to book", "pour réserver"),
        ("to greet", "pour saluer"), ("to welcome", "pour accueillir"),
        ("to receive", "pour recevoir"), ("to take", "pour prendre"),
        ("to catch", "pour attraper"), ("to seize", "pour saisir"),
        ("to grab", "pour saisir"), ("to touch", "pour toucher"),
        ("to feel", "pour sentir"), ("to hear", "pour entendre"),
        ("to smell", "pour sentir"), ("to taste", "pour goûter"),
        ("to think", "pour penser"), ("to believe", "pour croire"),
        ("to know", "pour savoir"), ("to understand", "pour comprendre"),
        ("to learn", "pour apprendre"), ("to teach", "pour enseigner"),
        ("to show", "pour montrer"), ("to tell", "pour dire"),
        ("to say", "pour dire"), ("to speak", "pour parler"),
        ("to write", "pour écrire"), ("to read", "pour lire"),
        ("to draw", "pour dessiner"), ("to paint", "pour peindre"),
        ("to sing", "pour chanter"), ("to dance", "pour danser"),
        ("to play", "pour jouer"), ("to work", "pour travailler"),
        ("to study", "pour étudier"), ("to practice", "pour pratiquer"),
        ("to try", "pour essayer"), ("to attempt", "pour tenter"),
        ("to succeed", "pour réussir"), ("to fail", "pour échouer"),
        ("to win", "pour gagner"), ("to lose", "pour perdre"),
        ("to earn", "pour gagner"), ("to spend", "pour dépenser"),
        ("to save", "pour économiser"), ("to borrow", "pour emprunter"),
        ("to lend", "pour prêter"), ("to buy", "pour acheter"),
        ("to sell", "pour vendre"), ("to trade", "pour échanger"),
        ("to exchange", "pour échanger"), ("to swap", "pour échanger"),
        ("to rent", "pour louer"), ("to lease", "pour louer"),
    ]
    
    for en, fr in pairs:
        text = text.replace(en, fr)
    return text

def generate(model_id, messages, client, max_tokens=1024, timeout=120):
    """Generate response. For reasoning models (Qwen), merge reasoning + content."""
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model_id, messages=messages,
                max_tokens=max_tokens, temperature=0.7, timeout=timeout,
            )
            msg = resp.choices[0].message
            # Merge reasoning + content for reasoning models
            reasoning = msg.reasoning_content or ""
            content = msg.content or ""
            # Merge: reasoning first, then content
            if reasoning and content:
                merged = reasoning + "\n\n" + content
            elif reasoning:
                merged = reasoning
            else:
                merged = content
            return merged, resp.usage.total_tokens if resp.usage else 0, resp.choices[0].finish_reason
        except (RateLimitError, APIError) as e:
            time.sleep(5 * (attempt + 1))
    return "", 0, "error"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["gemma", "ornith", "qwen"])
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", default=47, type=int)
    parser.add_argument("--skip-translation", action="store_true")
    args = parser.parse_args()
    
    model_map = {
        "gemma": "google/gemma-4-26b-a4b",
        "ornith": "ornith-1.0-35b",
        "qwen": "qwen3.6-35b-a3b-ud-q4ks",
    }
    model_id = model_map[args.model]
    
    # Load scenarios
    scenarios = []
    for line in SFT_SCENARIOS.read_text().strip().split('\n'):
        if line.strip():
            scenarios.append(json.loads(line))
    if args.limit < len(scenarios):
        scenarios = scenarios[:args.limit]
    
    # Checkpoint
    completed = load_checkpoint() if args.resume else []
    results = load_results() if args.resume else {}
    
    if not args.resume:
        CHECKPOINT_FILE.unlink(missing_ok=True)
        print("Fresh start")
    else:
        print(f"Checkpoint: {len(completed)} done, resuming from {len(completed)+1}/{len(scenarios)}")
    
    to_gen = [s for s in scenarios if s["id"] not in completed]
    print(f"Scenarios to generate: {len(to_gen)}")
    
    # Server config
    if args.model == "qwen":
        base_url = "http://localhost:58145/v1"  # Qwen reasoning model
    else:
        base_url = "http://localhost:8080/v1"  # Preset server
    
    client = OpenAI(base_url=base_url, api_key="not-needed", timeout=180)
    
    for i, scenario in enumerate(to_gen):
        sid = scenario["id"]
        category = scenario.get("category", "?")
        greeting = scenario.get("greeting", "Salut, assistant. Tu es là ?")
        user_query = scenario["turns"][1] if len(scenario["turns"]) > 1 else "aide-moi"
        
        print(f"\n[{i+1}/{len(to_gen)}] {sid} ({category})", end="", flush=True)
        
        # Turn 1
        t0 = time.time()
        t1_raw, tok1, f1 = generate(model_id, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": greeting},
        ], client, max_tokens=256, timeout=60)
        t1_time = time.time() - t0
        
        # Turn 2
        t0 = time.time()
        t2_raw, tok2, f2 = generate(model_id, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": greeting},
            {"role": "assistant", "content": t1_raw},
            {"role": "user", "content": user_query},
        ], client, max_tokens=512, timeout=90)
        t2_time = time.time() - t0
        
        # Translate
        if not args.skip_translation:
            turn1 = translate(t1_raw)
            turn2 = translate(t2_raw)
        else:
            turn1, turn2 = t1_raw, t2_raw
        
        # Build SFT
        example = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": greeting},
                {"role": "assistant", "content": turn1},
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": turn2},
            ],
            "metadata": {
                "scenario_id": sid, "category": category,
                "turn1_greeting": greeting,
                "turn1_raw": t1_raw[:50],
                "turn1_translated": turn1[:50] if not args.skip_translation else None,
                "turn2_raw": t2_raw[:50],
                "turn2_translated": turn2[:50] if not args.skip_translation else None,
                "turn1_tokens": tok1, "turn2_tokens": tok2,
                "turn1_time": round(t1_time, 2), "turn2_time": round(t2_time, 2),
                "finish_reason": f"{f1}/{f2}",
            }
        }
        
        results[sid] = example
        completed.append(sid)
        save_checkpoint(completed, results)
        
        lang1 = "FR" if any(w in turn1.lower() for w in ["je suis", "tu peux", "voici", "prêt", "salut", "bonjour"]) else "EN"
        lang2 = "FR" if any(w in turn2.lower() for w in ["je suis", "tu peux", "voici", "prêt", "commande", "shell"]) else "EN"
        print(f" [{lang1}/{lang2}] ({t1_time:.1f}+{t2_time:.1f}s) ✓")
        
        time.sleep(1)
    
    # Final save
    with open(OUTPUT_FILE, 'w') as f:
        for ex in results.values():
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"\n{'='*60}")
    print(f"SFT DATA: {len(results)} examples ({args.model})")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Checkpoint: {CHECKPOINT_FILE}")

if __name__ == "__main__":
    main()
