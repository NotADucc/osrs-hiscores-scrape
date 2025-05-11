import argparse
import sys
from util.log import get_logger

logger = get_logger()


def main(in_file, delimiter):
    with open(in_file, "r") as file:
        lines = file.readlines()

    sorted_lines = sorted(lines, key=lambda x: int(x.split(delimiter)[0]))

    with open(in_file, "w") as file:
        file.writelines(sorted_lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', required=True)
    parser.add_argument('--delimiter', default=',')
    args = parser.parse_args()

    main(args.in_file, args.delimiter)

    logger.info("done")
    sys.exit(0)
