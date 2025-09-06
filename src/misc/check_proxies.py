import argparse
import asyncio
import threading

import aiohttp

from src.deprecated.pool import execute
from src.util.guard_clause_handler import script_running_in_cmd_guard
from src.util.log import log_execution, get_logger

logger = get_logger()
file_lock = threading.Lock()


async def process(proxy: str, **kwargs) -> None:
    out_file: str = kwargs["out_file"]
    try:
        if proxy.startswith(("https://", "http://", "socks4://", "socks5://")):
            proxy_url = proxy
        else:
            # ip, port, user, pwd
            splitted = proxy.split(":")
            proxy_url = f"http://{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}" \
                if len(splitted) > 2 \
                else f"http://{splitted[0]}:{splitted[1]}"

        async with aiohttp.ClientSession() as session:
            async with session.get("http://httpbin.org/ip", proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    ip_info = await resp.json()
                    logger.info(f'{ip_info}')
                    with file_lock:
                        with open(out_file, "a", encoding="utf-8") as f:
                            f.write(f'{proxy_url}\n')
                else:
                    logger.error(f"{proxy_url} | status {resp.status}")

    except Exception as err:
        print(err)


@log_execution
async def main(proxy_file: str):
    with open(proxy_file, "r") as f:
        proxies = f.read().splitlines()

    splitted = proxy_file.split('.')
    valid_file = splitted[0] + "_valid." + splitted[1]
    await execute(process, proxies, out_file=valid_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy-file', required=True,
                        help="Path to the proxy file")
    script_running_in_cmd_guard()

    args = parser.parse_args()

    asyncio.run(main(args.proxy_file))
