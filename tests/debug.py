import sys

from ..osrs_hiscore_scrape.request.common import HSType
from ..osrs_hiscore_scrape.util.log import get_logger, log_execution

logger = get_logger(__name__)


@log_execution
def main():
    hs_debug = HSType.debug()
    logger.debug('\n'.join(hs_debug))
    logger.debug(str(len(hs_debug)))
    input()


if __name__ == '__main__':
    main()
    sys.exit(0)
