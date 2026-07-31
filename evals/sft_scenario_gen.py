#!/usr/bin/env python3
"""Generate SFT training scenarios for xonsh assistant.

IMPORTANT: These scenarios must be DISTINCT from eval scenarios to avoid
data contamination. The SFT dataset trains the model to respond in French
from Turn 1, while the eval tests generalization on unseen scenarios.

Usage:
    python3 sft_scenario_gen.py
"""
import json
from pathlib import Path

OUTPUT_DIR = Path("/home/waser/Projets/OneOS/src/data/output")

# ── These scenarios are NOT in eval/ ──────────────────────────────────
# They cover similar xonsh concepts but with different phrasing/topics

SFT_SCENARIOS = [
    # System info / environment
    {
        "id": "sft_pwd_location",
        "turns": ["Assistant?", "dis-moi quel dossier on utilise en ce moment"],
        "category": "pwd"
    },
    {
        "id": "sft_hostname_check",
        "turns": ["Assistant?", "montre-moi le nom de cette machine"],
        "category": "hostname"
    },
    {
        "id": "sft_python_version",
        "turns": ["Assistant?", "quelle version de python on a ici"],
        "category": "python"
    },
    
    # File operations
    {
        "id": "sft_read_config",
        "turns": ["Assistant?", "lis-moi le fichier .bashrc"],
        "category": "cat"
    },
    {
        "id": "sft_create_temp",
        "turns": ["Assistant?", "écris salut dans un fichier temporaire"],
        "category": "echo"
    },
    {
        "id": "sft_list_py_files",
        "turns": ["Assistant?", "montre-moi tous les scripts python du dossier"],
        "category": "find"
    },
    {
        "id": "sft_count_lines",
        "turns": ["Assistant?", "combien de lignes y a-t-il dans ce readme"],
        "category": "wc"
    },
    
    # Process management
    {
        "id": "sft_running_procs",
        "turns": ["Assistant?", "quels processus tournent en ce moment"],
        "category": "ps"
    },
    {
        "id": "sft_kill_something",
        "turns": ["Assistant?", "arrête le processus qui prend le plus de cpu"],
        "category": "kill"
    },
    {
        "id": "sft_memory_top",
        "turns": ["Assistant?", "les 5 processus qui mangent le plus de ram"],
        "category": "top"
    },
    
    # Network
    {
        "id": "sft_ip_address",
        "turns": ["Assistant?", "donne-moi l'adresse IP de la machine"],
        "category": "ip"
    },
    {
        "id": "sft_dns_lookup",
        "turns": ["Assistant?", "résous google.fr pour voir l'IP"],
        "category": "dig"
    },
    {
        "id": "sft_network_interfaces",
        "turns": ["Assistant?", "quelles interfaces réseau sont actives"],
        "category": "ip"
    },
    
    # Math / computation
    {
        "id": "sft_factorial",
        "turns": ["Assistant?", "calcule 7 factorielle"],
        "category": "python"
    },
    {
        "id": "sft_square_root",
        "turns": ["Assistant?", "racine carrée de 144"],
        "category": "python"
    },
    {
        "id": "sft_random_number",
        "turns": ["Assistant?", "génère un nombre aléatoire entre 1 et 100"],
        "category": "python"
    },
    
    # Text manipulation
    {
        "id": "sft_reverse_string",
        "turns": ["Assistant?", "inverse le mot 'ordinateur'"],
        "category": "python"
    },
    {
        "id": "sft_count_words",
        "turns": ["Assistant?", "combien de mots dans cette phrase: la vie est belle"],
        "category": "python"
    },
    {
        "id": "sft_uppercase",
        "turns": ["Assistant?", "met en majuscules: bonjour le monde"],
        "category": "python"
    },
    
    # File navigation
    {
        "id": "sft_home_contents",
        "turns": ["Assistant?", "qu'est-ce qu'il y a dans mon dossier personnel"],
        "category": "ls"
    },
    {
        "id": "sft_list_hidden",
        "turns": ["Assistant?", "affiche les fichiers cachés du dossier"],
        "category": "ls"
    },
    {
        "id": "sft_tree_structure",
        "turns": ["Assistant?", "montre-moi la structure des dossiers en arbre"],
        "category": "tree"
    },
    
    # Time / date
    {
        "id": "sft_current_time",
        "turns": ["Assistant?", "quelle heure est-il précisément"],
        "category": "date"
    },
    {
        "id": "sft_unix_timestamp",
        "turns": ["Assistant?", "donne-moi le timestamp unix"],
        "category": "date"
    },
    
    # Package / software
    {
        "id": "sft_installed_packages",
        "turns": ["Assistant?", "liste les packages pip installés"],
        "category": "pip"
    },
    {
        "id": "sft_disk_space",
        "turns": ["Assistant?", "combien d'espace libre il reste sur le disque"],
        "category": "df"
    },
    {
        "id": "sft_check_update",
        "turns": ["Assistant?", "est-ce qu'il y a des mises à jour système"],
        "category": "apt"
    },
    
    # Shell features
    {
        "id": "sft_env_filter",
        "turns": ["Assistant?", "filtre les variables qui contiennent PATH"],
        "category": "env"
    },
    {
        "id": "sft_set_alias",
        "turns": ["Assistant?", "crée un alias ll pour ls -la"],
        "category": "alias"
    },
    {
        "id": "sft_list_aliases",
        "turns": ["Assistant?", "montre-moi tous les alias actifs"],
        "category": "alias"
    },
    
    # System monitoring
    {
        "id": "sft_cpu_count",
        "turns": ["Assistant?", "combien de coeurs CPU on a"],
        "category": "nproc"
    },
    {
        "id": "sft_uptime",
        "turns": ["Assistant?", "depuis combien de temps la machine tourne"],
        "category": "uptime"
    },
    {
        "id": "sft_last_reboot",
        "turns": ["Assistant?", "quand a-t-on démarré la dernière fois"],
        "category": "uptime"
    },
    
    # Python in shell
    {
        "id": "sft_json_parse",
        "turns": ["Assistant?", "analyse ce JSON et extrais la clé name"],
        "category": "python"
    },
    {
        "id": "sft_sort_numbers",
        "turns": ["Assistant?", "trie ces nombres dans l'ordre: 42,7,99,1,23"],
        "category": "python"
    },
    {
        "id": "sft_find_max",
        "turns": ["Assistant?", "trouve le plus grand nombre de cette liste: [3,17,42,8]"],
        "category": "python"
    },
    
    # File permissions
    {
        "id": "sft_make_executable",
        "turns": ["Assistant?", "rend le script executable"],
        "category": "chmod"
    },
    {
        "id": "sft_change_owner",
        "turns": ["Assistant?", "change le propriétaire du fichier"],
        "category": "chown"
    },
    
    # Archive operations
    {
        "id": "sft_compress",
        "turns": ["Assistant?", "archive le dossier dans un fichier zip"],
        "category": "zip"
    },
    {
        "id": "sft_list_archive",
        "turns": ["Assistant?", "montre le contenu de l'archive tar.gz"],
        "category": "tar"
    },
    
    # Git operations
    {
        "id": "sft_git_status",
        "turns": ["Assistant?", "quel est l'état du dépôt git"],
        "category": "git"
    },
    {
        "id": "sft_git_log",
        "turns": ["Assistant?", "affiche les 5 derniers commits"],
        "category": "git"
    },
    
    # User info
    {
        "id": "sft_whoami",
        "turns": ["Assistant?", "qui suis-je sur cette machine"],
        "category": "whoami"
    },
    {
        "id": "sft_groups",
        "turns": ["Assistant?", "dans quels groupes je suis"],
        "category": "groups"
    },
    
    # Output manipulation
    {
        "id": "sft_tail_file",
        "turns": ["Assistant?", "les 20 dernières lignes du journal"],
        "category": "tail"
    },
    {
        "id": "sft_head_file",
        "turns": ["Assistant?", "les 10 premières lignes du fichier"],
        "category": "head"
    },
    {
        "id": "sft_grep_pattern",
        "turns": ["Assistant?", "cherche les lignes avec error dans le log"],
        "category": "grep"
    },
]

def main():
    output_file = OUTPUT_DIR / "sft_xonsh_scenarios.jsonl"
    
    with open(output_file, 'w') as f:
        for scenario in SFT_SCENARIOS:
            f.write(json.dumps(scenario, ensure_ascii=False) + '\n')
    
    print(f"Generated {len(SFT_SCENARIOS)} SFT scenarios")
    print(f"Saved to: {output_file}")
    
    # Print categories
    categories = {}
    for s in SFT_SCENARIOS:
        categories.setdefault(s["category"], []).append(s["id"])
    
    print(f"\nCategories ({len(categories)}):")
    for cat, ids in sorted(categories.items()):
        print(f"  {cat}: {len(ids)} scenarios")

if __name__ == "__main__":
    main()
