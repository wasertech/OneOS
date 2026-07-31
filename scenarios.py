"""
Scenario definitions for the User Simulator.

Each scenario is a multi-turn conversation template that simulates realistic
user interactions with Assistant in a shared xonsh session on Destinée:

  Host: Linux Destinee 7.0.13-1-MANJARO x86_64
  CPU: AMD Ryzen Threadripper 2920X (24 threads) @ 3.5GHz
  GPU: 2x NVIDIA TITAN RTX (24 Go VRAM each)
  RAM: 96 Go DDR4
  Disk: NVMe ~733 Go
  User: waser, Home: /home/waser, Projets: /home/waser/Projets
  Langue: fr_CH.UTF-8, Shell: xonsh (via Assistant)
  Python: 3.11.14

The key insight: variables, imports, and file state persist across turns within
a scenario. This is what makes these traces valuable — they demonstrate how an
agent navigates a live shared environment with accumulated state.

Target: ~1000 turns total across all categories.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Turn:
    """A single turn in a scenario - the user's prompt seed."""
    prompt: str
    # Whether this turn is expected to trigger tool calls (xonsh, web_search, etc.)
    expects_tools: bool = True
    # Subcategory tag for fine-grained analytics
    subcategory: Optional[str] = None


@dataclass
class Scenario:
    """A multi-turn conversation scenario with shared state."""
    name: str
    category: str
    turns: list[Turn] = field(default_factory=list)
    description: str = ""
    # Reset xonsh session state before running this scenario
    reset_state: bool = True


# ============================================================================
# DATA SCIENCE (~150 turns target)
# Real datasets, real libraries installed on Destinée, real paths
# ============================================================================

def ds_pandas_csv_exploration() -> Scenario:
    return Scenario(
        name="ds_pandas_csv",
        category="data_science",
        description="Full EDA workflow on a CSV dataset with persistent DataFrame state",
        turns=[
            Turn("import pandas as pd et charge https://raw.githubusercontent.com/vincentdchan/bike-sharing-dataset/master/hour.csv dans df"),
            Turn("montre les 5 premières lignes de df avec df.head()"),
            Turn("donne moi df.info() - types de colonnes et valeurs manquantes"),
            Turn("y a-t-il des valeurs manquantes ? Si oui combien par colonne ?"),
            Turn("calcule la moyenne du nombre de locataires (count) par heure de la journée avec un groupby sur 'hr'"),
            Turn("fais un groupby sur la saison et donne les stats descriptives de count"),
            Turn("quelle est la corrélation entre temperature et le nombre de locations ?"),
            Turn("filtre df pour ne garder que les jours avec temp > 0.4 et stocke dans df_filtered"),
        ],
    )


def ds_numpy_matrix_ops() -> Scenario:
    return Scenario(
        name="ds_numpy_matrices",
        category="data_science",
        description="Matrix operations and statistical analysis with persistent numpy state",
        turns=[
            Turn("import numpy as np et crée une matrice 10x10 de nombres aléatoires entre 0 et 1 dans 'mat'"),
            Turn("calcule la moyenne, médiane et écart-type de mat"),
            Turn("trouve les 5 plus grandes valeurs de mat et leurs indices avec np.argpartition"),
            Turn("normalise mat pour avoir une moyenne de 0 et un écart-type de 1, stocke dans 'mat_norm'"),
            Turn("calcule le produit matriciel de mat_norm avec sa transposée"),
            Turn("donne les valeurs propres de ce produit matriciel avec np.linalg.eigvals"),
        ],
    )


def ds_sklearn_classification() -> Scenario:
    return Scenario(
        name="ds_sklearn_ml",
        category="data_science",
        description="Full ML workflow: load → split → train → evaluate on Destinée's GPUs",
        turns=[
            Turn("import sklearn.datasets et charge le dataset wine, stocke X et y"),
            Turn("split en train/test avec 80/20, random_state=42"),
            Turn("entraîne un Random Forest classifier sur les données d'entraînement"),
            Turn("donne la précision, recall et F1 score sur le test set avec classification_report"),
            Turn("affiche l'importance des features du modèle"),
        ],
    )


def ds_time_series() -> Scenario:
    return Scenario(
        name="ds_timeseries",
        category="data_science",
        description="Time series analysis with date parsing, rolling stats on local data",
        turns=[
            Turn("crée un DataFrame avec 365 jours de données aléatoires : date (début 2026-01-01), temperature (moyenne 20°C écart-type 8), humidity (moyenne 60%)"),
            Turn("parse la colonne date en datetime et fais-en l'index du DataFrame"),
            Turn("calcule une moyenne mobile sur 7 jours pour la température avec rolling(7).mean()"),
            Turn("fais un plot de la température brute vs la moyenne mobile avec matplotlib"),
            Turn("quelle est la semaine avec la température maximale ?"),
        ],
    )


def ds_data_generation() -> Scenario:
    return Scenario(
        name="ds_synthetic_data",
        category="data_science",
        description="Generate synthetic datasets for testing ML pipelines",
        turns=[
            Turn("génère un dataset synthétique avec 1000 échantillons, 5 features gaussiennes et un label binaire"),
            Turn("ajoute du bruit à 2 des features pour simuler du data drift"),
            Turn("sépare en train/val/test 70/15/15 et sauvegarde chaque split dans /tmp/data/"),
        ],
    )


def ds_pandas_groupby_aggregation() -> Scenario:
    return Scenario(
        name="ds_groupby_agg",
        category="data_science",
        description="Complex groupby aggregations on a real dataset",
        turns=[
            Turn("charge le dataset tips de seaborn et stocke dans df"),
            Turn("calcule la moyenne et médiane du pourboire par jour de la semaine et par genre du serveur"),
            Turn("quelle est la combinaison jour/serveur avec le plus gros pourboire moyen ?"),
            Turn("fais un pivot table avec day en index, sex en colonnes et total_bill en valeurs (moyenne)"),
        ],
    )


def ds_numpy_image_processing() -> Scenario:
    return Scenario(
        name="ds_numpy_images",
        category="data_science",
        description="Basic image processing with numpy arrays",
        turns=[
            Turn("crée une image 256x256 avec un dégradé de gris horizontal en numpy"),
            Turn("ajoute du bruit gaussien à cette image avec sigma=30"),
            Turn("applique un filtre de lissage (moyenne mobile) sur l'image bruitée"),
            Turn("compare les histogrammes de l'image originale et celle après filtrage"),
        ],
    )


def ds_pandas_merge_join() -> Scenario:
    return Scenario(
        name="ds_merge_join",
        category="data_science",
        description="Merge multiple DataFrames, handle missing data",
        turns=[
            Turn("crée deux DataFrames : clients (id, nom, ville) et commandes (client_id, montant, date)"),
            Turn("fais un merge left join sur client_id et affiche le résultat"),
            Turn("calcule le total des commandes par ville"),
            Turn("filtre pour ne garder que les villes avec plus de 1000€ de commandes totales"),
        ],
    )


def ds_sklearn_regression() -> Scenario:
    return Scenario(
        name="ds_sklearn_reg",
        category="data_science",
        description="Regression analysis with sklearn on Boston-style data",
        turns=[
            Turn("charge le dataset california housing de sklearn et explore les features"),
            Turn("split en train/test 80/20, entraîne un GradientBoostingRegressor"),
            Turn("donne le R² score et le RMSE sur le test set"),
            Turn("essaie un Ridge regression pour comparer - lequel est meilleur ?"),
        ],
    )


def ds_pandas_datetime_ops() -> Scenario:
    return Scenario(
        name="ds_datetime",
        category="data_science",
        description="Date/time manipulation with pandas",
        turns=[
            Turn("crée un DataFrame avec des timestamps aléatoires sur l'année 2026 et une valeur numérique associée"),
            Turn("extrait le mois, le jour de la semaine et l'heure depuis les timestamps"),
            Turn("regroupe par mois et calcule la somme des valeurs"),
            Turn("fais un resample hebdomadaire avec moyenne et écart-type"),
        ],
    )


def ds_statistical_tests() -> Scenario:
    return Scenario(
        name="ds_stats_tests",
        category="data_science",
        description="Statistical hypothesis testing with scipy",
        turns=[
            Turn("génère deux échantillons de 100 valeurs chacun : un normal N(50, 10) et un N(52, 10)"),
            Turn("fais un test t de Student pour vérifier si les moyennes sont significativement différentes"),
            Turn("calcule la puissance du test avec une simulation Monte Carlo (1000 itérations)"),
        ],
    )


# ============================================================================
# NATURAL CONVERSATION (~120 turns target)
# French language, Swiss context, references to Destinée's actual setup
# ============================================================================

def conv_ai_philosophy() -> Scenario:
    return Scenario(
        name="conv_ai_consciousness",
        category="natural_conversation",
        description="Philosophical discussion about AI consciousness in French",
        turns=[
            Turn("Qu'est-ce que tu penses de l'idée qu'une IA puisse être consciente ?"),
            Turn("Et si on te disait que la conscience c'est juste un pattern d'information complexe ?"),
            Turn("Mais comment distinguer une vraie compréhension d'une simulation parfaite ?"),
            Turn("Est-ce que le test de Turing est encore pertinent aujourd'hui avec les LLMs comme toi ?"),
        ],
    )


def conv_tech_explanation() -> Scenario:
    return Scenario(
        name="conv_backprop",
        category="natural_conversation",
        description="Explaining backpropagation with concrete examples",
        turns=[
            Turn("explique moi comment fonctionne la backpropagation dans un réseau de neurones"),
            Turn("peux-tu me donner un exemple concret avec des chiffres simples ?"),
            Turn("et quelle est la différence entre gradient descent et stochastic gradient descent ?"),
            Turn("quand est-ce qu'on préfère Adam à SGD vanilla pour l'entraînement ?"),
        ],
    )


def conv_project_ideation() -> Scenario:
    return Scenario(
        name="conv_sleep_tracker",
        category="natural_conversation",
        description="Brainstorming a health data analysis project",
        turns=[
            Turn("je veux créer un outil pour analyser les habitudes de sommeil à partir des données Apple Health. Donne moi 5 idées de features intéressantes"),
            Turn("la feature sur la corrélation sommeil/productivité me plaît - comment on pourrait l'implémenter techniquement ?"),
            Turn("quelles librairies Python tu recommanderais pour ce genre d'analyse temporelle ?"),
        ],
    )


def conv_french_language() -> Scenario:
    return Scenario(
        name="conv_english_help",
        category="natural_conversation",
        description="Language practice - correcting English for a French speaker",
        turns=[
            Turn("aide-moi à améliorer mon anglais - corrige cette phrase: 'I have 25 years and I work since 3 years in IT'"),
            Turn("explique la différence entre present perfect et past simple avec des exemples"),
            Turn("traduis en français : 'The early bird catches the worm' et explique le sens figuré"),
        ],
    )


def conv_system_discussion() -> Scenario:
    return Scenario(
        name="conv_destinee_setup",
        category="natural_conversation",
        description="Discussing Destinée's hardware setup and capabilities",
        turns=[
            Turn("quel est le matériel de cette machine ?"),
            Turn("avec 2x TITAN RTX et 96 Go de RAM, qu'est-ce qu'on pourrait entraîner localement ?"),
            Turn("est-ce que c'est viable de faire du fine-tuning LoRA sur un modèle 70B avec ce setup ?"),
        ],
    )


def conv_career_advice() -> Scenario:
    return Scenario(
        name="conv_career",
        category="natural_conversation",
        description="Career discussion in AI/ML field",
        turns=[
            Turn("je suis développeur full-stack et je veux passer en ML engineering - par où commencer ?"),
            Turn("quelles compétences techniques sont les plus demandées pour un ML engineer en 2026 ?"),
            Turn("est-ce que le fine-tuning de LLMs est une bonne spécialisation ou c'est trop niche ?"),
        ],
    )


def conv_cooking() -> Scenario:
    return Scenario(
        name="conv_recipes",
        category="natural_conversation",
        description="Casual cooking discussion - no tools needed",
        turns=[
            Turn("donne moi une recette de fondue vaudoise authentique pour 4 personnes"),
            Turn("quel fromage utiliser si je ne trouve pas de Gruyère ?"),
            Turn("et comment faire pour que la fondue ne colle pas au fond ?"),
        ],
    )


def conv_music() -> Scenario:
    return Scenario(
        name="conv_music_taste",
        category="natural_conversation",
        description="Music discussion and recommendations",
        turns=[
            Turn("je cherche de la musique pour coder - tu connais des playlists lo-fi ou ambient ?"),
            Turn("qu'est-ce que tu penses du genre vaporwave comme fond sonore pour travailler ?"),
        ],
    )


def conv_travel() -> Scenario:
    return Scenario(
        name="conv_swiss_travel",
        category="natural_conversation",
        description="Travel planning discussion for Switzerland",
        turns=[
            Turn("je veux faire une randonnée de 3 jours dans les Alpes suisses en été - des suggestions ?"),
            Turn("quelle région est la moins fréquentée mais avec de beaux paysages ?"),
            Turn("combien ça coûte environ pour 3 jours en refuge ?"),
        ],
    )


def conv_book_club() -> Scenario:
    return Scenario(
        name="conv_books",
        category="natural_conversation",
        description="Book recommendations and literary discussion",
        turns=[
            Turn("recommande moi 3 livres sur l'histoire de l'informatique et de l'IA"),
            Turn("lequel de ces livres est le plus accessible pour quelqu'un qui n'est pas technicien ?"),
        ],
    )


def conv_math_help() -> Scenario:
    return Scenario(
        name="conv_math",
        category="natural_conversation",
        description="Math help - explaining concepts step by step",
        turns=[
            Turn("explique moi le théorème de Bayes avec un exemple concret"),
            Turn("comment on l'utilise dans les filtres anti-spam ?"),
            Turn("peux-tu me donner un exercice pratique pour m'entraîner ?"),
        ],
    )


def conv_startup() -> Scenario:
    return Scenario(
        name="conv_startup_ideas",
        category="natural_conversation",
        description="Startup ideation and business model discussion",
        turns=[
            Turn("donne moi 3 idées de startup SaaS qui pourraient marcher en Suisse"),
            Turn("l'idée d'outil de conformité RGPD automatisé me plaît - quel serait le MVP ?"),
            Turn("comment valider ce marché avant de développer ?"),
        ],
    )


# ============================================================================
# DEBUGGING (~100 turns target)
# Real errors, real tracebacks, iterative fixing in shared session
# ============================================================================

def dbg_factorial() -> Scenario:
    return Scenario(
        name="dbg_factorial",
        category="debugging",
        description="Write buggy factorial function, debug iteratively",
        turns=[
            Turn("écris une fonction python qui calcule la factorielle d'un nombre et stocke-la dans une variable fact"),
            Turn("essaie de l'appeler avec fact(5) - si ça plante, analyse l'erreur"),
            Turn("ajoute un cas pour les nombres négatifs et les non-entiers avec des exceptions appropriées"),
            Turn("refactorise en version itérative au lieu de récursive et compare les performances"),
        ],
    )


def dbg_csv_parsing() -> Scenario:
    return Scenario(
        name="dbg_csv_parse",
        category="debugging",
        description="Debug CSV file reading with encoding and parsing issues",
        turns=[
            Turn("crée un fichier /tmp/test_data.csv avec 10 lignes de données : nom, age, ville"),
            Turn("écris une fonction qui lit ce CSV et retourne la moyenne d'âge par ville"),
            Turn("essaie d'exécuter - si erreur, corrige le problème"),
            Turn("ajoute du logging pour tracer les erreurs de parsing avec le module logging"),
        ],
    )


def dbg_import_error() -> Scenario:
    return Scenario(
        name="dbg_missing_import",
        category="debugging",
        description="Debug ImportError - missing package, install it, verify",
        turns=[
            Turn("essaie d'importer seaborn - si ça plante, installe-le et réessaye"),
            Turn("utilise seaborn pour faire un pairplot du dataset iris de sklearn"),
        ],
    )


def dbg_json_parsing() -> Scenario:
    return Scenario(
        name="dbg_json_parse",
        category="debugging",
        description="Debug JSON parsing with nested structures and type errors",
        turns=[
            Turn("crée un fichier /tmp/users.json avec une liste de 5 utilisateurs (nom, age, hobbies[])"),
            Turn("écris une fonction qui charge ce JSON et retourne tous les hobbies uniques"),
            Turn("essaie d'exécuter - si erreur, corrige le problème"),
        ],
    )


def dbg_regex() -> Scenario:
    return Scenario(
        name="dbg_regex",
        category="debugging",
        description="Debug regex patterns for text extraction",
        turns=[
            Turn("écris une expression régulière pour extraire les emails d'un texte"),
            Turn("teste sur ce texte : 'Contactez jean@test.com ou Marie_Dupont@exemple.fr pour infos'"),
            Turn("ajoute aussi la détection de numéros de téléphone au format suisse +41 XX XXX XX XX"),
        ],
    )


def dbg_async() -> Scenario:
    return Scenario(
        name="dbg_asyncio",
        category="debugging",
        description="Debug async/await code with common pitfalls",
        turns=[
            Turn("écris une fonction async qui fait 3 requêtes HTTP en parallèle vers http://localhost:1234/v1/models"),
            Turn("essaie d'exécuter avec asyncio.run() - si erreur, corrige le problème"),
            Turn("ajoute un timeout de 5 secondes par requête et du retry sur erreur"),
        ],
    )


def dbg_type_errors() -> Scenario:
    return Scenario(
        name="dbg_types",
        category="debugging",
        description="Debug type errors in Python - mixing str/int, None handling",
        turns=[
            Turn("écris une fonction qui prend une liste de chaînes et retourne la longueur moyenne des mots"),
            Turn("essaie avec ['hello', 'world', 'test'] puis avec une liste vide - gère les edge cases"),
            Turn("ajoute des type hints et vérifie avec un assert que le résultat est bien un float"),
        ],
    )


def dbg_file_permissions() -> Scenario:
    return Scenario(
        name="dbg_perms",
        category="debugging",
        description="Debug file permission issues on Linux",
        turns=[
            Turn("crée un fichier /tmp/test_perm.txt et essaie de le rendre lisible uniquement par l'utilisateur"),
            Turn("vérifie les permissions avec os.stat() en Python"),
            Turn("essaie d'écrire dedans depuis un autre contexte - gère l'exception PermissionError"),
        ],
    )


# ============================================================================
# GIT WORKFLOW (~80 turns target)
# Real repos on Destinée: /home/waser/Projets/
# ============================================================================

def git_projets_status() -> Scenario:
    return Scenario(
        name="git_projets_check",
        category="git_workflow",
        description="Check git status of projects in /home/waser/Projets/",
        turns=[
            Turn("va dans /home/waser/Projets/OneOS et check le status git"),
            Turn("montre les 5 derniers commits avec un message court"),
            Turn("quel est le diff non commité si il y en a ?"),
        ],
    )


def git_branch_workflow() -> Scenario:
    return Scenario(
        name="git_feature_branch",
        category="git_workflow",
        description="Create feature branch, make changes, check status",
        turns=[
            Turn("dans /home/waser/Projets/OneOS liste les branches locales et distantes"),
            Turn("quel est le dernier commit sur la branche principale ?"),
            Turn("montre l'historique des commits avec git log --oneline -10"),
        ],
    )


def git_diff_analysis() -> Scenario:
    return Scenario(
        name="git_diff",
        category="git_workflow",
        description="Analyze diffs between commits and branches",
        turns=[
            Turn("dans /home/waser/Projets/OneOS montre le diff du dernier commit"),
            Turn("combien de lignes ont été ajoutées et supprimées ?"),
            Turn("quels fichiers ont été modifiés dans les 3 derniers commits ?"),
        ],
    )


def git_stash_workflow() -> Scenario:
    return Scenario(
        name="git_stash",
        category="git_workflow",
        description="Use git stash to save work in progress",
        turns=[
            Turn("dans /home/waser/Projets/OneOS check s'il y a des modifications non commitées"),
            Turn("si oui, fais un git stash pour les sauvegarder"),
            Turn("vérifie que le working tree est propre maintenant"),
        ],
    )


def git_log_stats() -> Scenario:
    return Scenario(
        name="git_stats",
        category="git_workflow",
        description="Git contribution statistics and history analysis",
        turns=[
            Turn("dans /home/waser/Projets/OneOS donne les stats de commits par auteur"),
            Turn("quel est le fichier qui a le plus été modifié historiquement ?"),
            Turn("montre l'historique des modifications du fichier config.yaml s'il existe"),
        ],
    )


# ============================================================================
# FILE MANAGEMENT (~80 turns target)
# Real paths on Destinée, persistent filesystem state across turns
# ============================================================================

def fm_project_scaffold() -> Scenario:
    return Scenario(
        name="fm_new_project",
        category="file_management",
        description="Scaffold a new Python project in /home/waser/Projets/",
        turns=[
            Turn("crée une structure de projet Python dans /tmp/myproject avec src/, tests/, docs/ et un README.md"),
            Turn("écris un pyproject.toml basique pour ce projet avec le nom 'myproject' version 0.1.0"),
            Turn("ajoute un .gitignore standard pour Python avec les patterns habituels"),
            Turn("liste la structure complète du projet avec tree ou find"),
        ],
    )


def fm_config_transform() -> Scenario:
    return Scenario(
        name="fm_json_to_yaml",
        category="file_management",
        description="Read JSON config, transform data, write output in different format",
        turns=[
            Turn("crée un fichier /tmp/config.json avec une config : nom='destinee_sim', version=1.0, debug=true"),
            Turn("lis ce fichier JSON et affiche son contenu formaté"),
            Turn("ajoute une section 'hardware' avec gpu='TITAN RTX x2', ram='96Go', cpu='Threadripper 2920X'"),
            Turn("exporte la config en format YAML dans /tmp/config.yaml si pyyaml est dispo, sinon en CSV"),
        ],
    )


def fm_log_analysis() -> Scenario:
    return Scenario(
        name="fm_log_parse",
        category="file_management",
        description="Parse and analyze log files with Python",
        turns=[
            Turn("crée un fichier /tmp/app.log avec 50 lignes de logs simulées (timestamp, level, message)"),
            Turn("écris une fonction qui compte le nombre d'erreurs par heure dans ce fichier de log"),
            Turn("filtre pour ne garder que les lignes ERROR et CRITICAL"),
        ],
    )


def fm_directory_audit() -> Scenario:
    return Scenario(
        name="fm_dir_audit",
        category="file_management",
        description="Audit directory structure, find large files, duplicates",
        turns=[
            Turn("liste les fichiers dans /home/waser/Projets/OneOS/src avec leur taille"),
            Turn("trouve les 10 plus gros fichiers dans /home/waser/Projets/"),
            Turn("calcule la taille totale occupée par tous les fichiers .py dans Projets/"),
        ],
    )


def fm_backup_script() -> Scenario:
    return Scenario(
        name="fm_backup",
        category="file_management",
        description="Create a backup script with tar and compression",
        turns=[
            Turn("écris un script Python qui fait une archive tar.gz de /tmp/myproject si le dossier existe"),
            Turn("ajoute une option pour exclure les dossiers __pycache__ et .git"),
            Turn("teste l'exécution et vérifie que l'archive a été créée"),
        ],
    )


# ============================================================================
# SYSTEM MONITORING (~60 turns target)
# Real hardware: Threadripper, 2x TITAN RTX, 96 Go RAM, NVMe
# ============================================================================

def sysmon_resources() -> Scenario:
    return Scenario(
        name="sysmon_cpu_ram",
        category="system_monitoring",
        description="Check CPU and RAM usage on Destinée's Threadripper + 96Go setup",
        turns=[
            Turn("montre moi l'utilisation CPU et RAM actuelle avec les commandes système"),
            Turn("quels sont les 10 processus qui consomment le plus de mémoire ?"),
            Turn("combien d'espace disque reste-t-il sur /home/waser ?"),
            Turn("donne moi un résumé système : uptime, charge, température GPU si dispo"),
        ],
    )


def sysmon_gpu() -> Scenario:
    return Scenario(
        name="sysmon_gpu_status",
        category="system_monitoring",
        description="Monitor GPU status on Destinée's dual TITAN RTX setup",
        turns=[
            Turn("check le statut des GPUs avec nvidia-smi - utilisation VRAM et température"),
            Turn("quels processus utilisent les GPUs en ce moment ?"),
            Turn("quelle est la consommation électrique totale des GPUs ?"),
        ],
    )


def sysmon_network() -> Scenario:
    return Scenario(
        name="sysmon_net",
        category="system_monitoring",
        description="Check network connectivity and active connections",
        turns=[
            Turn("quelles sont les connexions réseau actives avec ss ou netstat ?"),
            Turn("montre l'adresse IP locale et le hostname de cette machine"),
            Turn("teste la connectivité vers localhost:1234 (LM Studio) avec curl"),
        ],
    )


def sysmon_disk() -> Scenario:
    return Scenario(
        name="sysmon_disk",
        category="system_monitoring",
        description="Disk usage analysis and cleanup recommendations",
        turns=[
            Turn("analyse l'utilisation du disque par partition avec df -h"),
            Turn("trouve les dossiers qui occupent le plus d'espace dans /home/waser/"),
            Turn("donne des recommandations pour libérer de l'espace si nécessaire"),
        ],
    )


def sysmon_processes() -> Scenario:
    return Scenario(
        name="sysmon_procs",
        category="system_monitoring",
        description="Process monitoring and management",
        turns=[
            Turn("liste les processus Python en cours d'exécution avec leur PID et consommation"),
            Turn("y a-t-il des processus qui tournent depuis plus de 7 jours ?"),
            Turn("montre l'arbre des processus (pstree) pour voir les relations parent/enfant"),
        ],
    )


# ============================================================================
# PYTHON SCRIPTING (~70 turns target)
# Functions persist in memory across turns - key differentiator
# ============================================================================

def py_class_design() -> Scenario:
    return Scenario(
        name="py_task_manager",
        category="python_scripting",
        description="Create a Task class, add methods, test incrementally",
        turns=[
            Turn("définis une classe Task avec des attributs: nom (str), priorite (int 1-5), complet (bool False par défaut)"),
            Turn("ajoute une méthode __str__ et crée 3 instances de tâches dans une liste 'tasks'"),
            Turn("ajoute une méthode filter_by_priority(min_prio) à la classe qui retourne les tâches au-dessus d'un seuil"),
            Turn("teste avec [t.__str__() for t in tasks] pour voir le résultat"),
        ],
    )


def py_data_transform() -> Scenario:
    return Scenario(
        name="py_collections",
        category="python_scripting",
        description="Work with dicts, lists, sets for data manipulation",
        turns=[
            Turn("crée un dictionnaire 'contacts' avec 5 entrées : nom -> {email, telephone}"),
            Turn("écris une fonction chercher_par_email(email) qui cherche dans contacts et retourne l'entrée correspondante"),
            Turn("teste la fonction avec un email du dictionnaire et un qui n'existe pas"),
        ],
    )


def py_file_utils() -> Scenario:
    return Scenario(
        name="py_file_helpers",
        category="python_scripting",
        description="Build file utility functions that persist in session",
        turns=[
            Turn("définis une fonction get_file_size(path) qui retourne la taille d'un fichier en Mo"),
            Turn("définis une fonction list_large_files(directory, threshold_mb=100) qui liste les fichiers au-dessus du seuil"),
            Turn("teste avec list_large_files('/home/waser/Projets', 50) pour voir quels projets sont gros"),
        ],
    )


def py_web_scraper() -> Scenario:
    return Scenario(
        name="py_http_client",
        category="python_scripting",
        description="Build a simple HTTP client with retry logic",
        turns=[
            Turn("définis une fonction fetch_json(url) qui fait un GET et retourne le JSON parsé"),
            Turn("ajoute du retry avec exponential backoff (max 3 tentatives, délai initial 1s)"),
            Turn("teste en appelant http://localhost:1234/v1/models"),
        ],
    )


def py_text_processing() -> Scenario:
    return Scenario(
        name="py_nlp_basic",
        category="python_scripting",
        description="Text processing functions - tokenization, stemming, frequency analysis",
        turns=[
            Turn("définis une fonction word_frequency(text) qui retourne un dictionnaire mot->comptage"),
            Turn("teste avec le texte 'la rapidité de la tortue bat la lentezza du lièvre' et affiche les 5 mots les plus fréquents"),
            Turn("ajoute une version qui ignore les stop words français (le, la, les, de, du, des)"),
        ],
    )


def py_config_parser() -> Scenario:
    return Scenario(
        name="py_ini_parser",
        category="python_scripting",
        description="Build a config parser with validation",
        turns=[
            Turn("définis une classe ConfigParser qui lit un fichier INI et retourne les sections comme des dicts"),
            Turn("crée un fichier /tmp/test.ini avec 2 sections [database] et [server]"),
            Turn("teste le parser sur ce fichier et affiche la config parsée"),
        ],
    )


# ============================================================================
# WEB RESEARCH (~50 turns target)
# Uses web_search tool, reads pages, synthesizes findings
# ============================================================================

def web_llm_quantization() -> Scenario:
    return Scenario(
        name="web_quantization",
        category="web_research",
        description="Research LLM quantization methods relevant to Destinée's setup",
        turns=[
            Turn("cherche les dernières avancées en quantization de modèles LLM (GGUF, AWQ, GPTQ)"),
            Turn("résume les différences clés entre GGUF et GPTQ en termes de précision et vitesse d'inférence"),
            Turn("quelle méthode est recommandée pour un modèle 70B sur une seule GPU 24Go comme nos TITAN RTX ?"),
        ],
    )


def web_manjaro_updates() -> Scenario:
    return Scenario(
        name="web_system_info",
        category="web_research",
        description="Research system-related topics on the web",
        turns=[
            Turn("cherche les dernières nouveautés de Manjaro Linux et du noyau Linux 7.x"),
            Turn("quelles sont les améliorations de performance pour le Threadripper sur ce noyau ?"),
        ],
    )


def web_ml_trends() -> Scenario:
    return Scenario(
        name="web_ml_2026",
        category="web_research",
        description="Research current ML trends and breakthroughs",
        turns=[
            Turn("cherche les dernières tendances en machine learning pour 2026"),
            Turn("quels sont les nouveaux modèles open source sortis récemment ?"),
            Turn("résume les avancées majeures en RAG et retrieval-augmented generation"),
        ],
    )


def web_python_updates() -> Scenario:
    return Scenario(
        name="web_python_new",
        category="web_research",
        description="Research Python ecosystem updates",
        turns=[
            Turn("cherche les nouveautés de Python 3.12 et 3.13"),
            Turn("quelles sont les améliorations de performance par rapport à Python 3.11 ?"),
        ],
    )


# ============================================================================
# BUILD/TEST (~40 turns target)
# Real venv creation, package installation on Destinée
# ============================================================================

def build_venv_data() -> Scenario:
    return Scenario(
        name="build_data_env",
        category="build_test",
        description="Create a data science virtual environment with proper packages",
        turns=[
            Turn("crée un virtualenv dans /tmp/data_env avec python3"),
            Turn("installe pandas, numpy, matplotlib et scikit-learn dans cet environnement"),
            Turn("vérifie que les versions installées sont récentes en listant les packages"),
        ],
    )


def build_docker() -> Scenario:
    return Scenario(
        name="build_dockerfile",
        category="build_test",
        description="Create a Dockerfile for a Python application",
        turns=[
            Turn("écris un Dockerfile pour une app Python avec pandas et flask"),
            Turn("ajoute un healthcheck sur le port 5000"),
            Turn("teste si docker est installé et essaye de builder l'image"),
        ],
    )


def build_makefile() -> Scenario:
    return Scenario(
        name="build_make",
        category="build_test",
        description="Create a Makefile for project automation",
        turns=[
            Turn("écris un Makefile avec les cibles : install, test, lint, clean pour un projet Python"),
            Turn("ajoute une cible 'dev' qui lance un watcher avec inotifywait ou watchfiles"),
        ],
    )


# ============================================================================
# ENV/SHELL (~30 turns target)
# Xonsh-specific features, environment variables on Destinée
# ============================================================================

def env_check() -> Scenario:
    return Scenario(
        name="env_inspect",
        category="env_shell",
        description="Inspect and manage environment in xonsh session",
        turns=[
            Turn("montre les variables d'environnement PYTHONPATH et PATH"),
            Turn("quelle est ma version de Python active et où est-elle installée ?"),
            Turn("liste les packages pip installés dans l'environnement courant avec pip list"),
        ],
    )


def env_xonsh_features() -> Scenario:
    return Scenario(
        name="env_xonsh_demo",
        category="env_shell",
        description="Demonstrate xonsh-specific features (mixing Python and shell)",
        turns=[
            Turn("montre moi comment mixer Python et shell dans xonsh - fais ls du répertoire courant en Python avec os.listdir()"),
            Turn("capture la sortie de 'uname -a' dans une variable et affiche-la formatée"),
        ],
    )


def env_aliases() -> Scenario:
    return Scenario(
        name="env_aliases",
        category="env_shell",
        description="Create and manage shell aliases",
        turns=[
            Turn("crée un alias 'gpu' qui exécute nvidia-smi --query-gpu=name,temperature.gpu,memory.used --format=csv"),
            Turn("teste l'alias et affiche le résultat"),
            Turn("ajoute un alias 'disk' qui montre df -h filtré sur les partitions montées"),
        ],
    )


# ============================================================================
# SCENARIO REGISTRY
# ============================================================================

SCENARIOS: dict[str, list[Scenario]] = {}


def _register(scenario: Scenario):
    cat = scenario.category
    if cat not in SCENARIOS:
        SCENARIOS[cat] = []
    SCENARIOS[cat].append(scenario)


_REGISTERED = False


def register_all():
    """Register all defined scenarios into the global registry."""
    global _REGISTERED
    if _REGISTERED:
        return
    _REGISTERED = True

    # Data Science (target ~150 turns)
    for fn in [ds_pandas_csv_exploration, ds_numpy_matrix_ops, ds_sklearn_classification,
               ds_time_series, ds_data_generation, ds_pandas_groupby_aggregation,
               ds_numpy_image_processing, ds_pandas_merge_join, ds_sklearn_regression,
               ds_pandas_datetime_ops, ds_statistical_tests]:
        _register(fn())

    # Natural Conversation (target ~120 turns)
    for fn in [conv_ai_philosophy, conv_tech_explanation, conv_project_ideation,
               conv_french_language, conv_system_discussion, conv_career_advice,
               conv_cooking, conv_music, conv_travel, conv_book_club,
               conv_math_help, conv_startup]:
        _register(fn())

    # Debugging (target ~100 turns)
    for fn in [dbg_factorial, dbg_csv_parsing, dbg_import_error,
               dbg_json_parsing, dbg_regex, dbg_async,
               dbg_type_errors, dbg_file_permissions]:
        _register(fn())

    # Git Workflow (target ~80 turns)
    for fn in [git_projets_status, git_branch_workflow, git_diff_analysis,
               git_stash_workflow, git_log_stats]:
        _register(fn())

    # File Management (target ~80 turns)
    for fn in [fm_project_scaffold, fm_config_transform, fm_log_analysis,
               fm_directory_audit, fm_backup_script]:
        _register(fn())

    # System Monitoring (target ~60 turns)
    for fn in [sysmon_resources, sysmon_gpu, sysmon_network,
               sysmon_disk, sysmon_processes]:
        _register(fn())

    # Python Scripting (target ~70 turns)
    for fn in [py_class_design, py_data_transform, py_file_utils,
               py_web_scraper, py_text_processing, py_config_parser]:
        _register(fn())

    # Web Research (target ~50 turns)
    for fn in [web_llm_quantization, web_manjaro_updates,
               web_ml_trends, web_python_updates]:
        _register(fn())

    # Build/Test (target ~40 turns)
    for fn in [build_venv_data, build_docker, build_makefile]:
        _register(fn())

    # Env/Shell (target ~30 turns)
    for fn in [env_check, env_xonsh_features, env_aliases]:
        _register(fn())


def get_scenarios(category: Optional[str] = None) -> list[Scenario]:
    """Get all scenarios, optionally filtered by category."""
    if not _REGISTERED:
        register_all()
    if category:
        return SCENARIOS.get(category, [])
    result = []
    for cat_scenarios in SCENARIOS.values():
        result.extend(cat_scenarios)
    return result


def get_total_turns(category: Optional[str] = None) -> int:
    """Count total turns across all scenarios."""
    return sum(len(s.turns) for s in get_scenarios(category))
