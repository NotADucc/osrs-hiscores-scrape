from src.request.common import HSAccountTypes
from src.request.job import HSLookupJob
from src.request.results import PlayerRecord


@staticmethod
def map_player_record_to_job(priority: int, account_type: HSAccountTypes, input: PlayerRecord) -> HSLookupJob:
    """ function that maps a `PlayerRecord` to a `HSLookupJob` """
    return HSLookupJob(priority=priority, account_type=account_type, username=input.username)

@staticmethod
def map_player_records_to_jobs(account_type: HSAccountTypes, input: list[PlayerRecord]) -> list['HSLookupJob']:
    """ function that maps a list of `PlayerRecord` to a list of `HSLookupJob` """
    return [map_player_record_to_job(priority=idx, account_type=account_type, input=x) for idx, x in enumerate(input)]