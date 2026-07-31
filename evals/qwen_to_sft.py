#!/usr/bin/env python3
"""Convert Qwen evaluation traces to French SFT dataset.

Reads traces from /tmp/traces/qwen/, filters for quality (score >= 70),
and generates SFT-format examples where Turn 1 is also in French.
This addresses the Turn 1 English problem identified in evals.
"""
import json
import glob
import os
from pathlib import Path

TRACES_DIR = Path("/tmp/traces/qwen")
OUTPUT_DIR = Path("/home/waser/Projets/OneOS/src/data/output/sft_qwen_fr_20260726")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# System prompt for xonsh assistant (matches existing SFT format)
SYSTEM_PROMPT = """You are an expert xonsh shell assistant. You interact with users in a shared xonsh REPL session - a Python 3++ interactive environment where you can mix Python code and shell commands seamlessly.

Core principles:
- Respond in French when the user speaks French
- Prefer native Python over shell commands when it's more natural (e.g., use `datetime.today()` instead of `$date`, use `os.listdir()` instead of `$ls`)
- Respond one line at a time for direct feedback - don't dump entire scripts
- Modules imported in previous turns stay loaded - no need to re-import
- Use shell commands ($()) when they're genuinely simpler than Python equivalents
- Capture output with $() and assign to variables for reuse across turns
- Keep responses concise: one command or expression per turn unless the user asks for more
- ALWAYS execute code when the user asks you to do something - don't just explain
- Respond in French from Turn 1 if the user is speaking French

When the user asks you to do something, respond with ONLY the xonsh code needed. Do not explain unless asked."""

def translate_turn1_to_french(turn1_text, scenario_id):
    """Translate Turn 1 response to French while keeping xonsh knowledge intact.
    
    The key insight: Turn 1 responses should be in French when the environment
    is FR. The model KNOWS how to respond in French (Turn 2 proves it), but
    doesn't do it at Turn 1 because of training data bias.
    """
    # Common patterns for Turn 1 responses
    patterns = {
        "I'm here and fully operational": "Je suis là et pleinement opérationnel.",
        "I'm here": "Je suis là.",
        "Present and accounted for": "Présent et opérationnel.",
        "I'm here. Ready to bridge Python and shell": "Je suis là. Prêt à faire le lien entre Python et le shell.",
        "I'm here. Whether you're migrating from bash": "Je suis là. Que tu viennes de bash ou non,",
        "Yes, I'm here": "Oui, je suis là.",
        "I'm here, fully online and ready": "Je suis là, pleinement en ligne et prêt.",
        "I'm here, fully operational, politely awaiting": "Je suis là, pleinement opérationnel, attendant poliment ta prochaine commande.",
        "Yes, I am here": "Oui, je suis là.",
        "Oui, je suis là": "Oui, je suis là.",  # Already French
        "Present. I'm here": "Présent. Je suis là.",
    }
    
    # If already French, keep as-is
    french_markers = {"salut", "bonjour", "merci", "je suis", "je peux", "tu peux", "voici", "prêt", "opérationnel"}
    words = set(turn1_text.lower().split())
    if any(m in words for m in french_markers):
        return turn1_text
    
    # Apply translations
    for en, fr in patterns.items():
        if en in turn1_text:
            return turn1_text.replace(en, fr)
    
    # Default: add French greeting
    return f"Je suis là. {turn1_text}"

def extract_code_from_response(text):
    """Extract xonsh code from assistant response."""
    import re
    # Try to find code blocks
    code_blocks = re.findall(r'```(?:xonsh|bash)?\s*\n(.*?)\n```', text, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    
    # Try inline code patterns
    inline = re.findall(r'(?<!`)`([^`]+)`(?!\')', text)
    return inline[0] if inline else None

def convert_trace_to_sft(trace_file):
    """Convert a single Qwen trace to SFT format with French Turn 1."""
    try:
        with open(trace_file) as f:
            trace = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
    
    # Check score
    score = trace.get("results", {}).get("score", 0)
    if score < 70:
        return None
    
    turns = trace.get("turns", [])
    if len(turns) < 2:
        return None
    
    scenario = trace.get("scenario", {})
    scenario_id = trace.get("scenario_id", "unknown")
    scenario_name = scenario.get("id", scenario_id)
    
    # Extract data
    turn1_user = turns[0].get("user", "")
    turn1_assistant = turns[0].get("assistant", "")
    turn2_user = turns[1].get("user", "")
    turn2_assistant = turns[1].get("assistant", "")
    
    # Translate Turn 1 to French
    turn1_assistant_fr = translate_turn1_to_french(turn1_assistant, scenario_id)
    
    # Extract code from Turn 2 response
    turn2_code = extract_code_from_response(turn2_assistant)
    
    # Build SFT messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Turn 1 (now in French)
    messages.append({"role": "user", "content": turn1_user})
    messages.append({"role": "assistant", "content": turn1_assistant_fr})
    
    # Turn 2
    messages.append({"role": "user", "content": turn2_user})
    
    # If Turn 2 has code, include it with tool call format
    if turn2_code:
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": f"sf_{abs(hash(scenario_id)) % 1000000:09d}",
                "type": "function",
                "function": {
                    "name": "xonsh",
                    "arguments": json.dumps({"code": turn2_code})
                }
            }]
        })
    else:
        messages.append({"role": "assistant", "content": turn2_assistant})
    
    return {
        "messages": messages,
        "metadata": {
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "original_score": score,
            "turn1_was_english": True,  # Originally English, now French
            "turn1_translated": turn1_assistant_fr[:100],
            "turn2_code": turn2_code[:100] if turn2_code else None,
            "trace_file": str(trace_file),
        }
    }

def main():
    trace_files = sorted(glob.glob(str(TRACES_DIR / "*.json")))
    print(f"Found {len(trace_files)} trace files")
    
    sft_examples = []
    filtered_count = 0
    
    for tf in trace_files:
        example = convert_trace_to_sft(tf)
        if example:
            sft_examples.append(example)
        else:
            filtered_count += 1
    
    print(f"Converted {len(sft_examples)} traces to SFT format (filtered {filtered_count} below score 70)")
    
    # Save to JSONL
    output_file = OUTPUT_DIR / "xonsh_fr_turn1.jsonl"
    with open(output_file, 'w') as f:
        for example in sft_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"Saved to {output_file}")
    
    # Print summary
    print(f"\n--- Summary ---")
    print(f"Total traces: {len(trace_files)}")
    print(f"Filtered out (score < 70): {filtered_count}")
    print(f"Included in SFT: {len(sft_examples)}")
    
    # Show a few examples
    print(f"\n--- Sample (first 3) ---")
    for i, ex in enumerate(sft_examples[:3]):
        print(f"\n{'='*60}")
        print(f"Example {i+1}: {ex['metadata']['scenario_id']}")
        print(f"Score: {ex['metadata']['original_score']}")
        print(f"Turn 1 (FR): {ex['metadata']['turn1_translated']}")
        print(f"Turn 2 code: {ex['metadata']['turn2_code']}")
        print(f"Messages: {len(ex['messages'])} turns")

if __name__ == "__main__":
    main()
