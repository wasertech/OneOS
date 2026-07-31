#!/usr/bin/env python3
"""Merge Qwen + Gemma SFT data, translate Qwen to French, produce final dataset.

Merges:
- 47 Gemma examples (already FR)
- 30 Qwen examples (EN, needs translation)

Produces a single dataset with 77 FR examples.
"""
import json
from pathlib import Path

GEMMA_FILE = Path("/home/waser/Projets/OneOS/src/data/output/sft_checkpoint.json")
QWEN_FILE = Path("/home/waser/Projets/OneOS/src/data/output/sft_training_data.jsonl")
OUTPUT_FILE = Path("/home/waser/Projets/OneOS/src/data/output/sft_training_final.jsonl")

# Translation dictionary - comprehensive list
TRANSLATIONS = [
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

# More specific translations for common AI phrases
SPECIFIC_TRANSLATIONS = [
    ("Hello! How can I help you", "Bonjour ! Comment puis-je vous aider"),
    ("I can help you with that", "Je peux vous aider avec ça"),
    ("Let me help you", "Laissez-moi vous aider"),
    ("Here's the command", "Voici la commande"),
    ("Here is the command", "Voici la commande"),
    ("You can use the following command", "Vous pouvez utiliser la commande suivante"),
    ("To do this, you can use", "Pour faire cela, vous pouvez utiliser"),
    ("This will show you", "Cela va vous montrer"),
    ("The output will be", "La sortie sera"),
    ("This command will", "Cette commande va"),
    ("You should see", "Vous devriez voir"),
    ("This is how you", "C'est ainsi que vous"),
    ("To get this information", "Pour obtenir cette information"),
    ("To accomplish this", "Pour accomplir cela"),
    ("First, you need to", "D'abord, vous devez"),
    ("Next, you can", "Ensuite, vous pouvez"),
    ("Finally, you will", "Enfin, vous verrez"),
    ("This is because", "C'est parce que"),
    ("The reason is", "La raison est"),
    ("In order to", "Afin de"),
    ("As you can see", "Comme vous pouvez le voir"),
    ("For example", "Par exemple"),
    ("For instance", "Par exemple"),
    ("That's right", "C'est correct"),
    ("Exactly", "Exactement"),
    ("Correct", "Correct"),
    ("Well", "Eh bien"),
    ("Good", "Bien"),
    ("Great", "Super"),
    ("Awesome", "Génial"),
    ("Perfect", "Parfait"),
    ("I understand", "Je comprends"),
    ("I see", "Je vois"),
    ("That makes sense", "C'est logique"),
    ("That's a good question", "C'est une bonne question"),
    ("That's an interesting question", "C'est une question intéressante"),
    ("I'm not sure", "Je ne suis pas sûr"),
    ("I don't know", "Je ne sais pas"),
    ("Let me check", "Laissez-moi vérifier"),
    ("Let me see", "Laissez-moi voir"),
    ("Let me help you with that", "Laissez-moi vous aider avec cela"),
    ("I'll show you how", "Je vais vous montrer comment"),
    ("I'll help you with that", "Je vais vous aider avec ça"),
    ("I can do that for you", "Je peux faire ça pour vous"),
    ("No problem", "Pas de problème"),
    ("Sure", "Bien sûr"),
    ("Of course", "Bien sûr"),
    ("Absolutely", "Absolument"),
    ("Certainly", "Certainement"),
    ("Yes", "Oui"),
    ("Okay", "D'accord"),
    ("Alright", "D'accord"),
    ("Hmm", "Euh"),
    ("Wait", "Attendez"),
    ("One moment", "Un moment"),
    ("Just a second", "Une seconde"),
    ("In a moment", "Dans un instant"),
    ("Shortly", "Bientôt"),
    ("Right away", "Immédiatement"),
    ("Immediately", "Immédiatement"),
    ("Now", "Maintenant"),
    ("Currently", "Actuellement"),
    ("Recently", "Récemment"),
    ("Previously", "Précédemment"),
    ("Before", "Avant"),
    ("After", "Après"),
    ("During", "Pendant"),
    ("While", "Pendant que"),
    ("When", "Quand"),
    ("Where", "Où"),
    ("What", "Quoi"),
    ("Why", "Pourquoi"),
    ("How", "Comment"),
    ("Who", "Qui"),
    ("Which", "Lequel"),
    ("That", "Cela"),
    ("This", "Ceci"),
    ("These", "Ceux-ci"),
    ("Those", "Ceux-là"),
    ("Everything", "Tout"),
    ("Something", "Quelque chose"),
    ("Anything", "N'importe quoi"),
    ("Nothing", "Rien"),
    ("Someone", "Quelqu'un"),
    ("Everyone", "Tout le monde"),
    ("Anyone", "N'importe qui"),
    ("Nobody", "Personne"),
    ("My", "Mon"),
    ("Your", "Ton"),
    ("Their", "Leur"),
    ("Its", "Son"),
    ("Our", "Notre"),
    ("His", "Son"),
    ("Her", "Son"),
    ("The", "Le"),
    ("A", "Un"),
    ("An", "Un"),
    ("And", "Et"),
    ("But", "Mais"),
    ("Or", "Ou"),
    ("If", "Si"),
    ("Then", "Alors"),
    ("Because", "Parce que"),
    ("So", "Donc"),
    ("However", "Cependant"),
    ("Although", "Bien que"),
    ("While", "Pendant que"),
    ("Whether", "Si"),
    ("Unless", "À moins que"),
    ("Until", "Jusqu'à ce que"),
    ("Since", "Depuis"),
    ("Before", "Avant"),
    ("After", "Après"),
    ("When", "Quand"),
    ("Where", "Où"),
    ("Why", "Pourquoi"),
    ("How", "Comment"),
]


def translate_en_to_fr(text):
    """Translate English text to French."""
    if not text:
        return text
    result = text
    # First apply specific translations (longer/more specific first)
    for en, fr in sorted(SPECIFIC_TRANSLATIONS, key=len, reverse=True):
        result = result.replace(en, fr)
    # Then apply general translations
    for en, fr in TRANSLATIONS:
        result = result.replace(en, fr)
    return result


def main():
    # Load checkpoint data (has both Gemma and Qwen)
    checkpoint = json.loads(GEMMA_FILE.read_text())
    all_results = checkpoint.get("results", {})
    
    # Merge: Gemma (already FR) + Qwen (translate)
    merged = []
    for sid, ex in all_results.items():
        ex_copy = dict(ex)
        # Identify source
        if sid.startswith('sft_extra_'):
            ex_copy["source"] = "qwen"
            # Translate Qwen responses (Turn 1 = messages[2], Turn 2 = messages[4])
            ex_copy["messages"][2]["content"] = translate_en_to_fr(ex_copy["messages"][2]["content"])
            ex_copy["messages"][4]["content"] = translate_en_to_fr(ex_copy["messages"][4]["content"])
        else:
            ex_copy["source"] = "gemma"
        merged.append(ex_copy)
    
    # Write final dataset
    with open(OUTPUT_FILE, 'w') as f:
        for ex in merged:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    # Verify quality
    fr_t1 = sum(1 for ex in merged if any(w in ex['messages'][2]['content'].lower() for w in ['je suis', 'tu peux', 'voici', 'prêt', 'salut', 'bonjour']))
    fr_t2 = sum(1 for ex in merged if any(w in ex['messages'][4]['content'].lower() for w in ['je suis', 'tu peux', 'voici', 'prêt', 'commande', 'shell']))
    
    # Separate quality
    gemma = [ex for ex in merged if ex.get('source') == 'gemma']
    qwen = [ex for ex in merged if ex.get('source') == 'qwen']
    
    gemma_fr_t1 = sum(1 for ex in gemma if any(w in ex['messages'][2]['content'].lower() for w in ['je suis', 'tu peux', 'voici', 'prêt', 'salut', 'bonjour']))
    gemma_fr_t2 = sum(1 for ex in gemma if any(w in ex['messages'][4]['content'].lower() for w in ['je suis', 'tu peux', 'voici', 'prêt', 'commande', 'shell']))
    
    qwen_fr_t1 = sum(1 for ex in qwen if any(w in ex['messages'][2]['content'].lower() for w in ['je suis', 'tu peux', 'voici', 'prêt', 'salut', 'bonjour']))
    qwen_fr_t2 = sum(1 for ex in qwen if any(w in ex['messages'][4]['content'].lower() for w in ['je suis', 'tu peux', 'voici', 'prêt', 'commande', 'shell']))
    
    print(f"\n{'='*60}")
    print(f"FINAL DATASET: {len(merged)} examples")
    print(f"  Gemma: {len(gemma)} (FR)")
    print(f"  Qwen: {len(qwen)} (translated)")
    print(f"\nTurn 1 FR: {fr_t1}/{len(merged)} ({fr_t1/len(merged)*100:.0f}%)")
    print(f"  Gemma: {gemma_fr_t1}/{len(gemma)} ({gemma_fr_t1/len(gemma)*100:.0f}%)")
    print(f"  Qwen: {qwen_fr_t1}/{len(qwen)} ({qwen_fr_t1/len(qwen)*100:.0f}%)")
    print(f"Turn 2 FR: {fr_t2}/{len(merged)} ({fr_t2/len(merged)*100:.0f}%)")
    print(f"  Gemma: {gemma_fr_t2}/{len(gemma)} ({gemma_fr_t2/len(gemma)*100:.0f}%)")
    print(f"  Qwen: {qwen_fr_t2}/{len(qwen)} ({qwen_fr_t2/len(qwen)*100:.0f}%)")
    print(f"Output: {OUTPUT_FILE}")
    
    # Sample one Qwen example to verify translation
    if qwen:
        qwen_ex = qwen[0]
        print(f"\n--- Qwen Sample (translated) ---")
        for i, msg in enumerate(qwen_ex['messages']):
            content = msg['content'][:80] if len(msg['content']) > 80 else msg['content']
            print(f"  [{i}] {msg['role']}: {content}...")
    
    # Sample one Gemma example
    if gemma:
        gemma_ex = gemma[0]
        print(f"\n--- Gemma Sample (already FR) ---")
        for i, msg in enumerate(gemma_ex['messages']):
            content = msg['content'][:80] if len(msg['content']) > 80 else msg['content']
            print(f"  [{i}] {msg['role']}: {content}...")


if __name__ == "__main__":
    main()
