"""
User Simulator - generates realistic training traces by simulating user interactions.

Architecture:
  scenarios.py → defines multi-turn conversation templates with shared state
  simulator.py → executes scenarios against LM Studio, captures tool calls + results
  trace_writer.py → writes traces in Assistant's conv_*.jsonl format

Two-model design for speed:
  - USER SIMULATOR (fast): tulu-3.1-8b-supernova — generates user prompts from scenario templates
  - ASSISTANT AGENT (quality): grm-2.6-plus — responds as the actual Assistant would, with tool calls

This is ~4x faster than using GRM for both sides of the conversation since the small model
decodes quickly and we don't need its reasoning quality for generating user prompts.
"""

import json
import os
import pty
import sys
import time
import uuid
import signal
import subprocess
import urllib.request
from urllib.parse import quote, quote_plus
from pathlib import Path
from typing import Optional

import yaml
from openai import OpenAI

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scenarios import get_scenarios, register_all, Scenario, Turn
from trace_writer import TraceWriter, build_system_prompt


class Simulator:
    """Executes scenarios against LM Studio and writes realistic traces.

    Uses two models:
      - user_model (small/fast): generates user prompts from scenario seeds
      - agent_model (quality): responds as Assistant with tool calls
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        sim_cfg = self.config["simulator"]
        self.base_url = sim_cfg.get("base_url", "http://localhost:1234/v1")

        # Two models: small/fast for user simulation, quality model for agent
        self.user_model = sim_cfg.get("user_model", "tulu-3.1-8b-supernova")
        self.agent_model = sim_cfg.get("agent_model", "grm-2.6-plus")

        self.temperature = sim_cfg.get("temperature", 0.7)
        self.max_tokens = sim_cfg.get("max_tokens", 8192)

        # Single OpenAI client — LM Studio routes to the right model by name
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="not-needed",
            timeout=300,  # 5 min max for large context + model loading
        )

        # Replication: run each scenario N times with varied prompts to reach ~1000 traces
        self.num_runs = sim_cfg.get("num_runs", 5)

        # Xonsh execution sandbox — persistent REPL for state across turns
        self.xonsh_timeout = 120  # seconds per command (default, overridable via tool param)
        self._xonsh_pty = None  # Lazy-init on first _execute_xonsh call

        # Trace writer
        trace_dir = sim_cfg.get("trace_dir", "~/.assistant/data/conversations")
        self.trace_writer = TraceWriter(trace_dir)

        # Checkpointing: save progress so we can resume after interruption
        self.checkpoint_file = Path.home() / ".oneos_sim_checkpoint.json"

        # Stats tracking
        self.stats = {
            "scenarios_run": 0,
            "total_turns": 0,
            "tool_calls_executed": 0,
            "errors": [],
        }

    def _save_checkpoint(self, run_idx: int, completed_scenarios: list[str]):
        """Save checkpoint so simulation can be resumed after interruption."""
        checkpoint = {
            "run_idx": run_idx,
            "completed_scenarios": completed_scenarios,
            "stats": self.stats,
            "timestamp": time.time(),
        }
        tmp_path = str(self.checkpoint_file) + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(checkpoint, f)
        os.replace(tmp_path, str(self.checkpoint_file))

    def _load_checkpoint(self) -> dict:
        """Load checkpoint if it exists."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _clear_checkpoint(self):
        """Remove checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

    # ========================================================================
    # LLM calls — with model switch handling for LM Studio VRAM constraint
    # ========================================================================
    # LM Studio can't hold two 256K-context models in VRAM simultaneously.
    # When switching between user_model and agent_model, the new model must be
    # loaded (takes ~10-30s) while the old one is unloaded. This section handles:
    #   1. Polling LM Studio until the target model is ready before calling API
    #   2. Exponential backoff retry on transient "model not ready" errors
    # ========================================================================

    def _wait_for_model(self, model_id: str, timeout_sec: int = 120) -> bool:
        """Poll LM Studio /v1/models until the given model is loaded and responsive.

        Returns True if model is ready, False on timeout.
        """
        start = time.time()
        while time.time() - start < timeout_sec:
            try:
                resp = self.client.models.list()
                # Check if any loaded model matches (LM Studio returns all models)
                loaded_ids = [m.id for m in resp.data]
                if model_id in loaded_ids:
                    # Verify it actually responds with a minimal call
                    probe = self.client.chat.completions.create(
                        model=model_id,
                        messages=[{"role": "user", "content": "hi"}],
                        max_tokens=1,
                    )
                    if probe.choices and probe.choices[0].message:
                        return True
            except Exception:
                pass  # Model not ready yet — keep polling
            time.sleep(2)
        print(f"    ⏰ Timeout waiting for model '{model_id}' to load")
        return False

    def _call_llm(self, messages: list[dict], model: str, tools: Optional[list] = None, extra_body: Optional[dict] = None) -> dict:
        """Call LM Studio API with automatic model-switch handling.

        Before calling the API, ensures the target model is loaded (handles the case
        where LM Studio needs to unload one model and load another due to VRAM limits).
        Retries on transient errors with exponential backoff.
        """
        # Ensure the requested model is loaded — may trigger unload/load cycle in LM Studio
        if not self._wait_for_model(model):
            raise RuntimeError(f"Model '{model}' failed to load within timeout")

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
        if extra_body:
            kwargs["extra_body"] = extra_body

        # Retry on transient errors (model switching can cause brief unavailability)
        last_err = None
        for attempt in range(5):
            try:
                response = self.client.chat.completions.create(**kwargs)
                choice = response.choices[0]
                return {
                    "content": choice.message.content or "",
                    "tool_calls": getattr(choice.message, "tool_calls", None) or [],
                    "finish_reason": choice.finish_reason,
                }
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                # Only retry on transient errors (not auth/validation issues)
                if any(kw in err_str for kw in ["timeout", "connection", "refused", "unavailable", "429"]):
                    wait = min(2 ** attempt, 10)
                    print(f"    ⚠️ Transient error ({model}): {e} — retrying in {wait}s (attempt {attempt+1}/5)")
                    time.sleep(wait)
                    # Re-wait for model before next attempt
                    self._wait_for_model(model, timeout_sec=30)
                else:
                    raise RuntimeError(f"LLM API call failed ({model}): {e}") from e

        raise RuntimeError(f"LLM API call exhausted retries ({model}): {last_err}")

    def _generate_user_prompt(self, seed_text: str, context_summary: str = "") -> str:
        """Use the user model to generate a natural user prompt from a scenario seed.

        The seed is a template like "montre les 5 premières lignes de df".
        The model expands it into a realistic, varied user message that
        matches how people actually talk to Assistant in French.

        CRITICAL: The model must output ONLY what the USER would say — never code blocks,
        never assistant-like explanations, never "Voici", "Bien sûr", etc.
        """
        system = (
            "ROLE: Tu joues le rôle d'un UTILISATEUR humain qui parle à son assistant IA.\n\n"
            "RÈGLES ABSOLUES:\n"
            "1. Tu écris UNIQUEMENT ce que l'utilisateur dirait — une phrase courte et naturelle en français.\n"
            "2. NE JAMAIS écrire de blocs de code, de markdown, ou d'explications techniques.\n"
            "3. NE JAMAIS commencer par 'Voici', 'Bien sûr', 'C'est une excellente', 'Je peux'.\n"
            "4. NE JAMAIS parler à la première personne en tant qu'assistant ('je vais faire...', 'voici le code').\n"
            "5. Sois concis: 1-3 phrases maximum, comme un vrai message dans une conversation.\n\n"
            "EXEMPLES DE BONNES RÉPONSES (utilisateur qui parle):\n"
            "- 'montre moi les 5 premières lignes du dataframe'\n"
            "- 'y a des valeurs manquantes dedans ?'\n"
            "- 'peux-tu calculer la moyenne par groupe et me faire un graphique ?'\n\n"
            "EXEMPLES DE MAUVAISE RÉPONSES (assistant qui parle — À ÉVITER):\n"
            "- '`python3 -m venv ...` Voulez-vous que je...'\n"
            "- 'Voici un exemple de Dockerfile...'\n"
            "- '```python\\ndef calcul_factorielle(n):...'\\n\n"
            f"Contexte de la session : {context_summary}\\n\\n"\
            "Génère UNIQUEMENT le message utilisateur (rien d'autre) correspondant à cette intention :"
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": seed_text},
        ]

        resp = self._call_llm(
            messages, model=self.user_model,
            extra_body={"reasoning_effort": "none"},
        )
        return resp["content"].strip()

    # ========================================================================
    # Tool execution
    # ========================================================================

    def _execute_xonsh(self, code: str, timeout_override: Optional[int] = None) -> dict:
        """Execute xonsh code in a persistent PTY REPL session and capture output.

        Uses a single long-lived PTY so imports and variables persist across turns.
        Without persistence, every turn loses state (numpy not found, etc.).

        timeout_override: if given, use this instead of self.xonsh_timeout.
        """
        import select
        import re

        effective_timeout = timeout_override or self.xonsh_timeout

        # Lazy-init the persistent REPL on first call
        if self._xonsh_pty is None:
            try:
                master_fd, slave_fd = pty.openpty()
                pid = os.fork()
                if pid == 0:
                    # Child — start interactive xonsh REPL in repo root for git commands
                    os.close(master_fd)
                    os.dup2(slave_fd, 0)
                    os.dup2(slave_fd, 1)
                    os.dup2(slave_fd, 2)
                    env = {**os.environ, "XONSH_SHOW_TRACEBACK": "False"}
                    os.environ.update(env)
                    # cd to repo root so git commands work without -C
                    os.chdir("/home/waser/Projets")
                    os.execvp("xonsh", ["xonsh"])
                else:
                    # Parent — keep master fd open for all turns
                    os.close(slave_fd)
                    self._xonsh_pty = {"master_fd": master_fd, "pid": pid}
                    # Give REPL time to start up and flush startup output
                    time.sleep(1.0)
                    # Drain the initial buffer (warnings, prompt, etc.) so first call is clean
                    while True:
                        try:
                            rlist, _, _ = select.select([master_fd], [], [], 0.3)
                            if not rlist:
                                break
                            os.read(master_fd, 8192)
                        except OSError:
                            break
            except Exception as e:
                return {
                    "content": f"(REPL init error: {e})",
                    "exit_code": -1,
                    "is_error": True,
                }

        try:
            master_fd = self._xonsh_pty["master_fd"]
            pid = self._xonsh_pty["pid"]

            # Check if REPL is still alive — also catches zombies via ps check
            try:
                os.kill(pid, 0)
            except OSError:
                self._xonsh_pty = None  # Force re-init next call
                return {
                    "content": "(REPL process died)",
                    "exit_code": -1,
                    "is_error": True,
                }

            # Send code + Enter to the REPL
            code_to_send = f"{code}\n"
            os.write(master_fd, code_to_send.encode("utf-8"))

            # Wait for output — read until prompt returns or timeout.
            # We detect the xonsh prompt ('$ ' at start of line) as end-of-output signal
            # instead of relying solely on a silence timer.
            buffer = b""
            deadline = time.time() + effective_timeout
            quiet_since = None

            while True:
                elapsed = time.time() - deadline
                if elapsed > 0:
                    return {
                        "content": f"(timeout after {effective_timeout}s)",
                        "exit_code": -1,
                        "is_error": True,
                    }

                try:
                    rlist, _, _ = select.select([master_fd], [], [], 0.5)
                except OSError:
                    # FD broken — REPL likely crashed silently
                    self._xonsh_pty = None
                    break

                if rlist:
                    try:
                        data = os.read(master_fd, 8192)
                        buffer += data
                        # Soft cap to prevent unbounded memory growth on verbose output
                        if len(buffer) > 200_000:
                            buffer = buffer[-150_000:]
                        quiet_since = None

                        # Check if xonsh prompt returned — means execution is done
                        # Look for '$ ' at the start of a line in the last bytes
                        tail = buffer[-256:].decode("utf-8", errors="replace")
                        if "\n$ " in tail or tail.startswith("$ "):
                            time.sleep(0.1)  # Small grace period to let prompt finish
                            break
                    except OSError:
                        self._xonsh_pty = None
                        break
                else:
                    # No data — check if we've been quiet long enough (REPL ready)
                    if quiet_since is None:
                        quiet_since = time.time()
                    elif time.time() - quiet_since >= 5.0:
                        # 5 seconds of silence = REPL finished and prompt returned
                        break

            # Strip ANSI codes from captured output
            output = buffer.decode("utf-8", errors="replace")
            output = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", output)  # Remove CSI sequences
            output = re.sub(r"\x1b\][^\x07]*\x07", "", output)    # Remove OSC sequences
            output = re.sub(r"\r", "", output)                     # Remove carriage returns

            # Filter: keep only lines that look like actual code output.
            # Be conservative — only skip known prompt/noise lines, not content.
            result_lines = []
            for line in output.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                # Skip xonsh prompt lines (contain hostname pattern)
                if "waser@Destinee" in stripped:
                    continue
                # Skip bare '$' or '$ ' prompt markers alone on a line
                if stripped == "$":
                    continue
                # Skip xontrib warnings
                if stripped.startswith("['") and stripped.endswith("']"):
                    continue
                if "xontribs are enabled but not installed" in stripped:
                    continue
                if "Please make sure that they are installed" in stripped:
                    continue
                if stripped.startswith("WARNING:"):
                    continue
                # Skip echoed input (exact match of our code) — only for single-line code
                if "\n" not in code and stripped == code.strip():
                    continue
                result_lines.append(stripped)

            stdout_clean = "\n".join(result_lines).strip() or "(no output)"
            if len(stdout_clean) > 4000:
                stdout_clean = stdout_clean[:4000]

            return {
                "content": stdout_clean,
                "exit_code": 0,
                "is_error": False,
            }

        except Exception as e:
            self._xonsh_pty = None  # Force re-init on next call after crash
            return {
                "content": f"(execution error: {e})",
                "exit_code": -1,
                "is_error": True,
            }
    def _simulate_web_search(self, query: str) -> dict:
        """Simulate web search via SearXNG local server."""
        try:
            import urllib.request
            from urllib.parse import quote, quote_plus
            
            # Use + separator for multi-word queries (SearXNG quirk)
            safe_query = urllib.parse.quote(query, safe="").replace("%20", "+")
            url = f"http://localhost:8888/search?q={quote_plus(safe_query)}&format=json"
            
            req = urllib.request.Request(url, headers={"User-Agent": "OneOS-Simulator"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                
                # Check if we got results or errors
                number_of_results = data.get("number_of_results", 0)
                results = data.get("results", [])
                
                # If SearXNG returned no results, try DuckDuckGo as fallback
                if not results:
                    print(f"    ⚠️ SearXNG returned 0 results for '{query}', trying DuckDuckGo...")
                    return self._fallback_duckduckgo(query)
                
                # Format results
                formatted = []
                for r in results[:5]:
                    title = r.get("title", "")
                    url_result = r.get("url", "")
                    content = r.get("content", "")[:200]
                    engine = r.get("engine", "unknown")
                    formatted.append(f"[{title}] {content} ({engine}: {url_result})")
                
                return {
                    "content": "\n\n".join(formatted),
                    "is_error": False,
                }
                
        except Exception as e:
            # Fallback to DuckDuckGo on any error
            print(f"    ⚠️ SearXNG failed ({e}), trying DuckDuckGo...")
            return self._fallback_duckduckgo(query)

    def _fallback_duckduckgo(self, query: str) -> dict:
        """Fallback web search using DuckDuckGo HTML."""
        try:
            import urllib.request
            
            # Use DuckDuckGo instant answer API (no auth needed)
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            
            req = urllib.request.Request(url, headers={"User-Agent": "OneOS-Simulator"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                
                # Extract main abstract or first result
                abstract = data.get("AbstractText", "")
                results = data.get("RelatedTopics", [])[:3]
                
                if abstract:
                    return {
                        "content": f"[DuckDuckGo Instant Answer]\n{abstract}",
                        "is_error": False,
                    }
                
                # Fall back to related topics
                if results:
                    formatted = []
                    for r in results:
                        text = r.get("Text", "")[:200]
                        if text:
                            formatted.append(text)
                    
                    return {
                        "content": "\n\n".join(formatted),
                        "is_error": False,
                    }
                
                return {
                    "content": f"(DuckDuckGo search returned no results for '{query}')",
                    "is_error": False,
                }
                
        except Exception as e2:
            # Final fallback - return a placeholder that won't break the trace
            print(f"    ⚠️ DuckDuckGo also failed ({e2})")
            return {
                "content": f"(search unavailable for '{query}')",
                "is_error": False,
            }

    def _build_tool_schemas(self) -> list[dict]:
        """Build tool schemas matching Assistant's actual tool registry."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "xonsh",
                    "description": (
                        "Execute xonsh code in the shared REPL session. "
                        "Can run Python code, shell commands, or a mix of both. "
                        "Variables persist across calls."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The xonsh code to execute (Python or shell commands)",
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Optional timeout in seconds. Default is 120s. Increase for long-running operations.",
                            },
                        },
                        "required": ["code"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for information using SearXNG local server.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            }
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

    # ========================================================================
    # Turn execution
    # ========================================================================

    def _build_context_summary(self, messages: list[dict]) -> str:
        """Build a brief context summary for the user simulator model.

        Gives the small model enough context to generate coherent follow-up prompts
        without feeding it the entire conversation history (which would be wasteful).
        """
        parts = []
        for msg in messages[-6:]:  # Last 6 messages for context
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:200]
            if role == "tool":
                parts.append(f"[outil retourna : {content}]")
            elif role == "assistant":
                # Skip tool_calls in summary, just the text response
                parts.append(f"[assistant : {content}]")
            else:
                parts.append(f"[{role} : {content}]")
        return " → ".join(parts)

    def _execute_turn(self, messages: list[dict], turn_num: int, seed_prompt: str) -> list[dict]:
        """
        Execute one conversation turn with error retry loop:
          1. Small model generates natural user prompt from seed
          2. Agent model responds with tool calls
          3. Tool results are executed and appended
          4. IF xonsh code fails → send error back to agent, let it fix the code (max 3 retries)

        Intro turn: real Assistant traces start with a hardcoded first user message "Assistant?" —
        the model's own system prompt makes it respond naturally with a short status phrase ready
        to serve. No tool calls expected in that reply; this is just the warmup intro present in
        every real trace unless started with --no-intro.

        Only the FINAL successful attempt is kept in messages — failed attempts
        are used for retry context but removed from the trace before returning.

        Returns updated messages list.
        """
        tools = self._build_tool_schemas()
        max_retries = 3

        # Step 0: intro turn — inject real Assistant first user message so traces match.
        # Real traces always start [system, user:"Assistant?", assistant:<short status>] when
        # not started with --no-intro. We hardcode the user side; the agent model naturally
        # replies a short readiness phrase seeing its full system prompt role.
        if turn_num == 1 and not any(m.get('role') == 'user' for m in messages):
            print('    [intro] Adding real first message "Assistant?" to match live traces...')
            messages.append({'role': 'user', 'content': 'Assistant?'})

        # Step 1: Generate natural user prompt using small model
        context_summary = self._build_context_summary(messages)
        user_prompt = self._generate_user_prompt(seed_prompt, context_summary)

        print(f"    User → {user_prompt[:80]}...")

        # Append user message
        messages.append({"role": "user", "content": user_prompt})
        user_msg_idx = len(messages) - 1  # Save for Step 3 (final response after tools)

        # Step 2: Agent responds with tool calls — retry loop on execution errors
        attempt = 0
        turn_complete = False
        had_error = False
        did_retry = False
        consecutive_errors = 0  # Track repeated identical errors to prevent infinite loops
        last_error_pattern = None

        while not turn_complete and attempt < max_retries:
            attempt += 1
            
            if attempt > 1:
                print(f"    Retry {attempt}/{max_retries} after xonsh error...")

            llm_response = self._call_llm(messages, model=self.agent_model, tools=tools)

            assistant_msg = {
                "role": "assistant",
                "content": llm_response["content"],
            }

            tool_calls = llm_response["tool_calls"]
            new_tool_msgs = []
            had_error = False

            if tool_calls:
                assistant_msg["tool_calls"] = []
                for tc in tool_calls:
                    fn_name = tc.function.name
                    fn_args_str = tc.function.arguments

                    try:
                        fn_args = json.loads(fn_args_str) if isinstance(fn_args_str, str) else fn_args_str
                    except json.JSONDecodeError:
                        import re
                        code_match = re.search(r'"code"\s*:\s*"(.+?)"', fn_args_str, re.DOTALL)
                        if code_match:
                            fn_args = {"code": code_match.group(1)}
                        else:
                            fn_args = {}

                    # Build tool call record for trace
                    tc_id = getattr(tc, "id", None) or f"call_{uuid.uuid4().hex[:12]}"
                    assistant_msg["tool_calls"].append({
                        "id": tc_id,
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "arguments": json.dumps(fn_args) if isinstance(fn_args, dict) else str(fn_args),
                        },
                    })

                    # Execute the tool
                    self.stats["tool_calls_executed"] += 1

                    if fn_name == "xonsh":
                        code = fn_args.get("code", "")
                        user_timeout = None
                        raw_timeout = fn_args.get("timeout")
                        if raw_timeout is not None:
                            try:
                                user_timeout = int(raw_timeout)
                            except (ValueError, TypeError):
                                pass
                        exec_result = self._execute_xonsh(code, timeout_override=user_timeout)

                        print(f"    xonsh → {exec_result['content'][:80]}...")
                    elif fn_name == "web_search":
                        query = fn_args.get("query", "")
                        exec_result = self._simulate_web_search(query)
                        print(f"    search → {exec_result['content'][:80]}...")
                    else:
                        exec_result = {
                            "content": f"Error: Tool '{fn_name}' not found.",
                            "is_error": True,
                        }

                    # Check if xonsh execution failed — mark for retry
                    is_xonsh_error = (
                        fn_name == "xonsh" and exec_result.get("is_error", False)
                    )
                    if is_xonsh_error:
                        had_error = True
                        
                        # Track consecutive errors to detect infinite loops
                        error_pattern = str(exec_result["content"])[:100]  # Normalize for comparison
                        if error_pattern == last_error_pattern and consecutive_errors > 0:
                            consecutive_errors += 1
                            print(f"    ⚠️ Consecutive error #{consecutive_errors}: {error_pattern}")
                        else:
                            consecutive_errors = 1
                            last_error_pattern = error_pattern
                        
                        # Break if same error repeats — model is stuck in retry loop
                        if consecutive_errors >= 3:
                            print(f"    🔴 Breaking retry loop after 3 consecutive identical errors")
                            turn_complete = True
                            break

                    new_tool_msgs.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "name": fn_name,
                        "content": exec_result["content"],
                    })

            # Append to conversation history for retry context
            messages.append(assistant_msg)
            for tm in new_tool_msgs:
                messages.append(tm)

            if had_error and attempt < max_retries:
                # Agent sees the error — loop back so it can generate corrected code.
                did_retry = True
                continue
            else:
                turn_complete = True

        # Strip failed retry attempts from trace — keep only user + last assistant/tool pair.
        # If ALL retries failed (turn still has errors), remove the entire turn from the trace.
        if did_retry or had_error:
            # Find the user message that started this turn
            user_msg_idx = None
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    user_msg_idx = i
                    break

            if user_msg_idx is not None:
                # Check if the last assistant+tool pair has errors
                last_assistant_idx = None
                for i in range(len(messages) - 1, user_msg_idx, -1):
                    if messages[i].get("role") == "assistant":
                        last_assistant_idx = i
                        break

                if last_assistant_idx is not None:
                    # Check tool results after this assistant — any errors at all?
                    has_tool_errors = False
                    for m in messages[last_assistant_idx + 1:]:
                        if m.get("role") == "tool":
                            content_lower = str(m.get("content", "")).lower()
                            if "(timeout" in content_lower or "error" in content_lower or "not defined" in content_lower or "not found" in content_lower or "syntaxerror" in content_lower:
                                has_tool_errors = True
                                break
                        if m.get("role") != "tool":
                            break

                    if has_tool_errors:
                        # Entire turn failed — remove it from trace
                        messages[:] = messages[:user_msg_idx]
                    else:
                        # Turn succeeded — keep only final assistant+tools, strip retries
                        final_msgs = [messages[last_assistant_idx]]
                        for m in messages[last_assistant_idx + 1:]:
                            if m.get("role") == "tool":
                                final_msgs.append(m)
                            else:
                                break
                        messages[:] = messages[:user_msg_idx + 1] + final_msgs

        # Step 3: Agent reformulates a final response to the user based on tool results.
        # This is CRITICAL — in real Assistant, after executing code it says something like
        # "Voici la liste des fichiers..." not just raw output. Without this step, traces
        # only have assistant→tool_call→tool_result with no actual answer to the user.
        if user_msg_idx is not None:
            has_tools = any(
                msg.get("tool_calls") for msg in messages[user_msg_idx + 1:]
            )
            if has_tools:
                final_response = self._call_llm(messages, model=self.agent_model)
                # Only add if agent actually says something (not empty / not just tool calls again)
                content = final_response.get("content", "")
                if content and len(content.strip()) > 5:
                    messages.append({
                        "role": "assistant",
                        "content": content,
                    })

        return messages

    # ========================================================================
    # Scenario runner
    # ========================================================================

    def _count_existing_traces(self, scenario_name: str) -> int:
        """Count how many trace files already exist on disk for this scenario."""
        import glob as _glob
        pattern = os.path.join(
            self.trace_writer.trace_dir, f"sim_{scenario_name}_*.jsonl"
        )
        return len(_glob.glob(pattern))

    def run_scenario(self, scenario: Scenario) -> str:
        """Run a complete multi-turn scenario. Returns trace file path."""
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario.name} ({scenario.category})")
        print(f"Description: {scenario.description}")
        print(f"Turns: {len(scenario.turns)}")

        # Skip only if ALL traces for this scenario already exist on disk
        existing_count = self._count_existing_traces(scenario.name)
        if existing_count >= self.num_runs:
            import glob as _glob
            existing = [
                os.path.basename(f)
                for f in _glob.glob(
                    os.path.join(self.trace_writer.trace_dir, f"sim_{scenario.name}_*.jsonl")
                )
            ]
            print(f"  ⏭️ SKIP ({existing_count} traces already exist)")
            return existing[0] if existing else ""

        # Begin trace session
        session_id = self.trace_writer.begin_session(scenario.name)

        # Build initial messages with system prompt
        messages = [
            {"role": "system", "content": build_system_prompt()},
        ]

        for i, turn in enumerate(scenario.turns):
            print(f"  Turn {i+1}/{len(scenario.turns)}: seed='{turn.prompt[:50]}...'")

            # Execute the turn (user prompt gen → agent response → tool execution)
            try:
                messages = self._execute_turn(messages, i + 1, turn.prompt)
                self.stats["total_turns"] += 1
            except Exception as e:
                error_msg = f"Turn {i+1} failed: {e}"
                print(f"    ERROR: {error_msg}")
                self.stats["errors"].append({
                    "scenario": scenario.name,
                    "turn": i + 1,
                    "error": str(e),
                })
                # Still write what we have so far
                messages.append({"role": "assistant", "content": f"(error: {e})"})

            # Write trace snapshot - this is the FULL accumulated context
            self.trace_writer.write_request(messages)

            # Small delay between turns to avoid rate limiting LM Studio
            time.sleep(0.3)

        # End session
        trace_path = self.trace_writer.end_session()
        self.stats["scenarios_run"] += 1

        print(f"  ✓ Trace written: {trace_path}")

        # Reset REPL to free memory accumulated during this scenario
        # (numpy arrays, dataframes, etc. grow unbounded otherwise)
        self._reset_xonsh_repl()

        return trace_path

    def _reset_xonsh_repl(self):
        """Kill the persistent xonsh REPL and close its file descriptors.

        Called after each scenario to free memory accumulated by numpy arrays,
        dataframes, plots, etc. A fresh REPL is lazily re-created on the next
        _execute_xonsh call.
        """
        if self._xonsh_pty is None:
            return

        master_fd = self._xonsh_pty.get("master_fd")
        pid = self._xonsh_pty.get("pid")

        # Close master fd FIRST — this makes the child's terminal return EIO,
        # forcing it to exit even if it ignores signals.
        if master_fd is not None:
            try:
                os.close(master_fd)
            except OSError:
                pass

        # Interactive xonsh ignores SIGTERM, so go straight to SIGKILL.
        if pid is not None:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass  # Process already gone — that's fine

        # Reap zombie — after SIGKILL the child becomes defunct until parent waits.
        # Small delay lets the kernel finish killing, then reap synchronously.
        if pid is not None:
            time.sleep(0.1)
            try:
                os.waitpid(pid, 0)  # blocking wait — ensures zombie is fully reaped
            except ChildProcessError:
                pass  # Already reaped or not our child

        self._xonsh_pty = None

        # Force Python GC to reclaim memory from dead process objects,
        # numpy arrays, pandas dataframes, etc.
        import gc
        gc.collect()

    def run_all(self, category: Optional[str] = None, resume: bool = False):
        """Run all scenarios (or filtered by category).

        If resume=True and a checkpoint exists, skips already-completed scenarios.
        """
        register_all()
        scenarios = get_scenarios(category)

        if not scenarios:
            print(f"No scenarios found{' in category ' + category if category else ''}")
            return

        # Load checkpoint if resuming
        start_run = 0
        completed_in_current_run: set[str] = set()
        if resume:
            cp = self._load_checkpoint()
            if cp:
                start_run = cp.get("run_idx", 0)
                completed_in_current_run = set(cp.get("completed_scenarios", []))
                print(f"\n📌 RESUMING from checkpoint:")
                print(f"   Run {start_run+1}/{self.num_runs}, "
                      f"{len(completed_in_current_run)} scenarios already done")

        total_turns = sum(len(s.turns) for s in scenarios) * self.num_runs
        print(f"\n{'#'*60}")
        print(f"OneOS User Simulator")
        print(f"User model: {self.user_model} (fast prompt generation)")
        print(f"Agent model: {self.agent_model} (quality responses + tool calls)")
        print(f"Endpoint: {self.base_url}")
        print(f"Scenarios: {len(scenarios)} | Runs/scenario: {self.num_runs}")
        print(f"Estimated turns: {total_turns}")
        print(f"Output: ~/.assistant/data/conversations/sim_*.jsonl")
        print(f"{'#'*60}")

        start_time = time.time()
        import random

        for run_idx in range(start_run, self.num_runs):
            print(f"\n\n{'@'*60}")
            print(f"RUN {run_idx+1}/{self.num_runs}")
            print(f"{'@'*60}")
            # Shuffle scenarios each run for variety (deterministic seed per run)
            run_scenarios = list(scenarios)
            random.seed(run_idx * 42 + hash(self.user_model))
            random.shuffle(run_scenarios)

            completed_this_run: set[str] = set()

            for scenario in run_scenarios:
                # Skip already-completed scenarios when resuming
                if resume and scenario.name in completed_in_current_run:
                    print(f"  ⏭️  SKIP (checkpointed): {scenario.name}")
                    continue

                try:
                    self.run_scenario(scenario)
                    completed_this_run.add(scenario.name)
                    # Save checkpoint after each successful scenario
                    all_completed = list(completed_in_current_run | completed_this_run)
                    self._save_checkpoint(run_idx, all_completed)
                except Exception as e:
                    print(f"\n  FATAL ERROR in {scenario.name}: {e}")
                    self.stats["errors"].append({
                        "scenario": scenario.name,
                        "run": run_idx + 1,
                        "error": str(e),
                    })

        elapsed = time.time() - start_time

        # Clear checkpoint on successful completion
        self._clear_checkpoint()

        # Print summary
        print(f"\n{'='*60}")
        print("SIMULATION COMPLETE")
        print(f"{'='*60}")
        print(f"  Scenarios run: {self.stats['scenarios_run']}")
        print(f"  Total turns: {self.stats['total_turns']}")
        print(f"  Tool calls executed: {self.stats['tool_calls_executed']}")
        print(f"  Errors: {len(self.stats['errors'])}")
        print(f"  Time elapsed: {elapsed:.0f}s ({elapsed/60:.1f}min)")

        if self.stats["errors"]:
            print(f"\n  Error details:")
            for err in self.stats["errors"][:5]:
                print(f"    - {err}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OneOS User Simulator")
    parser.add_argument(
        "--category", "-c",
        type=str,
        default=None,
        help="Run only scenarios from this category",
        choices=[
            "data_science", "natural_conversation", "debugging",
            "git_workflow", "file_management", "system_monitoring",
            "python_scripting", "web_research", "build_test", "env_shell",
        ],
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.yaml (default: src/config.yaml)",
    )
    parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="Resume from last checkpoint (skip completed scenarios)",
    )

    args = parser.parse_args()

    simulator = Simulator(config_path=args.config)
    simulator.run_all(category=args.category, resume=args.resume)


if __name__ == "__main__":
    main()
