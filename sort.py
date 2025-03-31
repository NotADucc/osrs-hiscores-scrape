import argparse
import sys
import logging


def main(in_file):
    with open(in_file, "r") as file:
        lines = file.readlines()

    sorted_lines = sorted(lines, key=lambda x: int(x.split(",")[0]))

    with open(in_file, "w") as file:
        file.writelines(sorted_lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', required=True)
    args = parser.parse_args()

    main(args.in_file)

    logging.info("done")
    sys.exit(0)
