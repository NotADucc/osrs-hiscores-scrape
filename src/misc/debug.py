import sys

from src.request.common import HSType
from src.util.log import get_logger, log_execution

logger = get_logger()


@log_execution
def main():
    hs_debug = HSType.debug()
    logger.debug('\n'.join(hs_debug))
    logger.debug(str(len(hs_debug)))
    input()


if __name__ == '__main__':
    main()
    sys.exit(0)
