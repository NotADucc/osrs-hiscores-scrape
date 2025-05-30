from deprecated.request import extract_stats, lookup_scrape
from request.common import HSLookup
from util.common import calc_cmb


def get_combat_stats_scrape(name: str, account_type: str, **kwargs) -> dict:
    page = lookup_scrape(name, HSLookup.from_string(account_type))
    extracted_stats = extract_stats(page)

    att = extracted_stats.get('Attack', {'lvl': 1})['lvl']
    de = extracted_stats.get('Defence', {'lvl': 1})['lvl']
    st = extracted_stats.get('Strength', {'lvl': 1})['lvl']
    hp = extracted_stats.get('Hitpoints', {'lvl': 10})['lvl']
    ra = extracted_stats.get('Ranged', {'lvl': 1})['lvl']
    pr = extracted_stats.get('Prayer', {'lvl': 1})['lvl']
    ma = extracted_stats.get('Magic', {'lvl': 1})['lvl']

    cmb_level = calc_cmb(att, de, st, hp, ra, pr, ma)

    stats = {
        'combat': cmb_level,
        'attack': att,
        'defence': de,
        'strength': st,
        'hitpoints': hp,
        'ranged': ra,
        'prayer': pr,
        'magic': ma
    }

    return stats