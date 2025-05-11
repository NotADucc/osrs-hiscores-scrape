from request.common import HSApiCsvMapper, HSApi, HSLookup
from request.request import lookup, lookup_scrape, extract_stats
from util.common import StatsFlag, calc_cmb


def get_stats_api(name: str, account_type: str, flags: StatsFlag = StatsFlag.default, **kwargs) -> dict:
    csv = lookup(name, HSApi[account_type]).split('\n')

    # i want cmb on first position when printed or written
    stats = {HSApiCsvMapper.combat.name: -1}

    add_skills = flags.__contains__(StatsFlag.add_skills)
    add_misc = flags.__contains__(StatsFlag.add_misc)

    for mapper_val in HSApiCsvMapper:
        if mapper_val.value == -1:
            continue

        val = int(csv[mapper_val.value].split(',')[1])
        if val == -1:
            continue

        if (not add_skills and mapper_val.is_skill() and not mapper_val.is_combat()) or (not add_misc and not mapper_val.is_skill()):
            continue

        stats[mapper_val.name] = val
    cmb_level = calc_cmb(stats[HSApiCsvMapper.attack.name], stats[HSApiCsvMapper.defence.name],
                         stats[HSApiCsvMapper.strength.name], stats[HSApiCsvMapper.hitpoints.name], stats[HSApiCsvMapper.ranged.name], stats[HSApiCsvMapper.prayer.name], stats[HSApiCsvMapper.magic.name])
    stats[HSApiCsvMapper.combat.name] = cmb_level

    return stats


def get_combat_stats_scrape(name: str, account_type: str, **kwargs) -> dict:
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
