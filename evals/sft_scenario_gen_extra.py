#!/usr/bin/env python3
"""Add 30 more SFT training scenarios for Qwen generation.

These are additional scenarios beyond the initial 47. The checkpoint system
will ignore already-completed scenarios and only generate the new ones.

Usage:
    python3 sft_scenario_gen_extra.py
"""
import json
from pathlib import Path

OUTPUT_FILE = Path("/home/waser/Projets/OneOS/src/data/output/sft_xonsh_scenarios.jsonl")

# Load existing scenarios
existing = set()
if OUTPUT_FILE.exists():
    for line in OUTPUT_FILE.read_text().strip().split('\n'):
        if line.strip():
            existing.add(json.loads(line)['id'])

# Generate new scenarios with 'sft_extra_' prefix to ensure uniqueness
extra_scenarios = [
    {"id": "sft_extra_cpu_usage", "category": "cpu", "greeting": "Hey, je voudrais voir l'utilisation CPU en détail", "turns": ["Bonjour ! Prêt à t'aider avec le CPU. Qu'est-ce que tu cherches ?"], "user_query": "Montre-moi les 5 processus qui consomment le plus de CPU", "prompt_hint": "top ou ps pour cpu"},
    {"id": "sft_extra_swap", "category": "memory", "greeting": "Salut ! J'ai un doute sur la mémoire", "turns": ["Pas de souci, dis-moi !"], "user_query": "Combien de swap est utilisé sur le système ?", "prompt_hint": "free -m ou cat /proc/meminfo"},
    {"id": "sft_extra_disk_io", "category": "disk", "greeting": "Coucou, je suis perdu dans les disques", "turns": ["C'est normal, les disques c'est compliqué !"], "user_query": "Quels sont les disques montés et leur point de montage ?", "prompt_hint": "mount ou df -T"},
    {"id": "sft_extra_log_tail", "category": "logs", "greeting": "Bonjour assistant, j'ai un problème de log", "turns": ["Je suis là, dis-moi tout !"], "user_query": "Affiche les 10 dernières lignes du fichier /var/log/syslog", "prompt_hint": "tail -n 10"},
    {"id": "sft_extra_env_export", "category": "env", "greeting": "Hello ! J'ai besoin de définir une variable", "turns": ["C'est parti !"], "user_query": "Exporte la variable PYTHONPATH=/home/user/lib", "prompt_hint": "export PYTHONPATH=..."},
    {"id": "sft_extra_pipe_sort", "category": "pipe", "greeting": "Salut, je veux trier des données", "turns": ["Avec plaisir !"], "user_query": "Liste les fichiers de /tmp triés par taille décroissante", "prompt_hint": "ls -S /tmp ou ls -lhS"},
    {"id": "sft_extra_user_add", "category": "user", "greeting": "Bonjour, je dois créer un utilisateur", "turns": ["D'accord, comment s'appelle l'utilisateur ?"], "user_query": "Crée l'utilisateur 'developer' avec le groupe 'dev'", "prompt_hint": "useradd"},
    {"id": "sft_extra_crontab", "category": "cron", "greeting": "Hey, comment planifier une tâche ?", "turns": ["Pour planifier, on utilise crontab. Qu'est-ce que tu veux faire ?"], "user_query": "Affiche les tâches cron de l'utilisateur courant", "prompt_hint": "crontab -l"},
    {"id": "sft_extra_which_cmd", "category": "find", "greeting": "Salut, où est installé ce programme ?", "turns": ["Je vais chercher ça pour toi !"], "user_query": "Où se trouve l'exécutable python3 ?", "prompt_hint": "which python3"},
    {"id": "sft_extra_man_page", "category": "man", "greeting": "Bonjour, je ne sais pas utiliser cette commande", "turns": ["Pas de panique, on va regarder la doc !"], "user_query": "Affiche le manuel de la commande grep", "prompt_hint": "man grep"},
    {"id": "sft_extra_history", "category": "history", "greeting": "Hey, qu'est-ce que j'ai fait récemment ?", "turns": ["On va regarder ton historique !"], "user_query": "Affiche les 20 dernières commandes exécutées", "prompt_hint": "history 20"},
    {"id": "sft_extra_cwd", "category": "cd", "greeting": "Salut, où suis-je ?", "turns": ["On va vérifier !"], "user_query": "Va dans le dossier /etc/nginx puis affiche le chemin", "prompt_hint": "cd /etc/nginx && pwd"},
    {"id": "sft_extra_touch", "category": "file", "greeting": "Bonjour, je dois créer un fichier vide", "turns": ["C'est fait !"], "user_query": "Crée un fichier vide appelé 'test.txt' dans /tmp", "prompt_hint": "touch /tmp/test.txt"},
    {"id": "sft_extra_rm_recursive", "category": "rm", "greeting": "Coucou, je veux supprimer un dossier", "turns": ["Attention, ça c'est destructif !"], "user_query": "Supprime récursivement le dossier /tmp/old_data", "prompt_hint": "rm -rf /tmp/old_data"},
    {"id": "sft_extra_mv_rename", "category": "mv", "greeting": "Hello, je dois renommer un fichier", "turns": ["Avec plaisir !"], "user_query": "Renomme 'document.txt' en 'document_final.txt'", "prompt_hint": "mv document.txt document_final.txt"},
    {"id": "sft_extra_cp_recursive", "category": "cp", "greeting": "Salut, comment copier un dossier complet ?", "turns": ["On utilise cp -r pour ça !"], "user_query": "Copie le dossier /home/data dans /backup/data", "prompt_hint": "cp -r"},
    {"id": "sft_extra_link_symlink", "category": "ln", "greeting": "Bonjour, qu'est-ce qu'un lien symbolique ?", "turns": ["C'est comme un raccourci ! On en crée un ?"], "user_query": "Crée un lien symbolique de /usr/bin/python3 vers /usr/local/bin/python", "prompt_hint": "ln -s"},
    {"id": "sft_extra_chmod_recursive", "category": "chmod", "greeting": "Hey, comment rendre un script exécutable ?", "turns": ["C'est facile, on utilise chmod !"], "user_query": "Rend le script /home/user/myscript.sh exécutable", "prompt_hint": "chmod +x"},
    {"id": "sft_extra_grep_recursive", "category": "grep", "greeting": "Salut, je dois chercher dans tous les fichiers", "turns": ["On va chercher partout !"], "user_query": "Cherche le texte 'ERROR' dans tous les fichiers .log de /var/log", "prompt_hint": "grep -r ERROR /var/log/*.log"},
    {"id": "sft_extra_find_name", "category": "find", "greeting": "Bonjour, comment trouver un fichier par son nom ?", "turns": ["On utilise la commande find !"], "user_query": "Trouve tous les fichiers .py dans /home/user", "prompt_hint": "find /home/user -name '*.py'"},
    {"id": "sft_extra_diff", "category": "diff", "greeting": "Coucou, comment comparer 2 fichiers ?", "turns": ["On utilise diff !"], "user_query": "Compare les fichiers config_old.json et config_new.json", "prompt_hint": "diff config_old.json config_new.json"},
    {"id": "sft_extra_wc", "category": "wc", "greeting": "Hello, combien de lignes a ce fichier ?", "turns": ["On compte pour toi !"], "user_query": "Compte le nombre de lignes, mots et caractères de README.md", "prompt_hint": "wc -l -w -c README.md"},
    {"id": "sft_extra_xargs", "category": "pipe", "greeting": "Salut, comment passer des arguments à une commande ?", "turns": ["On utilise xargs pour ça !"], "user_query": "Supprime tous les fichiers .tmp dans /tmp en utilisant ls et xargs", "prompt_hint": "ls /tmp/*.tmp | xargs rm"},
    {"id": "sft_extra_redirection", "category": "redirect", "greeting": "Bonjour, comment rediriger la sortie ?", "turns": ["On peut rediriger vers un fichier !"], "user_query": "Affiche la date et redirige le résultat dans /tmp/date.txt", "prompt_hint": "date > /tmp/date.txt"},
    {"id": "sft_extra_append", "category": "redirect", "greeting": "Hey, comment ajouter du texte à la fin d'un fichier ?", "turns": ["On utilise >> pour ajouter !"], "user_query": "Ajoute la ligne 'export PATH=$PATH:/usr/local/bin' à .bashrc", "prompt_hint": "echo ... >> .bashrc"},
    {"id": "sft_extra_curl", "category": "network", "greeting": "Salut, comment faire une requête HTTP ?", "turns": ["On utilise curl !"], "user_query": "Fais une requête GET sur https://httpbin.org/get", "prompt_hint": "curl https://httpbin.org/get"},
    {"id": "sft_extra_wget", "category": "network", "greeting": "Coucou, comment télécharger un fichier ?", "turns": ["Avec wget !"], "user_query": "Télécharge le fichier https://example.com/data.csv dans /tmp", "prompt_hint": "wget -O /tmp/data.csv https://example.com/data.csv"},
    {"id": "sft_extra_systemctl", "category": "service", "greeting": "Bonjour, comment gérer un service ?", "turns": ["On utilise systemctl !"], "user_query": "Affiche le statut du service sshd", "prompt_hint": "systemctl status sshd"},
    {"id": "sft_extra_journal", "category": "logs", "greeting": "Hello, comment voir les logs du système ?", "turns": ["On utilise journalctl !"], "user_query": "Affiche les logs du kernel depuis le démarrage", "prompt_hint": "journalctl -k -b"},
    {"id": "sft_extra_xonsh_help", "category": "xonsh", "greeting": "Salut, comment avoir de l'aide sur xonsh ?", "turns": ["On peut utiliser la built-in help !"], "user_query": "Affiche l'aide sur les alias dans xonsh", "prompt_hint": "help('aliases')"},
]

# Write to a separate file
extra_file = Path("/home/waser/Projets/OneOS/src/data/output/sft_xonsh_scenarios_extra.jsonl")
with open(extra_file, 'w') as f:
    for scenario in extra_scenarios:
        f.write(json.dumps(scenario, ensure_ascii=False) + '\n')

print(f"Generated {len(extra_scenarios)} extra scenarios")
print(f"Saved to: {extra_file}")
print("\nIDs:", [s['id'] for s in extra_scenarios])
