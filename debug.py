import sys
from request.common import HSApiCsvMapper, HSOverallTableMapper
from util.log import get_logger

logger = get_logger()


def main():
    logger.debug(HSOverallTableMapper.debug())
    logger.debug(HSApiCsvMapper.debug())

    input()

if __name__ == '__main__':
    main()
    sys.exit(0)
