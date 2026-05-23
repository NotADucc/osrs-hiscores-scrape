import re
from argparse import ArgumentParser

from osrs_hiscore_scrape.cli.helpers import argparse_wrapper
from osrs_hiscore_scrape.request.dto import HSFilterEntry
from osrs_hiscore_scrape.request.hs_account_types import HSAccountTypes
from osrs_hiscore_scrape.request.hs_types import HSType
from osrs_hiscore_scrape.worker.constants import DEFAULT_WORKER_SIZE


class OSRSArgumentParser(ArgumentParser):

    def proxy_file(self, required: bool = False) -> 'OSRSArgumentParser':
        self.add_argument(
            "--proxy-file",
            "--proxy",
            "-p",
            dest='proxy_file',
            required=required,
            help="Path to the proxy file"
        )
        return self

    def output_file(self, required: bool = False) -> 'OSRSArgumentParser':
        self.add_argument(
            "--out-file",
            "--out",
            "-o",
            dest="output_file",
            required=required,
            help="Path to the output file"
        )
        return self

    def input_file(self, required: bool = False) -> 'OSRSArgumentParser':
        self.add_argument(
            '--in-file',
            '--input',
            '-i',
            dest="input_file",
            required=required,
            help="Path to the input file. Reads from highscores if omitted"
        )
        return self

    def username(self, required: bool = False) -> 'OSRSArgumentParser':
        self.add_argument(
            '--username',
            '--name',
            dest='username',
            required=required,
            help="OSRS player name to lookup"
        )
        return self

    def account_type(self, required: bool = False, default: HSAccountTypes | None = HSAccountTypes.main) -> 'OSRSArgumentParser':
        self.add_argument(
            '--account-type',
            '--account',
            dest="account_type",
            default=default,
            required=required,
            type=argparse_wrapper(HSAccountTypes.from_string),
            choices=list(HSAccountTypes),
            help="OSRS account type to scrape hiscores from"
        )
        return self

    def hs_type(self, required: bool = False, default: HSType | None = HSType.overall) -> 'OSRSArgumentParser':
        self.add_argument(
            "--hs-type",
            "--hs",
            dest="hs_type",
            default=default,
            required=required,
            type=argparse_wrapper(HSType.from_string),
            choices=list(HSType),
            help="OSRS hiscore category to scrape from"
        )
        return self

    def filter(self, required: bool = False) -> 'OSRSArgumentParser':
        self.add_argument(
            '--filter',
            dest="filter",
            type=argparse_wrapper(_parse_key_value_pairs),
            required=required,
            help="Custom filter used to match accounts"
        )
        return self

    def num_workers(self, required: bool = False, default: int = DEFAULT_WORKER_SIZE) -> 'OSRSArgumentParser':
        self.add_argument(
            "--num-workers",
            "--workers",
            dest="num_workers",
            default=default,
            required=required,
            type=int,
            help=f"Number of concurrent scraping workers/threads"
        )
        return self

    def rank_range(self, required: bool = False) -> 'OSRSArgumentParser':
        self.add_argument(
            "--start-rank",
            "--start",
            dest="start_rank",
            default=1,
            required=required,
            type=int,
            help="Starting hiscore rank to scrape from"
        )

        self.add_argument(
            "--end-rank",
            "--end",
            dest="end_rank",
            default=-1,
            required=required,
            type=int,
            help="Ending hiscore rank to scrape to"
        )

        return self


def _parse_key_value_pairs(arg) -> list[HSFilterEntry]:
    kv_pairs = arg.split(',')
    result = []

    for pair in kv_pairs:
        match = re.match(r'\s*(.*?)\s*(<=|>=|=|<|>)\s*(.*?)\s*$', pair)
        if not match:
            raise ValueError(f"Invalid pair format: '{pair}'")

        key_str, op, value_str = match.groups()
        key = HSType.from_string(key_str.strip())
        value_str = value_str.strip()
        try:
            value = float(value_str)
            if value.is_integer():
                value = int(value)
        except ValueError:
            raise ValueError(f"Invalid number: {value_str}")

        if op == '=':
            def func(x, v=value): return x == v
        elif op == '<':
            def func(x, v=value): return x < v
        elif op == '>':
            def func(x, v=value): return x > v
        elif op == '<=':
            def func(x, v=value): return x <= v
        elif op == '>=':
            def func(x, v=value): return x >= v
        else:
            raise ValueError(f"Unsupported operator: '{op}'")

        result.append(HSFilterEntry(hstype=key, predicate=func))

    return result
