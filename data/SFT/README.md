---
license: mit
language:
  - en
pipeline_tag: text-generation
tags:
  - sft
  - fine-tuning
  - instruction-tuning
  - reasoning
  - coding
  - agent
  - frontier-traces
---

# Accretion — Frontier Trace Distillation Dataset

A curated, unified SFT dataset distilled from frontier model traces across multiple architectures and reasoning styles. Named after the accretion disk — the region where matter spirals inward, accelerated and organized by gravity into a coherent structure. This dataset does the same for language model training: it takes high-quality traces from frontier models and accelerates them into a focused, well-organized training resource.

## The Dataset

**29,477 examples** unified from 5 frontier trace sources, covering three categories of behavior:

| Category | Examples | Description |
|---|---|---|
| **coding** | 17,973 | Coding, debugging, code review, implementation |
| **reasoning** | 7,836 | Mathematical reasoning, algorithm design, problem solving |
| **agent** | 3,679 | Tool use, multi-turn agent interactions, command execution |

### Train / Test Split

| Split | Examples |
|---|---|
| **train** | 26,532 |
| **test** | 2,945 |

Split is stratified by source to maintain proportional representation.

### Source Datasets

| Source | Examples | Link |
|---|---|---|
| Fable 5 (Claude Fable 5) | 11,235 | [greghavens/fable-5-coding-and-debugging-traces](https://huggingface.co/datasets/greghavens/fable-5-coding-and-debugging-traces) |
| Kimi K2.6 Max distilled | 7,836 | [lordx64/reasoning-distill-kimi-k2-6-max-sft](https://huggingface.co/datasets/lordx64/reasoning-distill-kimi-k2-6-max-sft) |
| Kimi K3 traces | 4,906 | [greghavens/kimi-k3-coding-and-debugging-traces](https://huggingface.co/datasets/greghavens/kimi-k3-coding-and-debugging-traces) |
| Hermes Agent traces | 3,679 | [DJLougen/hermes-agent-traces-filtered](https://huggingface.co/datasets/DJLougen/hermes-agent-traces-filtered) |
| GLM 5.2 coding & debugging | 1,821 | [greghavens/glm-5.2-coding-and-debugging-traces](https://huggingface.co/datasets/greghavens/glm-5.2-coding-and-debugging-traces) |

## Dataset Structure

Each example follows the standard `messages` format:

```json
{
  "messages": [
    {"role": "user", "content": "Prompt text here..."},
    {"role": "assistant", "content": "<think>\nReasoning steps here...\n</think>\n\nResponse text here...", "tool_calls": [{"id": "...", "type": "function", "function": {"name": "...", "arguments": "..."}}]},
    {"role": "tool", "content": "Tool output..."}
  ],
  "metadata": {
    "source": "hermes_agent",
    "source_name": "DJLougen/hermes-agent-traces-filtered",
    "format_used": "conversations",
    "has_code": true,
    "has_tools": true
  }
}
```

## Statistics

### Language Distribution

The dataset is **100% English**. No translation pass was applied.

### Content Length (per message)

| Role | Median | Mean |
|---|---|---|
| User | ~250 chars | ~1,000 chars |
| Assistant | ~150 chars | ~1,500 chars |
| Tool output | ~100 chars | ~1,500 chars |

### Message Count per Example

| Statistic | Value |
|---|---|
| Median | 2 messages |
| Mean | 18.6 messages |
| Min | 2 |
| Max | 246 |

### Reasoning & Tool Usage

| Metric | Count |
|---|---|
| Assistant messages with reasoning (think tags) | 68,248 |
| Assistant messages with tool_calls | 158,708 |
| Empty assistant messages (silent reasoning) | 103,987 (21.0%) |

### Per-Source Breakdown

| Source | Train | Test | Total |
|---|---|---|---|
| fable_5 | 10,112 | 1,123 | 11,235 |
| kimi_k2.6 | 7,053 | 783 | 7,836 |
| kimi_k3_traces | 4,416 | 490 | 4,906 |
| hermes_agent | 3,312 | 367 | 3,679 |
| glm_5.2 | 1,639 | 182 | 1,821 |
| **Total** | **26,532** | **2,945** | **29,477** |

## Processing Pipeline

The dataset was built through a multi-stage process:

1. **Download & Unification** — Source datasets were downloaded from HuggingFace and converted to a single `messages` format with consistent metadata. Each source's native format (raw text, traces, conversations) was mapped to the unified structure.

2. **Reasoning & Tool Preservation** — The conversion was updated to preserve `reasoning_content` (wrapped in `` tags) and `tool_calls` in assistant messages. These were previously stripped but are critical for frontier model training.

3. **Quality Inspection** — The original Claude Mythos source (25,000 examples) was removed after inspection. The examples had a rigid 1-question-1-answer format with nearly identical openings, making them unsuitable for diverse training.

4. **Train/Test Split** — The remaining 29,477 examples were split 90/10, stratified by source.

## Intended Use

This dataset is designed for supervised fine-tuning (SFT) of base language models on frontier-level reasoning and tool-use behaviors. It's particularly suited for:

- **Reasoning capabilities** — multi-step problem solving, algorithm design
- **Coding & debugging** — implementation, error analysis, code review
- **Agent/Tool-use behavior** — tool calling, multi-turn interactions, command execution

## Notes

- The dataset is **100% English**. A French translation pass was planned but deferred — multilingual base models are expected to transfer English reasoning patterns effectively.
- Some source datasets contain very long conversation traces (up to 246 messages). These are included for realism but may benefit from length-based filtering during training.
- The `hermes_agent` source is the only one with consistent tool-call patterns — it represents real agent trajectories from a multi-turn conversational agent.
- Tool-heavy examples come primarily from the `hermes_agent` source. Other sources have minimal tool usage.

## Citation

If you use this dataset, please cite the original source datasets:

```bibtex
@misc{fable_5_traces,
  title = {fable-5-coding-and-debugging-traces},
  author = {greghavens},
  year = {2025},
  publisher = {Hugging Face}
}

@misc{kimi_k2_6_distill,
  title = {reasoning-distill-kimi-k2-6-max-sft},
  author = {lordx64},
  year = {2025},
  publisher = {Hugging Face}
}

@misc{kimi_k3_traces,
  title = {kimi-k3-coding-and-debugging-traces},
  author = {greghavens},
  year = {2025},
  publisher = {Hugging Face}
}

@misc{hermes_agent_traces,
  title = {hermes-agent-traces-filtered},
  author = {DJLougen},
  year = {2025},
  publisher = {Hugging Face}
}

@misc{glm_5_2_traces,
  title = {glm-5.2-coding-and-debugging-traces},
  author = {greghavens},
  year = {2025},
  publisher = {Hugging Face}
}
```

## License

This curated dataset is released under the **MIT License**. Individual source datasets retain their original licenses — check each source for its specific terms.
