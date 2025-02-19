from common import HSApiCsvMapper, HSApi, HSLookup, calc_cmb
from request import lookup


def transform_user_api(_, name, acc_type):
    csv = lookup(name, HSApi[acc_type]).split(b'\n')

    att = int(csv[HSApiCsvMapper.attack.value].split(b',')[1])
    de = int(csv[HSApiCsvMapper.defence.value].split(b',')[1])
    st = int(csv[HSApiCsvMapper.strength.value].split(b',')[1])
    hp = int(csv[HSApiCsvMapper.hitpoints.value].split(b',')[1])
    ra = int(csv[HSApiCsvMapper.ranged.value].split(b',')[1])
    pr = int(csv[HSApiCsvMapper.prayer.value].split(b',')[1])
    ma = int(csv[HSApiCsvMapper.magic.value].split(b',')[1])
    return calc_cmb(att, de, st, hp, ra, pr, ma)


def transform_user_scrape(_, name, acc_type):
    page = lookup_scrape(name, HSLookup[acc_type])
    extracted_stats = extract_stats(page)

    att = extracted_stats.get('Attack', {'lvl': 1})['lvl']
    de = extracted_stats.get('Defence', {'lvl': 1})['lvl']
    st = extracted_stats.get('Strength', {'lvl': 1})['lvl']
    hp = extracted_stats.get('Hitpoints', {'lvl': 10})['lvl']
    ra = extracted_stats.get('Ranged', {'lvl': 1})['lvl']
    pr = extracted_stats.get('Prayer', {'lvl': 1})['lvl']
    ma = extracted_stats.get('Magic', {'lvl': 1})['lvl']
    return calc_cmb(att, de, st, hp, ra, pr, ma)
