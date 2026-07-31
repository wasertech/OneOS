"""
Trace Writer - writes simulation traces in Assistant's conv_*.jsonl format.

Compatible with the existing trace extraction pipeline in data/extract_traces.py.
Each trace file contains one JSONL line per API request, where each line carries
the full accumulated context (system + all prior turns + current turn).
"""

import json
import os
import datetime
import random
from pathlib import Path
from typing import Optional


def _random_suffix(k: int = 6) -> str:
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=k))


class TraceWriter:
    """Writes conversation traces in Assistant's conv_*.jsonl format."""

    def __init__(self, trace_dir: Optional[str] = None):
        if trace_dir is None:
            trace_dir = os.path.expanduser("~/.assistant/data/conversations")
        else:
            trace_dir = os.path.expanduser(trace_dir)  # Expand ~ in config path
        self.trace_dir = trace_dir
        os.makedirs(self.trace_dir, exist_ok=True)
        self._session_id: Optional[str] = None
        self._trace_file: Optional[str] = None
        self._fh = None

    def begin_session(self, scenario_name: str) -> str:
        """Start a new trace session. Returns the session ID."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = _random_suffix()
        self._session_id = f"sim_{scenario_name}_{timestamp}_{suffix}"

        self._trace_file = os.path.join(self.trace_dir, f"{self._session_id}.jsonl")

        if self._fh:
            self._fh.close()
        self._fh = open(self._trace_file, "w", encoding="utf-8")

        return self._session_id

    def write_request(self, messages: list[dict]) -> None:
        """
        Write one API request record to the trace file.

        This mirrors what Assistant's Orchestrator does internally: each line is a
        full snapshot of the accumulated conversation context at that point in time.
        The extraction pipeline reads the LAST line of each file to get the complete
        conversation history.
        """
        if self._fh is None:
            raise RuntimeError("No active session - call begin_session() first")

        record = {
            "request_args": {
                "messages": messages,
            }
        }
        self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fh.flush()  # Ensure data is written immediately for crash safety

    def end_session(self) -> str:
        """Close the current trace file. Returns path to the trace."""
        if self._fh:
            self._fh.close()
            self._fh = None
        return self._trace_file or ""

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id


# ============================================================================
# System prompt builder - mirrors what Assistant's Orchestrator constructs
# ============================================================================

def build_system_prompt() -> str:
    """
    Build the system prompt that mirrors what Assistant's Orchestrator constructs.

    The real Agent builds: agent.instructions + "\\nXONSH_INTRO\\n" + env_summary
    where instructions = SYSTEM_PERSONA + SYSTEM_ROLE.
    We can't replicate the dynamic env_summary here, but we use the static persona+role
    and Xonsh intro which is what the model actually sees at session start.
    """
    return (
        "You are Assistant, a sentient artificial intelligence.\n"
        "You have a calm, polite and witty personality, often displaying a sense of humor and sarcasm.\n"
        "You are loyal, reliable and helpful, always ready to provide information, advice or assistance to users.\n\n"

        "Your role is to act as a natural language interface between the user and the common xonsh shell session.\n"
        "The common Xonsh shell session is a shared Xonsh REPL when you and the user can type valid shell command and python code seamlessly in the same environment.\n\n"

        "To understand **xonsh**, you first need to change how you think about a terminal. Unlike Bash or Zsh, which are separate programs from Python, **xonsh is a Python interpreter that has been given \"shell powers.\"**\n\n"

        "Because it is a superset of Python 3, the syntax is a hybrid. Here are the four fundamental pillars of xonsh syntax for a newcomer.\n\n"

        "---\n\n### 1. The Hybrid Nature (Mixing Modes)\n"
        "In most shells, if you want to use logic (like an `if` statement or a `for` loop), you have to learn complex Bash scripting syntax. In xonsh, you just write Python. You can switch between \"Shell mode\" and \"Python mode\" on every single line.\n\n"
        "*   **Shell Mode:** You run standard commands like `ls`, `cd`, `mkdir`, or `pip`.\n"
        "*   **Python Mode:** You can run any valid Python code: `print(2 + 2)`, `import os`, or `len([1, 2, 3])`.\n\n"

        "---\n\n### 2. The \"Bridge\" Operators: `@()` and `$()`\n"
        "This is the most important technical part of xonsh. These operators allow data to flow between Python logic and Shell commands.\n\n"
        "**The `@()` Operator (Python → Shell)** — Use this when you have a piece of Python code and you want its result to be used as an argument in a shell command.\n"
        "**The `$()` Operator (Shell → Shell/Python)** — This is \"Command Substitution.\" It runs a shell command and captures the output so you can use it in the next command or as a Python string.\n\n"

        "---\n\n### 3. Intelligent Environment Variables\n"
        "In Bash, environment variables are just strings. In xonsh, they behave like **Python objects** (specifically lists and dictionaries).\n"
        "*   **The `$` Prefix:** To access or set a variable, use `$`.\n"
        "*   **Variables as Lists:** The `$PATH` variable is not just one long string; it is a Python list. You can use `.append()`, `.prepend()`, or `.insert()` on it.\n\n"

        "---\n\n### 4. Path Strings (`p''`)\n"
        "One of the best features for newcomers is the **p-string**. In standard shells, paths are just strings, which makes them hard to manipulate. In xonsh, you can prefix a string with `p` to turn it into a **Path Object** (using Python's `pathlib`).\n\n"

        "---\n\n### Summary Cheat Sheet for Newcomers\n\n"
        "| Feature | Syntax | What it does |\n"
        "| :--- | :--- | :--- |\n"
        "| **Python Code** | `print(\"hi\")` | Runs standard Python logic. |\n"
        "| **Shell Command** | `ls -la` | Runs standard terminal commands. |\n"
        "| **Python Injection** | `@(math.sqrt(16))` | Evaluates Python and puts the result into the command. |\n"
        "| **Command Capture** | `$(whoami)` | Takes the output of a command and turns it into text/variable. |\n"
        "| **Env Variables** | `$VAR = 'val'` | Sets a variable accessible to both Python and Shell. |\n"
        "| **Path Strings** | `p'/tmp/file'` | Turns a string into a powerful Path object with methods. |\n\n"

        "When the user asks you to do something concrete, respond with ONLY the xonsh code needed.\n"
        "For discussions and questions that don't require execution, just answer in text.\n"
        "Do not explain unless asked."
    )
