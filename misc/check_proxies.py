import argparse
import json
import sys
import threading

import requests
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.log import get_logger
from util.retry_handler import retry
from util.threading_handler import spawn_threads


logger = get_logger()
file_lock = threading.Lock()


def process(proxy: str, **args: dict) -> None:
    out_file = args["out_file"]
    try:
        if proxy.startswith(("https://", "http://", "socks4://", "socks5://")):
            proxy_url = proxy
            print(proxy_url)
        else:
            # ip, port, user, pwd
            splitted = proxy.split(":")
            proxy_url = f"http://{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}" \
                if len(splitted) > 2 \
                else f"http://{splitted[0]}:{splitted[1]}"

        res = requests.get("http://ipinfo.io/json",
                           proxies={"http": proxy_url, "https": proxy_url})
        if res.status_code == 200:
            with file_lock:
                with open(out_file, "a") as f:
                    f.write(f'{proxy_url}\n')
            logger.info(f'{json.loads(res.text)["ip"]}')
        else:
            logger.error(f'failed {proxy_url} | {res.status_code}')

    except Exception as err:
        print(err)


def main(proxy_file: str):
    with open(proxy_file, "r") as f:
        proxies = f.read().splitlines()

    splitted = proxy_file.split('.')
    valid_file = splitted[0] + "_valid." + splitted[1]
    spawn_threads(process, proxies, out_file=valid_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy-file', required=True,
                        help="Path to the proxy file")
    running_script_not_in_cmd_guard(parser)

    args = parser.parse_args()

    main(args.proxy_file)
    logger.debug("done")
    sys.exit(0)
