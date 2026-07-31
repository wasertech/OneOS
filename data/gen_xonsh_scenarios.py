#!/usr/bin/env python3
"""Generate xonsh syntax scenarios from the official xonsh tutorial docs.

Parses RST with a simple regex parser (no docutils) — docutils + Pygments xonsh lexer
crashes on color_file() needing LS_COLORS shell context in the simulator venv.
Each doc section becomes a scenario in OneOS Scenario/Turn format (French user prompts).
Generation calls LM Studio; run without --run to just extract parsed sections.
"""

import json, time, sys, argparse, os
from pathlib import Path

# Paths
DOCS_DIR = Path("~/Documents/Xonsh/Docs").expanduser()
OUTPUT_FILE = Path(os.environ.get("ONEOS_OUTPUT", str(Path.home() / "Projets" / "OneOS" / "output"))) / "xonsh_gen_scenarios.py"

EXAMPLE_SCENARIOS = """EXEMPLES DE SCÉNARIOS EXISTANTS (format et style à reproduire):

Scénario: Demonstrate xonsh-specific features (mixing Python and shell)
Turns:
1. "montre moi comment mixer Python et shell dans xonsh - fais ls du répertoire courant en Python avec os.listdir()"
2. "capture la sortie de 'uname -a' dans une variable et affiche-la formatée"

Scénario: Basic environment checks
Turns:
1. "quel est le nom de ma machine, mon utilisateur actuel et où suis-je ?"
2. "affiche les 5 premiers résultats de whoami combiné avec hostname en pipe"""


def parse_rst(filepath):
    """Parse RST file into section dicts using simple regex parsing.

    Why not docutils: docutils delegates code blocks to Pygments.
    When xonsh is in the venv, its lexer crashes on color_file() needing
    LS_COLORS shell context. Regex parsing avoids the lexer entirely.
    """
    import re
    text = Path(filepath).read_text()
    lines = text.splitlines()

    # RST section: title line followed by line of === or --- (same length, no spaces)
    section_pat = re.compile(r'^(\S.*?)\s*\n(={3,}|-{3,})$', re.MULTILINE)
    section_indices = []
    for m in section_pat.finditer(text):
        name = " ".join(m.group(1).split())
        start = m.start()
        section_indices.append((name, start))

    sections = []
    for i, (name, start) in enumerate(section_indices):
        end = section_indices[i + 1][1] if i + 1 < len(section_indices) else len(text)
        body = text[start:end]
        examples, context_lines = extract_section_content(body)
        sections.append({
            "name": name,
            "examples": examples,
            "context_text": "\n".join(context_lines[:50]),
        })
    return sections


def extract_section_content(body):
    """Extract xonsh command examples and prose context from a section body."""
    import re
    examples = []
    context_lines = []
    in_literal = False

    # Track if previous line was a directive — RST mandates a blank line separator
    # between directive and its content, which must NOT end the literal block.
    prev_was_directive = False

    for line in body.splitlines():
        if in_literal:
            if line.strip() == "":
                if prev_was_directive:
                    prev_was_directive = False
                    continue  # RST blank-line separator, not block end
                in_literal = False
                continue
            # Inside literal block (code example): xonsh prompts start with "@ "
            cmd = line.strip()
            if cmd.startswith("@ ") and len(cmd) > 2:
                examples.append(cmd[2:])
            continue

        stripped = line.strip()

        # Start of literal block: directive or paragraph ending ::
        if (stripped.startswith(".. ") and not stripped.startswith(".. _")
                and ("::" in line or re.match(r'^\.\. (code-block|prompt|reST|sourcecode)::', stripped))):
            in_literal = True
            prev_was_directive = True
            continue
        if stripped.endswith("::"):
            in_literal = True
            continue

        # Paragraph (prose context)
        if stripped and not stripped.startswith(("-", "+", "=", "*", "#")):
            context_lines.append(stripped)

    return examples, context_lines


def select_syntax_sections(sections):
    """Select sections teaching actual xonsh syntax worth practicing."""
    targets = {
        "Running Commands",
        "Strings and Quoting in Subprocess Mode",
        r"Captured Subprocess with ``$()`` and ``!()``",
        r"Python Evaluation with ``@()``",
        r"Command Substitution with ``@$()``",
        "Pipes",
    }

    selected = []
    for s in sections:
        if any(s["name"].startswith(t) or t.startswith(s["name"]) for t in targets):
            commands = s["examples"]
            # Add context paragraphs too, skip category headings with no real content
            if not commands and not s.get("context_text"):
                continue
            selected.append({
                "section": s["name"],
                "context": s.get("context_text", ""),
                "commands": list(dict.fromkeys(
                    c for c in commands
                    if len(c.strip()) > 2 and not c.strip().startswith("#")
                )),
            })
    return selected


def generate_scenario_prompt(section):
    """Build a prompt for the LLM to generate French user turns from a doc section."""
    cmds = "\n".join(f"  - {c}" for c in section["commands"][:8]) if section["commands"] else "(pas de commande d'exemple dans cette section)"
    ctx = section.get("context", "") or "(pas de contexte textuel dans la documentation pour cette section)"

    return f"""Tu es un ingénieur rédacteur de scénarios utilisateur en français.
Ta tâche : générer 4 à 8 tours (turns) d'un dialogue utilisateur réaliste, en français, qui explorent naturellement la syntaxe xonsh décrite ci-dessous.
Le style doit ressembler exactement aux exemples fournis plus bas — phrases courtes et naturelles, pas de commandes isolées sans phrase d'introduction.

CONTEXTE DOCUMENTATION (section : {section['section']}):
{ctx}

COMMANDES D'EXEMPLE XONSH DE CETTE SECTION (syntaxe vraie issue de la documentation officielle) :
{cmds}

RÈGLES STRICTES :
- Réponds UNIQUEMENT par un bloc JSON valide, sans markdown ```json```.
- Format exact du JSON : {"name": "nom court du scénario", "category": "xonsh_tutorial", "turns": ["prompt tour 1", ...]}
- Les prompts doivent être en français naturel, variés, progressifs.

EXEMPLE DE FORMAT (style à reproduire) :
{EXAMPLE_SCENARIOS}"""


def call_llm(messages):
    from openai import OpenAI
    # Local llama-server (systemd service), not LM Studio.
    client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed", timeout=600)

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="google/gemma-4-26b-a4b",  # llama-server slot ID
                messages=[{"role": "user", "content": messages}],
                temperature=1.0, max_tokens=800)
            raw = resp.choices[0].message.content.strip()

            # Extract JSON from response (handle markdown wrapping if any)
            import re
            obj = json.loads(raw)
        except Exception as e:
            print(f"Warning: LLM call failed attempt {attempt+1}: {e}", file=sys.stderr)
            time.sleep(30 * (attempt + 1))
            continue

        # Validate structure returned by model
        turns = obj.get("turns") or []
        if not isinstance(turns, list):
            print(f"Warning: generated scenario has invalid 'turns' field, skipping", file=sys.stderr)
            return None
        try:
            turns = [str(t).strip('"').strip() for t in turns]
        except Exception as e:
            print(f"Warning: failed to parse turns content: {e}", file=sys.stderr)
            return None

        if len(turns) < 2:
            print(f"Warning: generated scenario has too few turns ({len(turns)}), skipping", file=sys.stderr)
            return None

        # Clean up model output names (remove markdown artifacts, ensure category set properly)
        name = obj.get("name") or "scenario"
        name = re.sub(r"[`_\\*\[\]#()]", "", name).strip().replace('"', '')
        return {"name": name[:50], "category": "xonsh_tutorial", "turns": turns}

    print(f"Warning: all LLM calls failed for this section", file=sys.stderr)
    return None


def generate_scenarios(sections):
    """Generate scenarios by calling the model for each doc section."""
    results = []
    total = len(sections)
    for i, sec in enumerate(sections):
        prompt = generate_scenario_prompt(sec)
        print(f"\rGenerating scenario {i+1}/{total}: {sec['section'][:50]}", end="", flush=True)

        result = call_llm(prompt)
        if not result: continue

        results.append(result)
        print()  # newline after progress update
    return results


def write_generated_code(scenarios, sections):
    """Format generated scenarios as Python code ready to be registered in the OneOS scenario system."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        '# Xonsh tutorial-based scenarios — generated from official xonsh docs.',
        f'# Generated on {now} by data/gen_xonsh_scenarios.py',
        '', 'from .. import Scenario, Turn', '', ''
    ]

    for i, sc in enumerate(scenarios):
        lines.append(f'scenario_{i+1:02d} = Scenario("xonsh_tutorial", "{sc["name"]}",')
        for turn_text in sc["turns"]:
            safe = turn_text.replace("\\", "\\\\").replace('"', '\\"').replace('\n', '\\n')
            lines.append(f'    Turn("{safe}"),')
        lines.append(')')
        lines.append('')

    code = "\n".join(lines)
    OUTPUT_FILE.write_text(code, encoding="utf-8")
    print(f"\nGenerated {len(scenarios)} scenarios -> {OUTPUT_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Generate xonsh tutorial scenarios for OneOS")
    parser.add_argument("--run", action="store_true", help="Generate scenarios against LM Studio (~10-20 min)")
    args = parser.parse_args()

    doc_path = DOCS_DIR / "tutorial.rst"
    if not doc_path.exists():
        sys.exit(f"Error: tutorial.rst not found at {doc_path}\nRun first:\n  git clone --depth 1 https://github.com/xonsh/xonsh.git /tmp/.xonsh\n  mv /tmp/.xonsh/docs ~/Documents/Xonsh/Docs")

    print("Parsing xonsh documentation with docutils...")
    all_sections = parse_rst(doc_path)
    if not all_sections:
        sys.exit("Error: no sections parsed from tutorial.rst — something is wrong with the docs or parsing.")
    
    selected = select_syntax_sections(all_sections)
    print(f"Parsed {len(all_sections)} total sections, selected {len(selected)} syntax-focused ones for generation:")
    for s in selected:
        cmds = f" ({s['commands'][:3]}...)" if len(s.get("commands", [])) > 3 else f" ({s.get('commands', [])})"
        print(f"  - {s['section']}{cmds}")

    if not args.run:
        sys.exit("\nStopped. Pass --run to generate scenarios against LM Studio.")

    print("\nGenerating French scenario turns via LLM (this takes a while, don't cancel mid-way)...")
    scenarios = generate_scenarios(selected)
    if not scenarios:
        sys.exit("Error: no scenarios generated successfully.")

    write_generated_code(scenarios, selected)


if __name__ == "__main__":
    main()
