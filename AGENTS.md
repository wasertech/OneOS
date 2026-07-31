# Agent Guidelines for OneOS Evaluation Project

## Project Context

**OneOS is the testbench for Assistant.** This project tests, evaluates, and compares LLM models before they're deployed to the real Assistant. The goal is to measure model quality for the actual use case: a natural language interface to xonsh shell.

## How It Works

Models are tested through the **real Assistant module** — same system prompt, same tools, same everything. The evaluation uses:
- **Real system prompt** from `~/Projets/Assistant/assistant`: `SYSTEM_PERSONA + SYSTEM_ROLE + XONSH_INTRO + env_summary`
- **Real user config** from `~/.assistant/config.toml`
- **Models served via llama-server** on `http://localhost:8080`
- **Multi-turn evaluation** mimicking actual assistant usage

## Key Files

- `evals/model_compare_multiturn.py` — Main evaluation script. Imports real Assistant modules. Uses real system prompt from `assistant.__init__.py` and `assistant.nlp.xonsh`.
- `evals/tasks/` — JSON task definitions (intro, xonsh-shell scenarios)
- `evals/output/` — JSON output files from evaluations

## Running Evaluations

```bash
cd /home/waser/Projets/OneOS/src
python3 evals/model_compare_multiturn.py --model all
python3 evals/model_compare_multiturn.py --model qwen  # single model
python3 evals/model_compare_multiturn.py --model all --output evals/output/eval_results.json
```

Models are tested through the real Assistant prompt — not hardcoded. The script imports `SYSTEM_PERSONA`, `SYSTEM_ROLE`, and `XONSH_INTRO` from the actual module at `~/Projets/Assistant/assistant`.

## Evaluation Criteria (0-100)

- **40% Language consistency** — Must respond in correct locale. wrong language = penalty.
- **30% Code quality** — Must generate actual xonsh/Python code, not just explain.
- **15% Real data** — No placeholders, no hallucinated values (RAM, CPU, etc.).
- **10% Conciseness** — Not too verbose, not too brief.
- **5% Format** — Proper structure.

## Multi-Turn Test Pattern

Each task is 1-2 turns:
1. **Turn 1**: "Assistant?" → Greeting handshake. Model should acknowledge in correct locale.
2. **Turn 2**: Real query → Model acts. Should generate actual code/command.

## Scoring Thresholds

- **70-100**: ✅ Pass — model is suitable
- **40-69**: ⚠️ Marginal — needs work
- **<40**: ❌ Fail — not suitable

## Available Models on llama-server

```
http://localhost:8080/v1/models →
  google/gemma-4-26b-a4b
  grm-2.6-plus-0628-mtp-reasoning-i1
  ornith-1.0-35b
  qwen3.6-35b-a3b-ud-q4ks
```

## Important Notes

- The system prompt is built dynamically from the Assistant module. NEVER hardcode it — it must reflect what the real assistant uses.
- The real assistant uses the orchestrator with `agent.instructions + "\nXONSH_INTRO\n" + env_summary` as system prompt.
- Use the user's config from `~/.assistant/config.toml`, NOT defaults.
- This is NOT a generic benchmark — it specifically measures how well models perform as xonsh shell assistants.
