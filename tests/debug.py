import sys

from ..osrs_hiscore_scrape.log.logger import get_logger
from ..osrs_hiscore_scrape.request.hs_types import HSType

logger = get_logger(__name__)


def main():
    hs_debug = HSType.debug()
    logger.debug('\n'.join(hs_debug))
    logger.debug(str(len(hs_debug)))
    input()


if __name__ == '__main__':
    main()
    sys.exit(0)
