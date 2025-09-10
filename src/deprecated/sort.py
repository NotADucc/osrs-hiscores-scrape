import argparse
import json
import sys

from src.util.log import get_logger
from src.util.script_utils import script_running_in_cmd_guard

logger = get_logger()


def main(in_file):
    with open(in_file, "r") as file:
        lines = file.readlines()

    sorted_lines = sorted(lines, key=lambda x: json.loads(x)["rank"])

    with open(in_file, "w") as file:
        file.writelines(sorted_lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Sort lines in a file based on the first column")
    parser.add_argument('--in-file', required=True,
                        help="Path to the input file")

    script_running_in_cmd_guard()
    args = parser.parse_args()

    main(args.in_file)

    logger.info("done")
    sys.exit(0)
