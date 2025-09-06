import sys

from src.request.common import HSType
from src.util.log import log_execution, get_logger

logger = get_logger()


@log_execution
def main():
    logger.debug(', '.join(HSType.debug()))
    input()


if __name__ == '__main__':
    main()
    sys.exit(0)
