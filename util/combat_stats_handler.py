from request.common import HSApiCsvMapper, HSApi, HSLookup
from request.request import lookup, lookup_scrape, extract_stats
from util.common import calc_cmb


def get_combat_stats_api(_, name: str, account_type: str) -> float:
    csv = lookup(name, HSApi[account_type]).split(b'\n')

    att = int(csv[HSApiCsvMapper.attack.value].split(b',')[1])
    de = int(csv[HSApiCsvMapper.defence.value].split(b',')[1])
    st = int(csv[HSApiCsvMapper.strength.value].split(b',')[1])
    hp = int(csv[HSApiCsvMapper.hitpoints.value].split(b',')[1])
    ra = int(csv[HSApiCsvMapper.ranged.value].split(b',')[1])
    pr = int(csv[HSApiCsvMapper.prayer.value].split(b',')[1])
    ma = int(csv[HSApiCsvMapper.magic.value].split(b',')[1])

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


def get_combat_stats_scrape(_, name: str, account_type: str) -> float:
    page = lookup_scrape(name, HSLookup[account_type])
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
