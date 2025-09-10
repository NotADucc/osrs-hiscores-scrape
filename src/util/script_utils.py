import argparse
import os
import sys

import psutil


def argparse_wrapper(func):
    """Wrap a converter function to turn KeyError into ArgumentTypeError."""
    def wrapped(s: str):
        try:
            return func(s)
        except KeyError as e:
            raise argparse.ArgumentTypeError(str(e))
    return wrapped


def script_running_in_cmd_guard():
    """
        Guard clause to try and ensure the script is executed from a real terminal
        (cmd, PowerShell, bash, zsh, etc.), not by double-clicking in a file manager.
    """
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        _exit_with_message(
            "This script must be run from a terminal, not as a background process.")

    parent = psutil.Process(os.getppid()).parent()
    parent_name = parent.name().lower() if parent else ""
    if any(x in parent_name for x in {"finder", "nautilus", "dolphin", "explorer", "explorer.exe"}):
        _exit_with_message(
            "This script must be run from a terminal (bash, zsh, etc.), not the file manager.")


def _exit_with_message(msg: str):
    """Helper to show a red error message and exit."""
    print(f"\033[91m{msg}\033[0m\n", file=sys.stderr)
    print("Read the README for more information.")
    input("Press Enter to exit...")
    sys.exit(1)
