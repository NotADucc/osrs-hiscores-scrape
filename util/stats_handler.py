from request.common import HSApiCsvMapper, HSApi
from request.request import lookup
from util.common import StatsFlag, calc_cmb


def get_stats(name: str, account_type: HSApi, flags: StatsFlag = StatsFlag.default, **kwargs) -> dict:
    csv = lookup(name, account_type.csv()).split('\n')

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
