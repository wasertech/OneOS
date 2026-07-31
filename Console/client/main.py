import sys

from pathlib import Path
from prompt_toolkit import PromptSession
from client.assistant import Assistant

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Assistant is the shell.', add_help=True)
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Debug mode.",
    )
    parser.add_argument(
        "-c",
        help="Run a single command and exit.",
        dest="command",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-i",
        "--interactive",
        help="Force running in interactive mode.",
        dest="force_interactive",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "file",
        metavar="script-file",
        help="If present, execute the script in script-file or (if not present) execute as a command" " and exit.",
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "args",
        metavar="args",
        help="Additional arguments to the script (or command) specified " "by script-file.",
        nargs=argparse.REMAINDER,
        default=[],
    )
    return parser.parse_args()

def main():
    # get parsed args
    args = parse_args()
    sys.exit(main_assistant(args))

def main_assistant(args):
    assistant = Assistant()
    exit_code = 0

    if args.command:
        # Single command from argument
        assistant.single_command(args.command)
    elif args.file:
        # Script from file
        if Path(args.file).exists():
            assistant.script_from_file(args.file, args.args)
        else:
            # or Interpret as command instead
            command = f"{str(args.file)} {str(' '.join(args.args))}".lstrip()
            assistant.single_command(command)
    elif not sys.stdin.isatty() and not args.force_interactive:
        # Script from stdin
        code = sys.stdin.read()
        assistant.script_from_stdin(code)
    else:
        # Interactive Mode (command loop)
        assistant.interactive_mode()
    return exit_code