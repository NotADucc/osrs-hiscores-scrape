import sys

from src.request.common import HSType
from src.util.log import finished_script, get_logger

logger = get_logger()


@finished_script
def main():
    logger.debug(', '.join(HSType.debug()))
    input()


if __name__ == '__main__':
    main()
    sys.exit(0)
