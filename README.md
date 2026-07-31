# OneOS — Natural Language Operating System

Train LLMs on tailored data for system integration with natural language, running on **Destinée** (Threadripper 2920X · 2× TITAN RTX · 96 Go RAM).

---

## Architecture

```
OneOS/src/
├── config.yaml          # Configuration du simulateur (modèles, num_runs, trace_dir)
├── scenarios.py         # 62 scénarios multi-turns · 10 catégories · ~204 seeds
├── simulator.py         # Moteur d'exécution à 2 modèles avec xonsh réel
├── trace_writer.py      # Écriture conv_*.jsonl compatible extract_traces.py
└── data/
    └── extract_traces.py  # Pipeline d'extraction des traces réelles Assistant
```

## User Simulator

Génère des traces d'entraînement réalistes en simulant des interactions utilisateur avec Assistant dans une session xonsh partagée. Les variables, imports et état du filesystem persistent entre turns — ce qui rend ces traces uniques par rapport aux datasets NL2Shell classiques.

### Architecture à 2 modèles

| Rôle | Modèle | Pourquoi |
|---|---|---|
| **User simulator** | `tulu-3.1-8b-supernova` (~8B) | Décodage rapide pour générer les prompts utilisateur variés |
| **Assistant agent** | `grm-2.6-plus` | Qualité de réponse + tool calling fiable |

Le petit modèle reformule chaque seed en un prompt naturel différent à chaque run, ce qui donne une variation réaliste sans surcoût token significatif.

### Scénarios (10 catégories)

| Catégorie | Scénarios | Turns | Exemple |
|---|---|---|---|
| `data_science` | 11 | 50 | pandas EDA, sklearn ML pipeline, numpy matrices, time series |
| `natural_conversation` | 12 | 36 | Philosophie IA, explications tech, cuisine, voyages, carrière |
| `debugging` | 8 | 25 | Syntax errors, CSV parsing, async/await, type errors |
| `git_workflow` | 5 | 15 | Branching, diff analysis, stash, contribution stats |
| `file_management` | 5 | 17 | Project scaffolding, JSON→YAML transform, log parsing |
| `system_monitoring` | 5 | 16 | CPU/RAM/GPU monitoring, disk audit, process tree |
| `python_scripting` | 6 | 19 | OOP design, HTTP client, text processing, config parser |
| `web_research` | 4 | 10 | LLM quantization research, ML trends, Python updates |
| `build_test` | 3 | 8 | venv setup, Dockerfile, Makefile automation |
| `env_shell` | 3 | 8 | Environment inspection, xonsh features, aliases |

**Volume total :** 204 seeds × 5 runs = **~1020 traces** avec variation naturelle.

### Utilisation

```bash
# Lancer toute la simulation (~1000 traces)
cd /home/waser/Projets/OneOS/src
python3 simulator.py

# Lancer une seule catégorie
python3 simulator.py --category data_science

# Configurer un autre endpoint ou modèle
python3 simulator.py --config mon_config.yaml
```

Les traces sont écrites dans `~/.assistant/data/conversations/sim_*.jsonl` au même format que les traces réelles d'Assistant, compatibles avec le pipeline `data/extract_traces.py`.

### Configuration (`config.yaml`)

```yaml
simulator:
  base_url: "http://localhost:1234/v1"       # LM Studio API
  user_model: "tulu-3.1-8b-supernova"        # Petit modèle rapide (user prompts)
  agent_model: "grm-2.6-plus"                # Modèle qualité (assistant responses)
  temperature: 0.7
  max_tokens: 8192
  timeout: null                              # Pas de timeout — génération libre
  num_runs: 5                                # Répétitions par seed (~1000 traces)
  trace_dir: "~/.assistant/data/conversations"
```

## Pipeline de données

```
scenarios.py (seeds)
    ↓
simulator.py (Tulu → GRM + xonsh execution)
    ↓
trace_writer.py (conv_*.jsonl)
    ↓
data/extract_traces.py (extraction + formatage SFT)
    ↓
Dataset d'entraînement pour fine-tuning
```

## Environnement cible

Les scénarios sont ancrés dans l'environnement réel de Destinée :

- **OS :** Linux Destinee 7.0.13-1-MANJARO x86_64
- **CPU :** AMD Ryzen Threadripper 2920X (24 threads) @ 3.5 GHz
- **GPU :** 2× NVIDIA TITAN RTX (24 Go VRAM chacune)
- **RAM :** 96 Go DDR4
- **Disk :** NVMe ~733 Go
- **User :** waser, Home : `/home/waser`, Projets : `/home/waser/Projets/`
- **Langue :** fr_CH.UTF-8, Shell : xonsh via Assistant
- **Python :** 3.11.14
