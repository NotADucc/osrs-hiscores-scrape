import sys
from argparse import ArgumentParser


def script_running_in_cmd_guard(parser: ArgumentParser):
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        print("\033[91m\nThis script must be run from the command line.\033[0m\n")
        print("Read the README for more information.")
        input("Press enter to exit...")
        sys.exit(1)
