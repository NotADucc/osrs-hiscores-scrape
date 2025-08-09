import sys

from request.common import HSType
from util.log import get_logger


logger = get_logger()


def main():
    logger.debug(HSType.debug())
    input()


if __name__ == '__main__':
    main()
    sys.exit(0)
