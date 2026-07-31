#!/usr/bin/env python3
"""Interactive trace editor for OneOS sim traces — wizard mode."""

import json, os, sys, glob, argparse, curses, subprocess, readline
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.assistant/data/conversations/edit_state.json")
SIM_DIR = os.path.expanduser("~/.assistant/data/conversations/")


# ── State management ────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ── File / trace I/O ───────────────────────────────────────────────

def get_sim_files(status="pending"):
    state = load_state()
    files = sorted(glob.glob(f"{SIM_DIR}/sim_*.jsonl"))
    if status == "all":
        return files
    return [f for f in files
            if state.get(os.path.basename(f), {}).get("status", "pending") == status]


import copy as _copy_mod


# ── Deep copy helper ───────────────────────────────────────────────

def deepcopy(obj):
    """Deep copy using stdlib to avoid reference sharing between turns."""
    return _copy_mod.deepcopy(obj)


def load_trace(filepath):
    with open(filepath) as f:
        lines = [l.strip() for l in f if l.strip()]
    data = json.loads(lines[-1])
    # Deep copy so mutations during editing don't leak to next turn/file read
    return deepcopy(data.get("request_args", {}).get("messages", [])), lines, data


def save_trace(messages, lines, data, filepath):
    data["request_args"]["messages"] = messages
    data["_edited"] = {
        "timestamp": datetime.now().isoformat(),
        "editor_version": "3.0"
    }
    lines[-1] = json.dumps(data, ensure_ascii=False)
    with open(filepath, "w") as f:
        for line in lines:
            f.write(line + "\n")


def get_first_user_message(filepath):
    """Extract first user message from a trace file (for description preview)."""
    try:
        with open(filepath) as f:
            lines = [l.strip() for l in f if l.strip()]
        data = json.loads(lines[-1])
        msgs = data.get("request_args", {}).get("messages", [])
        for m in msgs:
            if m.get("role") == "user":
                text = str(m.get("content", ""))
                return text[:150].strip()
    except Exception:
        pass
    return ""


# ── Scenario metadata from filename ────────────────────────────────

SCENARIO_CATEGORIES = {
    "ds_": "Data Science",
    "conv_": "Conversation",
    "dbg_": "Debugging",
    "git_": "Git Workflow",
    "fm_": "File Management",
    "sysmon_": "System Monitor",
    "py_": "Python Scripting",
    "web_": "Web Research",
    "build_": "Build/Test",
    "env_": "Env/Shell",
}


def infer_category(filename):
    name = os.path.basename(filename)
    for prefix, cat in SCENARIO_CATEGORIES.items():
        if name.startswith(f"sim_{prefix}") or name.startswith(prefix):
            return cat
    return "Unknown"


def infer_scenario_name(filename):
    base = os.path.basename(filename).replace(".jsonl", "")
    parts = base.split("_")
    if len(parts) >= 3:
        return "_".join(parts[1:-2])
    return base


# ── Tool call parsing ──────────────────────────────────────────────

def parse_tool_args(tc):
    func = tc.get("function", {})
    name = func.get("name", "?")
    raw = func.get("arguments", func.get("args", "{}"))
    if isinstance(raw, str):
        try:
            return name, json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return name, {}
    elif isinstance(raw, dict):
        return name, raw
    return name, {}


def get_tool_command(tc):
    name, args = parse_tool_args(tc)
    if name == "xonsh":
        return f"xonsh: {args.get('code', '')}"
    return f"{name}: {json.dumps(args)[:120]}"


# ── Display helpers ────────────────────────────────────────────────

def _input_with_default(prompt, default=""):
    """Like input() but shows a pre-filled default value."""
    if default:
        one_line = default.replace("\n", "\\n").strip()
        suffix = f" [{one_line}]"
    else:
        suffix = ""
    raw = input(f"{prompt}{suffix}")
    return raw if raw else (default if default else "")


def clean_line(text):
    return "".join(c for c in text if ord(c) > 31 or c in "\n\t\r")


def truncate_tool_result(content, max_lines=20):
    lines = content.strip().split("\n")
    if len(lines) <= max_lines:
        return lines, False
    return lines[:max_lines], True


# ── Curses interactive file picker ─────────────────────────────────

class FilePickerResult:
    def __init__(self):
        self.selected = None


def _status_pair(status):
    mapping = {
        "pending": 2,
        "validated": 3,
        "refused": 4,
        "reviewed": 5,
    }
    return mapping.get(status, 2)


def interactive_file_picker(stdscr, files, state, result_holder):
    curses.curs_set(0)
    stdscr.nodelay(False)

    if not curses.has_colors():
        raise curses.error("No color support")
    curses.start_color()
    curses.use_default_colors()
    # Pair: fg, bg
    curses.init_pair(1, -1, -1)          # normal
    curses.init_pair(2, curses.COLOR_GREEN, -1)     # pending
    curses.init_pair(3, curses.COLOR_CYAN, -1)      # validated
    curses.init_pair(4, curses.COLOR_RED, -1)       # refused
    curses.init_pair(5, curses.COLOR_YELLOW, -1)    # reviewed
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)  # selected row
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_CYAN)   # header bar
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLUE)   # desc panel

    selected_idx = 0
    scroll_offset = 0
    search_query = ""
    filtered_files = list(files)

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if max_y < 8 or max_x < 40:
            try:
                stdscr.addstr(0, 0, "Terminal too small. Resize.")
            except curses.error:
                pass
            stdscr.refresh()
            ch = stdscr.getch()
            if ch in (27, ord('q'), ord('Q')):
                return
            continue

        header_lines = 2
        desc_lines = 3
        footer_lines = 2
        list_top = header_lines
        list_bottom = max_y - desc_lines - footer_lines
        visible_rows = max(1, list_bottom - list_top)

        # Apply search filter
        if search_query:
            import re
            pattern = re.compile(re.escape(search_query), re.IGNORECASE)
            filtered_files = [f for f in files
                              if pattern.search(os.path.basename(f))
                              or pattern.search(infer_scenario_name(f))
                              or pattern.search(infer_category(f))
                              or pattern.search(get_first_user_message(f))]
        else:
            filtered_files = list(files)

        total = len(filtered_files)
        if total == 0:
            selected_idx = 0
        elif selected_idx >= total:
            selected_idx = max(0, total - 1)

        # Clamp scroll
        if selected_idx < scroll_offset:
            scroll_offset = selected_idx
        elif selected_idx >= scroll_offset + visible_rows:
            scroll_offset = selected_idx - visible_rows + 1

        # ── Header bar ──
        try:
            hdr = f" ONEOS TRACE EDITOR  ({total} trace{'s' if total != 1 else ''}) "
            stdscr.attron(curses.color_pair(7) | curses.A_BOLD)
            stdscr.addnstr(0, 0, hdr.ljust(max_x), max_x - 1)
            stdscr.attroff(curses.color_pair(7) | curses.A_BOLD)
        except curses.error:
            pass

        # ── Search bar ──
        try:
            if search_query:
                sline = f" Filter: '{search_query}' [Esc clear] "
                stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
                stdscr.addnstr(1, 0, sline.ljust(max_x), max_x - 1)
                stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
            else:
                sline = " Filter: (type to search...) "
                stdscr.attron(curses.A_DIM)
                stdscr.addnstr(1, 0, sline.ljust(max_x), max_x - 1)
                stdscr.attroff(curses.A_DIM)
        except curses.error:
            pass

        # ── Column headers ──
        try:
            col_hdr = f" {'#':<4} {'Status':<11} {'Category':<17} {'Scenario':<20} File"
            stdscr.attron(curses.A_BOLD | curses.A_UNDERLINE)
            stdscr.addnstr(list_top, 1, col_hdr, max_x - 2)
            stdscr.attroff(curses.A_BOLD | curses.A_UNDERLINE)
        except curses.error:
            pass

        # ── File rows ──
        for row_idx in range(visible_rows):
            file_idx = scroll_offset + row_idx
            if file_idx >= total:
                break

            fp = filtered_files[file_idx]
            fname = os.path.basename(fp)
            fs = state.get(fname, {})
            status = fs.get("status", "pending")
            scenario = infer_scenario_name(fp)
            category = infer_category(fp)

            # Calculate available width for filename
            fixed_width = 4 + 1 + 11 + 1 + 17 + 1 + 20 + 1  # ~56
            avail_fname = max(8, max_x - 2 - fixed_width)

            line = f" {file_idx+1:<4} {status:<11} {category:<17} {scenario:<20} {fname[:avail_fname]}"

            try:
                if file_idx == selected_idx:
                    stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
                    stdscr.addnstr(list_top + 1 + row_idx, 0, line.ljust(max_x), max_x - 1)
                    stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
                else:
                    # Color the status portion
                    prefix = f" {file_idx+1:<4} "
                    status_str = f"{status:<11}"
                    rest = f" {category:<17} {scenario:<20} {fname[:avail_fname]}"

                    stdscr.addnstr(list_top + 1 + row_idx, 0, prefix, max_x - 1)
                    xpos = len(prefix)
                    try:
                        stdscr.attron(curses.color_pair(_status_pair(status)))
                        stdscr.addnstr(list_top + 1 + row_idx, xpos, status_str, max_x - xpos - 1)
                        stdscr.attroff(curses.color_pair(_status_pair(status)))
                    except curses.error:
                        pass
                    try:
                        stdscr.addnstr(list_top + 1 + row_idx, xpos + len(status_str), rest, max_x - xpos - len(status_str) - 1)
                    except curses.error:
                        pass
            except curses.error:
                pass

        # ── Description panel ──
        desc_y = list_bottom
        if total > 0 and selected_idx < total:
            fp = filtered_files[selected_idx]
            desc = get_first_user_message(fp)
            scenario = infer_scenario_name(fp)
            category = infer_category(fp)

            try:
                stdscr.attron(curses.color_pair(8))
                info_line = f" Scenario: {scenario}  |  Category: {category}"
                stdscr.addnstr(desc_y, 0, info_line.ljust(max_x), max_x - 1)
                stdscr.attroff(curses.color_pair(8))
            except curses.error:
                pass

            try:
                if desc:
                    msg_line = f" First message: {desc}"
                else:
                    msg_line = " First message: (none)"
                # Wrap description over up to 2 lines
                remaining = max_x - 2
                if len(msg_line) > remaining:
                    stdscr.addnstr(desc_y + 1, 0, msg_line[:remaining], remaining)
                    stdscr.addnstr(desc_y + 2, 0, msg_line[remaining:remaining*2].ljust(remaining), remaining)
                else:
                    stdscr.addnstr(desc_y + 1, 0, msg_line.ljust(max_x), max_x - 1)
            except curses.error:
                pass

        # ── Footer help ──
        footer_y = max_y - footer_lines
        try:
            h1 = " [Up/Dn] Navigate  [PgUp/PgDn] Page  [Enter] Pick  [A] All filtered  [Q] Quit"
            stdscr.addnstr(footer_y, 0, h1.ljust(max_x), max_x - 1)
        except curses.error:
            pass

        try:
            if total > visible_rows:
                scroll_info = f" {scroll_offset+1}-{min(scroll_offset+visible_rows, total)} / {total} "
                stdscr.addstr(footer_y + 1, max_x - len(scroll_info) - 1, scroll_info)
        except curses.error:
            pass

        if total > 0 and selected_idx < total:
            try:
                fname_short = os.path.basename(filtered_files[selected_idx])
                fline = f" {fname_short}"
                stdscr.attron(curses.A_DIM)
                stdscr.addnstr(footer_y + 1, 0, fline, max_x - 1)
                stdscr.attroff(curses.A_DIM)
            except curses.error:
                pass

        stdscr.refresh()

        # ── Input ──
        stdscr.nodelay(True)
        ch = stdscr.getch()
        stdscr.nodelay(False)

        if ch == -1:
            continue

        if ch in (curses.KEY_UP, 260):
            selected_idx = max(0, selected_idx - 1)
        elif ch in (curses.KEY_DOWN, 258):
            selected_idx = min(total - 1, selected_idx + 1)
        elif ch in (curses.KEY_PPAGE, 339):
            selected_idx = max(0, selected_idx - visible_rows)
        elif ch in (curses.KEY_NPAGE, 337):
            selected_idx = min(total - 1, selected_idx + visible_rows)
        elif ch in (curses.KEY_HOME, 259):
            selected_idx = 0
        elif ch in (curses.KEY_END, 360):
            selected_idx = total - 1
        elif ch == 27:  # Escape — clear search
            if search_query:
                search_query = ""
                selected_idx = 0
        elif ch in (ord('q'), ord('Q')):
            result_holder.selected = None
            return
        elif ch in (10, 13, curses.KEY_ENTER):
            if total > 0 and selected_idx < total:
                result_holder.selected = [filtered_files[selected_idx]]
                return
        elif ch in (ord('a'), ord('A')):
            result_holder.selected = list(filtered_files) if filtered_files else list(files)
            return
        elif ch in (127, curses.KEY_BACKSPACE, 8):
            search_query = search_query[:-1]
            selected_idx = 0
        elif 32 <= ch <= 126:
            search_query += chr(ch)
            selected_idx = 0


def run_file_picker(files, state):
    """Run curses picker; return selected filepaths or None (quit)."""
    holder = FilePickerResult()

    def _run(stdscr):
        interactive_file_picker(stdscr, files, state, holder)

    try:
        curses.wrapper(_run)
    except Exception as e:
        os.system("tput reset")
        print(f"  Picker error: {e}. Falling back to all files.")
        return list(files)

    # Force full terminal restore after curses — prevents invisible output
    os.system("tput reset")
    sys.stdout.flush()
    return holder.selected


# ── Wizard: step-based turn model ───────────────────────────────────
# Each turn = user msg + ordered list of steps.
# Step types: "reasoning" (assistant text), "action" (tool call + result)

def _next_id():
    """Generate a unique tool call ID."""
    import random
    return str(random.randint(100000000, 999999999))


def _replay_prior_actions(turns, current_turn_idx, prior_steps_in_turn=None):
    """Re-execute xonsh/file actions to restore environment state before executing one.

    Replays:
      1) all xonsh + file-mutating actions from turns 0..current_turn_idx-1
         (these are the committed, previously reviewed turns), then
      2) optional prior action steps from the CURRENT turn — edits/insertions made
         earlier in this editing session but not yet saved to disk.

    This ensures that when you edit/add an action at turn N, the full shell context
    (venv activated, files created, packages installed, etc.) is properly accumulated.
    Returns True if replay succeeded, False on errors.
    """
    has_prior = bool(prior_steps_in_turn)

    # No prior turns and no in-turn steps → nothing to do
    if current_turn_idx == 0 and not has_prior:
        return True

    print(f"\n  ⏮  Replaying actions to restore environment state "
          f"(turns 1..{current_turn_idx}" + (", plus prior edits this turn" if has_prior else "") + ")...")
    _init_xonsh()

    for ti in range(current_turn_idx):
        turn = turns[ti]
        for step in turn["steps"]:
            if step["type"] == "action":
                tc = step["tool_call"]
                name, args = parse_tool_args(tc)

                # Only replay xonsh commands (they carry shell state forward)
                if name == "xonsh":
                    code = args.get("code", "")
                    if code:
                        try:
                            _execute_tool(name, args)
                            print(f"    ✓ Turn {ti+1}: {code.strip()[:60]}")
                        except Exception as e:
                            print(f"    ✗ Turn {ti+1} failed: {e}")

                elif name in ("write_file", "edit_file"):
                    # Also replay file operations since they affect the filesystem
                    try:
                        _execute_tool(name, args)
                        print(f"    ✓ Turn {ti+1}: {name}{args.get('path', '?')}")
                    except Exception as e:
                        print(f"    ✗ Turn {ti+1} failed: {e}")

                elif name == "read_file":
                    # Skip read-only operations — no state to carry forward
                    pass

    # ── Then replay prior actions from the CURRENT turn (edits made earlier this session) ──
    if prior_steps_in_turn:
        for si, step in enumerate(prior_steps_in_turn):
            tc = step["tool_call"]
            name, args = parse_tool_args(tc)

            if name == "xonsh":
                code = args.get("code", "")
                if code:
                    try:
                        _execute_tool(name, args)
                        print(f"    ✓ Step {si}: {code.strip()[:60]}")
                    except Exception as e:
                        print(f"    ✗ Step {si} failed: {e}")

            elif name in ("write_file", "edit_file"):
                try:
                    _execute_tool(name, args)
                    print(f"    ✓ Step {si}: {name}{args.get('path', '?')}")
                except Exception as e:
                    print(f"    ✗ Step {si} failed: {e}")

            elif name == "read_file":
                pass  # read-only — no state to carry forward

    print("  Replay complete.\n")
    return True


def get_turns(messages):
    """Parse messages into turns with ordered steps (reasoning + actions).

    Two-pass approach: first scan to detect which assistant msgs have tool_calls,
    then classify content-only msgs as "reasoning" (before any action) or
    "response" (after any action). This correctly handles transition messages
    between reasoning and actions that should be visible replies.
    """
    turns = []
    i = 0
    while i < len(messages) and messages[i]["role"] == "system":
        i += 1

    while i < len(messages):
        if messages[i]["role"] != "user":
            i += 1
            continue

        turn = {"user": messages[i], "steps": []}
        i += 1

        # Skip orphaned tool results before any assistant message
        while i < len(messages) and messages[i]["role"] == "tool":
            i += 1

        # ── Pass 1: collect all assistant msgs + tool results in this turn ──
        rounds = []  # list of (asst_msg, tool_results_list)
        while i < len(messages) and messages[i]["role"] == "assistant":
            asst_msg = messages[i]
            i += 1

            # Collect following tool results
            results = []
            while i < len(messages) and messages[i]["role"] == "tool":
                results.append(messages[i])
                i += 1

            rounds.append((asst_msg, results))

        # ── Pass 2: detect if turn has any actions at all ──
        has_any_actions = any(r[0].get("tool_calls", []) for r in rounds)

        # ── Pass 3: classify each round into steps ──
        seen_actions = False
        first_content_only = True  # track if we've seen the first content-only msg
        for asst_msg, results in rounds:
            tool_calls = asst_msg.get("tool_calls", [])
            content = str(asst_msg.get("content", "")).strip()

            if tool_calls:
                # Classify content BEFORE marking actions as seen (order matters!)
                if content and not seen_actions:
                    # First time seeing actions → reasoning (pre-action thoughts)
                    turn["steps"].append({
                        "type": "reasoning",
                        "text": content,
                    })
                    first_content_only = False  # reset — next content-only will be response
                elif content:
                    # Actions already seen in a prior round → response
                    turn["steps"].append({
                        "type": "response",
                        "text": content,
                    })

                # Now mark that actions have been seen for subsequent rounds
                seen_actions = True

                # Pair each tool call with its result
                for tc_idx, tc in enumerate(tool_calls):
                    res = results[tc_idx] if tc_idx < len(results) else None
                    turn["steps"].append({
                        "type": "action",
                        "tool_call": deepcopy(tc),
                        "result": deepcopy(res) if res else None,
                    })

            elif content:
                # Content-only message — classify based on context
                if seen_actions or not has_any_actions:
                    # After actions, or no actions in turn at all → response (visible reply)
                    turn["steps"].append({
                        "type": "response",
                        "text": content,
                    })
                elif first_content_only:
                    # Very first content-only msg before any action → reasoning (internal thought)
                    first_content_only = False
                    turn["steps"].append({
                        "type": "reasoning",
                        "text": content,
                    })
                else:
                    # 2nd+ content-only msg before actions → response (visible transition/announcement)
                    turn["steps"].append({
                        "type": "response",
                        "text": content,
                    })

        turns.append(turn)

    return turns


def show_turn(turn_num, turn, show_full_result=False):
    """Display a single turn with all its steps."""
    print(f"\n{'─'*60}")
    print(f"  TURN {turn_num}  ({len(turn['steps'])} step(s))")
    print(f"{'─'*60}")

    user_text = str(turn["user"].get("content", ""))
    print(f"\n  USER: {user_text}")

    for si, step in enumerate(turn["steps"]):
        if step["type"] == "reasoning":
            txt = step["text"]
            lines = txt.split("\n")
            print(f"\n  [{si}] REASONING:")
            for line in lines[:5]:
                print(f"      {line}")
            if len(lines) > 5:
                print(f"      ... [{len(lines)-5} more lines]")

        elif step["type"] == "response":
            txt = step["text"]
            lines = txt.split("\n")
            print(f"\n  [{si}] RESPONSE:")
            for line in lines[:5]:
                print(f"      {line}")
            if len(lines) > 5:
                print(f"      ... [{len(lines)-5} more lines]")

        elif step["type"] == "action":
            tc = step["tool_call"]
            cmd = get_tool_command(tc)
            name, args = parse_tool_args(tc)
            print(f"\n  [{si}] ACTION → {cmd}")

            if step.get("result"):
                res_text = str(step["result"].get("content", ""))
                max_l = 9999 if show_full_result else 10
                lines, truncated = truncate_tool_result(res_text, max_lines=max_l)
                print(f"    [RESULT]:")
                for line in lines:
                    clean = clean_line(line)
                    if clean.strip():
                        print(f"      {clean}")
                if truncated:
                    total = len(res_text.split("\n"))
                    print(f"      ... [{total - max_l} more lines]")

    print()


def ask_turn_action():
    """Ask what to do with the current turn."""
    print(f"\n  What do you want to do?")
    print(f"    [V] Validate — accept this turn as-is")
    print(f"    [X] Refuse — mark this turn as incorrect")
    print(f"    [E] Edit — modify any part of this turn")
    print(f"    [T] Show full results")
    print(f"    [P] View the full system prompt for this trace")
    print(f"    [S] Skip — no changes, move on\n")

    while True:
        choice = input("  -> ").strip().lower()
        if choice in ("v", "x", "e", "t", "s", "p"):
            return choice
        print("  Invalid. Enter V, X, E, T, P, or S.")


def _edit_action_step(steps, step_idx, turns=None, current_turn_idx=0):
    """Edit an action step: change tool, args, regenerate result.

    Args:
        steps: the turn's full list of steps (current state, including edits made this session).
        step_idx: index in steps of the action to edit.
        turns / current_turn_idx: for replay of prior turns' committed actions.
    """
    step = steps[step_idx]
    tc = step["tool_call"]
    name, args = parse_tool_args(tc)

    available_tools = [
        "xonsh", "read_file", "edit_file", "write_file",
        "web_search", "read_webpage", "memory_search", "memory_add"
    ]
    print(f"\n  Available tools: {', '.join(available_tools)}")
    print("    [1] xonsh          [2] read_file     [3] edit_file")
    print("    [4] write_file     [5] web_search    [6] read_webpage")
    print("    [7] memory_search  [8] memory_add\n")

    tool_pick = input(f"  Pick tool (number or name) [{name}]: ").strip()
    if not tool_pick:
        return False
    num_map = {
        "1": "xonsh", "2": "read_file", "3": "edit_file", "4": "write_file",
        "5": "web_search", "6": "read_webpage", "7": "memory_search", "8": "memory_add"
    }
    new_name = num_map.get(tool_pick, tool_pick)
    if new_name not in available_tools:
        print(f"  Unknown tool '{new_name}'.")
        return False

    # Collect args
    if new_name == "xonsh":
        cur_code = args.get("code", "")
        print(f"\n  Current code:")
        for i, line in enumerate(cur_code.split("\n")):
            print(f"    {i+1}: {line}")
        new_code = _input_with_default("\n  New code (empty to cancel)", default=cur_code)
        if not new_code or new_code == cur_code:
            return False
        args = {"code": new_code}

    elif new_name == "read_file":
        cur_path = args.get("path", "")
        print(f"\n  Current path: {cur_path}")
        new_path = _input_with_default("\n  File path (empty to cancel)", default=cur_path).strip()
        if not new_path or new_path == cur_path:
            return False
        start_l = input("  Start line [1]: ").strip() or None
        end_l = input("  End line [all]: ").strip() or None
        args = {"path": new_path}
        if start_l:
            args["start_line"] = int(start_l)
        if end_l:
            args["end_line"] = int(end_l)

    elif new_name == "edit_file":
        print("\n  Edit file — path, old_text, new_text")
        new_path = input("  File path (empty to cancel): ").strip()
        if not new_path:
            return False
        old_t = input("  Old text: ")
        new_t = input("  New text: ")
        args = {"path": new_path, "old_text": old_t, "new_text": new_t}

    elif new_name == "write_file":
        print("\n  Write file")
        new_path = input("  File path (empty to cancel): ").strip()
        if not new_path:
            return False
        content_lines = []
        print("  Enter content (end with empty line):")
        while True:
            line = input("    ")
            if line == "":
                break
            content_lines.append(line)
        args = {"path": new_path, "content": "\n".join(content_lines)}

    elif new_name == "web_search":
        cur_q = args.get("query", "")
        print(f"\n  Current query: {cur_q}")
        new_q = _input_with_default("\n  Search query (empty to cancel)", default=cur_q).strip()
        if not new_q or new_q == cur_q:
            return False
        n_res = input("  Num results [5]: ").strip() or "5"
        args = {"query": new_q, "num_results": int(n_res)}

    elif new_name == "read_webpage":
        cur_url = args.get("url", "")
        print(f"\n  Current URL: {cur_url}")
        new_url = _input_with_default("\n  URL (empty to cancel)", default=cur_url).strip()
        if not new_url or new_url == cur_url:
            return False
        max_len = input("  Max length [8000]: ").strip() or "8000"
        args = {"url": new_url, "max_length": int(max_len)}

    elif new_name == "memory_search":
        cur_q = args.get("query", "")
        print(f"\n  Current query: {cur_q}")
        new_q = _input_with_default("\n  Search query (empty to cancel)", default=cur_q).strip()
        if not new_q or new_q == cur_q:
            return False
        args = {"query": new_q}

    elif new_name == "memory_add":
        cur_t = args.get("text", "")
        print(f"\n  Current text: {cur_t[:200]}")
        new_t = _input_with_default("\n  Text to add (empty to cancel)", default=cur_t).strip()
        if not new_t or new_t == cur_t:
            return False
        args = {"text": new_t}

    # Update tool call
    tc["function"]["name"] = new_name
    tc["function"]["arguments"] = json.dumps(args)

    # Replay prior actions to restore environment state (venv, files, etc.),
    # including edits made earlier in this turn before step_idx.
    prior_in_turn = [s for s in steps[:step_idx] if s["type"] == "action" and s.get("result")]
    _replay_prior_actions(turns, current_turn_idx, prior_steps_in_turn=prior_in_turn)

    # Regenerate result
    print("\n  Executing to regenerate result...")
    try:
        out = _execute_tool(new_name, args)
        new_result = out.strip() if out.strip() else "(empty output)"

        if step.get("result"):
            step["result"]["content"] = new_result
            step["result"]["name"] = new_name
        else:
            step["result"] = {
                "role": "tool",
                "tool_call_id": tc.get("id", _next_id()),
                "name": new_name,
                "content": new_result,
            }

        print(f"  Result regenerated ({len(new_result)} chars):")
        for rline in new_result.split("\n")[:5]:
            print(f"    {rline}")
        if len(new_result.split("\n")) > 5:
            print(f"    ... [{len(new_result.split(chr(10)))-5} more lines]")

    except subprocess.TimeoutExpired:
        err_msg = "Execution timed out (30s)"
        print(f"  {err_msg}")
        if step.get("result"):
            step["result"]["content"] = err_msg
        else:
            step["result"] = {"role": "tool", "tool_call_id": tc.get("id", _next_id()), "name": new_name, "content": err_msg}
    except Exception as e:
        print(f"  Execution error: {e}")
        if step.get("result"):
            step["result"]["content"] = str(e)
        else:
            step["result"] = {"role": "tool", "tool_call_id": tc.get("id", _next_id()), "name": new_name, "content": str(e)}

    print("  Action updated.")
    return True


def _init_xonsh():
    """Initialize xonsh environment (lazy, once)."""
    import xonsh.main as _xm
    _xm.setup()


def _execute_tool(name, args):
    """Execute a tool using real Assistant tool functions."""
    from assistant.tools import (
        execute_xonsh, execute_read_file, execute_write_file,
        execute_edit_file, execute_web_search, execute_read_webpage,
        execute_memory_search, execute_memory_add,
    )

    # xonsh tools need XSH initialized; others don't but it's safe to call once
    _init_xonsh()

    dispatch = {
        "xonsh": execute_xonsh,
        "read_file": execute_read_file,
        "write_file": execute_write_file,
        "edit_file": execute_edit_file,
        "web_search": execute_web_search,
        "read_webpage": execute_read_webpage,
        "memory_search": execute_memory_search,
        "memory_add": execute_memory_add,
    }

    fn = dispatch.get(name)
    if fn is None:
        return f"(tool {name} — not found)"

    try:
        result = fn(args)
        content = result.get("content", "") if isinstance(result, dict) else str(result)
        return content if content else "(empty output)"
    except Exception as e:
        return f"Error executing {name}: {e}"


def edit_turn_content(turn, turns=None, current_turn_idx=0):
    """Edit any part of a turn: user msg, steps, or insert new reasoning/action.
    
    Args:
        turn: the current turn being edited.
        turns: all turns (for replay of prior actions).
        current_turn_idx: index of this turn in the list (for replay scope).
    """
    while True:
        print(f"\n  ── EDIT TURN ({len(turn['steps'])} step(s)) ──")
        print(f"    [U] Edit user message")

        for si, step in enumerate(turn["steps"]):
            if step["type"] == "reasoning":
                preview = step["text"][:60].replace("\n", " ")
                print(f"    [{si}] Reasoning: \"{preview}...\"")
            elif step["type"] == "response":
                preview = step["text"][:60].replace("\n", " ")
                print(f"    [{si}] Response: \"{preview}...\"")
            elif step["type"] == "action":
                cmd = get_tool_command(step["tool_call"])[:50]
                print(f"    [{si}] Action: {cmd}")

        print(f"\n    [R] Add reasoning at end")
        print(f"    [P] Add response (visible reply) at end")
        print(f"    [C] Create new action (tool call)")
        print(f"    [D] Delete a step")
        print(f"    [M] Move/reorder steps")
        print(f"    [I] Insert reasoning before step N")
        print(f"    [O] Insert response before step N")
        print(f"    [Q] Done editing\n")

        choice = input("  -> ").strip().upper()

        if choice == "U":
            old = str(turn["user"].get("content", ""))
            print(f"\n  Current: {old}")
            new = _input_with_default("\n  New text (empty to cancel)", default=old)
            if new and new != old:
                turn["user"]["content"] = new
                print("  Updated.")

        elif choice.isdigit():
            si = int(choice)
            if 0 <= si < len(turn["steps"]):
                step = turn["steps"][si]
                if step["type"] in ("reasoning", "response"):
                    old = step["text"]
                    stype = step["type"].upper()
                    print(f"\n  Current {stype}:")
                    for i, line in enumerate(old.split("\n")):
                        print(f"    {i+1}: {line}")
                    new = _input_with_default("\n  New text (empty to cancel)", default=old)
                    if new and new != old:
                        step["text"] = new
                        print("  Updated.")
                elif step["type"] == "action":
                    # Pass the live turn steps + index so replay includes edits made earlier this session
                    _edit_action_step(turn["steps"], si, turns=turns, current_turn_idx=current_turn_idx)
            else:
                print("  Invalid step number.")

        elif choice == "R":
            txt = input("\n  Reasoning text (empty to cancel): ")
            if txt:
                turn["steps"].append({"type": "reasoning", "text": txt})
                print("  Added at end.")

        elif choice == "P":
            txt = input("\n  Response text (visible reply, empty to cancel): ")
            if txt:
                turn["steps"].append({"type": "response", "text": txt})
                print("  Added at end.")

        elif choice == "O":
            if not turn["steps"]:
                print("  No steps yet — use [P] to add at end.")
                continue
            num = input(f"\n  Insert BEFORE step number (0-{len(turn['steps'])-1}): ").strip()
            try:
                pos = int(num)
                if 0 <= pos < len(turn["steps"]):
                    txt = input("  Response text (empty to cancel): ")
                    if txt:
                        turn["steps"].insert(pos, {"type": "response", "text": txt})
                        print(f"  Inserted before step {pos}.")
                else:
                    print("  Out of range.")
            except ValueError:
                print("  Invalid number.")

        elif choice == "C":
            _create_action_step(turn, turns=turns, current_turn_idx=current_turn_idx)

        elif choice == "D":
            if not turn["steps"]:
                print("  No steps to delete.")
                continue
            num = input(f"\n  Step number to delete (0-{len(turn['steps'])-1}): ").strip()
            try:
                di = int(num)
                if 0 <= di < len(turn["steps"]):
                    removed = turn["steps"].pop(di)
                    rtype = removed["type"]
                    print(f"  Deleted step {di} ({rtype}).")
                else:
                    print("  Out of range.")
            except ValueError:
                print("  Invalid number.")

        elif choice == "M":
            _reorder_steps(turn)

        elif choice == "I":
            if not turn["steps"]:
                print("  No steps yet — use [R] to add at end.")
                continue
            num = input(f"\n  Insert BEFORE step number (0-{len(turn['steps'])-1}): ").strip()
            try:
                pos = int(num)
                if 0 <= pos < len(turn["steps"]):
                    txt = input("  Reasoning text (empty to cancel): ")
                    if txt:
                        turn["steps"].insert(pos, {"type": "reasoning", "text": txt})
                        print(f"  Inserted before step {pos}.")
                else:
                    print("  Out of range.")
            except ValueError:
                print("  Invalid number.")

        elif choice == "Q":
            break

        else:
            print("  Invalid choice.")


def _create_action_step(turn, turns=None, current_turn_idx=0):
    """Create a new action step (tool call + result) and append to turn.
    
    Args:
        turn: the current turn being edited.
        turns: all turns (for replay of prior actions).
        current_turn_idx: index of this turn in the list (for replay scope).
    """
    available_tools = [
        "xonsh", "read_file", "edit_file", "write_file",
        "web_search", "read_webpage", "memory_search", "memory_add"
    ]
    print(f"\n  Available tools: {', '.join(available_tools)}")
    print("    [1] xonsh          [2] read_file     [3] edit_file")
    print("    [4] write_file     [5] web_search    [6] read_webpage")
    print("    [7] memory_search  [8] memory_add\n")

    tool_pick = input("  Pick tool (number or name): ").strip()
    if not tool_pick:
        return
    num_map = {
        "1": "xonsh", "2": "read_file", "3": "edit_file", "4": "write_file",
        "5": "web_search", "6": "read_webpage", "7": "memory_search", "8": "memory_add"
    }
    new_name = num_map.get(tool_pick, tool_pick)
    if new_name not in available_tools:
        print(f"  Unknown tool '{new_name}'.")
        return

    # Collect args interactively
    args = _collect_args_for_tool(new_name)
    if args is None:
        return

    tc_id = _next_id()
    tc = {
        "id": tc_id,
        "type": "function",
        "function": {"name": new_name, "arguments": json.dumps(args)}
    }

    # Replay prior actions to restore environment state (venv, files, etc.),
    # including actions already in this turn before the new step.
    prior_in_turn = [s for s in turn["steps"] if s["type"] == "action" and s.get("result")]
    _replay_prior_actions(turns, current_turn_idx, prior_steps_in_turn=prior_in_turn)

    # Execute to get result
    print("\n  Executing...")
    try:
        out = _execute_tool(new_name, args)
        res_text = out.strip() if out.strip() else "(empty output)"
        result_msg = {"role": "tool", "tool_call_id": tc_id, "name": new_name, "content": res_text}
        print(f"  Result ({len(res_text)} chars):")
        for rline in res_text.split("\n")[:5]:
            print(f"    {rline}")
        if len(res_text.split("\n")) > 5:
            print(f"    ... [{len(res_text.split(chr(10)))-5} more lines]")
    except subprocess.TimeoutExpired:
        res_text = "Execution timed out (30s)"
        result_msg = {"role": "tool", "tool_call_id": tc_id, "name": new_name, "content": res_text}
    except Exception as e:
        res_text = str(e)
        result_msg = {"role": "tool", "tool_call_id": tc_id, "name": new_name, "content": str(e)}

    turn["steps"].append({"type": "action", "tool_call": tc, "result": result_msg})
    print("  Action added.")


def _collect_args_for_tool(name):
    """Interactively collect args for a tool. Returns dict or None on cancel."""
    if name == "xonsh":
        code = input("\n  Code/command: ").strip()
        return {"code": code} if code else None

    elif name == "read_file":
        path = input("\n  File path: ").strip()
        if not path:
            return None
        args = {"path": path}
        sl = input("  Start line [1]: ").strip() or None
        el = input("  End line [all]: ").strip() or None
        if sl:
            args["start_line"] = int(sl)
        if el:
            args["end_line"] = int(el)
        return args

    elif name == "edit_file":
        path = input("\n  File path: ").strip()
        if not path:
            return None
        old_t = input("  Old text (exact): ")
        new_t = input("  New text: ")
        return {"path": path, "old_text": old_t, "new_text": new_t}

    elif name == "write_file":
        path = input("\n  File path: ").strip()
        if not path:
            return None
        lines = []
        print("  Content (empty line to end):")
        while True:
            l = input("    ")
            if l == "":
                break
            lines.append(l)
        return {"path": path, "content": "\n".join(lines)}

    elif name == "web_search":
        q = input("\n  Search query: ").strip()
        if not q:
            return None
        nr = input("  Num results [5]: ").strip() or "5"
        return {"query": q, "num_results": int(nr)}

    elif name == "read_webpage":
        url = input("\n  URL: ").strip()
        if not url:
            return None
        ml = input("  Max length [8000]: ").strip() or "8000"
        return {"url": url, "max_length": int(ml)}

    elif name == "memory_search":
        q = input("\n  Search query: ").strip()
        return {"query": q} if q else None

    elif name == "memory_add":
        txt = input("\n  Text to add: ").strip()
        return {"text": txt} if txt else None

    return None


def _reorder_steps(turn):
    """Let user reorder steps by specifying a new order."""
    print(f"\n  Current order ({len(turn['steps'])} steps):")
    for si, step in enumerate(turn["steps"]):
        if step["type"] == "reasoning":
            preview = step["text"][:50].replace("\n", " ")
            print(f"    {si}: Reasoning \"{preview}\"")
        elif step["type"] == "response":
            preview = step["text"][:50].replace("\n", " ")
            print(f"    {si}: Response \"{preview}\"")
        elif step["type"] == "action":
            cmd = get_tool_command(step["tool_call"])[:45]
            print(f"    {si}: Action {cmd}")

    order_str = input(f"\n  New order (comma-separated indices, e.g. '2,0,1'): ").strip()
    if not order_str:
        return
    try:
        new_order = [int(x.strip()) for x in order_str.split(",")]
        if set(new_order) != set(range(len(turn["steps"]))):
            print("  Invalid — must contain each index exactly once.")
            return
        reordered = [turn["steps"][i] for i in new_order]
        turn["steps"] = reordered
        print("  Reordered.")
    except ValueError:
        print("  Invalid format.")


def apply_turns_to_messages(messages, turns):
    """Reconstruct flat messages list from step-based turns.

    Simple mapping: each reasoning step → assistant text message.
    Each action step → assistant tool_call message + tool result message.
    Consecutive reasoning steps are merged into one message to keep it clean.
    Reasoning immediately before an action is merged as `content` on the tool-call msg.
    """
    new_messages = []

    i = 0
    while i < len(messages) and messages[i]["role"] == "system":
        new_messages.append(messages[i])
        i += 1

    for turn in turns:
        new_messages.append(turn["user"])

        steps = turn["steps"]
        si = 0

        while si < len(steps):
            step = steps[si]

            if step["type"] == "reasoning":
                # Reasoning text is a visible assistant message before the action —
                # it shows what the agent was thinking. Matches real Assistant traces
                # where the model may emit a pre-action thought as text, then a separate
                # tool-call msg with empty content. Consecutive reasoning steps merged.
                text_parts = [step["text"]]
                si += 1
                while si < len(steps) and steps[si]["type"] == "reasoning":
                    text_parts.append(steps[si]["text"])
                    si += 1

                new_messages.append({"role": "assistant", "content": "\n\n".join(text_parts)})

            elif step["type"] == "response":
                # Visible reply — standalone assistant message.
                new_messages.append({"role": "assistant", "content": step["text"]})
                si += 1

            elif step["type"] == "action":
                tc = step["tool_call"]
                # Real Assistant format: tool-call msg has empty content, result separate.
                new_messages.append({"role": "assistant", "content": "", "tool_calls": [tc]})
                if step.get("result"):
                    new_messages.append(step["result"])
                si += 1

    return new_messages


# ── Wizard: trace review loop ──────────────────────────────────────

def review_trace(filepath, messages):
    """Walk through a trace turn by turn, asking for validation."""
    fname = os.path.basename(filepath)
    turns = get_turns(messages)

    # Show system prompt so the reviewer can check whether the assistant's intro
    # is appropriate for the environment (date, locale, pwd, tools available, etc.).
    sys_prompt = next((m.get("content", "") for m in messages if m.get("role") == "system"), None)
    if sys_prompt:
        print(f"\n  [SYSTEM PROMPT ({len(sys_prompt)} chars)] — preview:")
        print(f"{'─'*60}")
        prompt_lines = str(sys_prompt).split("\n")
        for line in prompt_lines[:12]:
            print(f"  {line}")
        if len(prompt_lines) > 12:
            print("  ... (truncated, use [P] to view the full system prompt)")

    print(f"\n{'='*70}")
    print(f"  REVIEWING: {fname}")
    print(f"  {len(turns)} turn(s) to review")
    print(f"{'='*70}")

    results = []
    tnum = 0

    while tnum < len(turns):
        turn = turns[tnum]
        resolved = False

        while not resolved:
            show_turn(tnum + 1, turn)
            choice = ask_turn_action()

            if choice == "v":
                results.append((tnum + 1, "validated"))
                print("  Turn validated.\n")
                resolved = True

            elif choice == "x":
                results.append((tnum + 1, "refused"))
                reason = input("  Reason (optional): ").strip()
                if reason:
                    print(f"  Noted: {reason}")
                print("  Turn refused.\n")
                resolved = True

            elif choice == "e":
                # Deep copy turn before editing so mutations don't leak if rejected
                backup = deepcopy(turn)
                edit_turn_content(backup, turns=turns, current_turn_idx=tnum)
                confirm = input("\n  Accept this edit? (y/N): ").strip().lower()
                if confirm == "y":
                    # Commit: replace original turn with edited copy
                    turns[tnum] = backup
                    results.append((tnum + 1, "edited"))
                    again = input("  Continue editing this turn? (Y/n to validate): ").strip().lower()
                    if again == "n":
                        resolved = True
                        print("  Turn accepted. Moving on...\n")
                    else:
                        # Re-parse from committed turns for accurate display
                        turn = turns[tnum]
                        print("  Re-displaying for verification...\n")
                else:
                    # Discard edits — backup is dropped, original 'turn' untouched
                    del backup
                    results.append((tnum + 1, "unchanged"))
                    print("  Edit discarded.\n")

            elif choice == "t":
                ri = 0
                for step in turn["steps"]:
                    if step["type"] == "action" and step.get("result"):
                        result_text = str(step["result"].get("content", ""))
                        lines = result_text.strip().split("\n")
                        print(f"\n    [FULL RESULT {ri+1}] ({len(lines)} lines):")
                        for line in lines:
                            print(f"      {clean_line(line)}")
                        ri += 1

            elif choice == "p":
                # View the full system prompt (messages[0] — skipped by get_turns).
                sys_prompt = next((m.get("content", "") for m in messages if m.get("role") == "system"), None)
                if sys_prompt:
                    print(f"\n  [FULL SYSTEM PROMPT ({len(sys_prompt)} chars)]:")
                    print(f"{'─'*60}")
                    for line in str(sys_prompt).split("\n"):
                        print(f"  {line}")
                else:
                    print("  No system prompt found in this trace.")

            elif choice == "s":
                results.append((tnum + 1, "skipped"))
                print("  Skipped.\n")
                resolved = True

        tnum += 1

    print(f"\n{'='*70}")
    print("  REVIEW SUMMARY")
    print(f"{'='*70}")
    for tnum, status in results:
        icon = {"validated": "+", "refused": "-", "edited": "~", "skipped": ">", "unchanged": "o"}
        print(f"  Turn {tnum}: {icon.get(status, '?')} {status}")

    return results, turns


# ── Main ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Interactive trace editor")
    parser.add_argument("--file", type=str, help="Edit a specific file")
    parser.add_argument("--status", default="pending",
                       choices=["all", "pending", "validated", "refused"],
                       help="Filter by status (default: pending)")
    args = parser.parse_args()

    state = load_state()

    if args.file:
        files = [args.file]
    else:
        files = get_sim_files(args.status)

    if not files:
        print("\n  No traces found.\n")
        return

    # Interactive curses picker
    selected = run_file_picker(files, state)

    if selected is None:
        print("\n  Quit.\n")
        return

    if not selected:
        print("\n  No files selected.\n")
        return

    for filepath in selected:
        fname = os.path.basename(filepath)
        messages, lines, data = load_trace(filepath)

        results, turns = review_trace(filepath, messages)

        # Save edits back to file (turns include all mutations from review)
        new_messages = apply_turns_to_messages(messages, turns)
        save_trace(new_messages, lines, data, filepath)

        print(f"\n  What to do with this trace?")
        print(f"    [V] Validate entire trace")
        print(f"    [R] Refuse entire trace")
        print(f"    [S] Mark as reviewed\n")

        file_choice = input("  -> ").strip().lower()

        if file_choice == "v":
            state[fname] = {"status": "validated", "edited_at": datetime.now().isoformat()}
            out_dir = SIM_DIR.replace("/sim_raw", "/output/validated")
            os.makedirs(out_dir, exist_ok=True)
            with open(filepath) as src:
                content = src.read()
            with open(os.path.join(out_dir, fname), "w") as dst:
                dst.write(content)
            print("  Validated.\n")

        elif file_choice == "r":
            state[fname] = {"status": "refused", "refused_at": datetime.now().isoformat()}
            print("  Refused.\n")

        else:
            state[fname] = {"status": "reviewed", "edited_at": datetime.now().isoformat()}
            print("  Marked as reviewed.\n")

    save_state(state)
    print("  Done. State saved.\n")


if __name__ == "__main__":
    main()
