from src.request.common import HSAccountTypes
from src.request.job import HSLookupJob
from src.request.results import CategoryRecord, PlayerRecord

def map_player_record_to_lookup_job(priority: int, account_type: HSAccountTypes, input: PlayerRecord) -> HSLookupJob:
    """ function that maps a `PlayerRecord` to a `HSLookupJob` """
    return HSLookupJob(priority=priority, account_type=account_type, username=input.username)


def map_player_records_to_lookup_jobs(account_type: HSAccountTypes, input: list[PlayerRecord]) -> list['HSLookupJob']:
    """ function that maps a list of `PlayerRecord` to a list of `HSLookupJob` """
    if not input:
        return []
    return [map_player_record_to_lookup_job(priority=idx, account_type=account_type, input=x) for idx, x in enumerate(input)]


def map_category_record_to_lookup_job(priority: int, account_type: HSAccountTypes, input: CategoryRecord) -> HSLookupJob:
    """ function that maps a `CategoryRecord` to a `HSLookupJob` """
    return HSLookupJob(priority=priority, account_type=account_type, username=input.username)


def map_category_records_to_lookup_jobs(account_type: HSAccountTypes, input: list[CategoryRecord]) -> list[HSLookupJob]:
    """ function that maps a list of `CategoryRecord` to a list of `HSLookupJob` """
    if not input:
        return []
    return [map_category_record_to_lookup_job(priority=idx, account_type=account_type, input=x) for idx, x in enumerate(input)]