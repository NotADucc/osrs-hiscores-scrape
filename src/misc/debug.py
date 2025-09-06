import sys

from src.request.common import HSType
from src.util.log import get_logger, log_execution

logger = get_logger()


@log_execution
def main():
    logger.debug(', '.join(HSType.debug()))
    input()


if __name__ == '__main__':
    main()
    sys.exit(0)
