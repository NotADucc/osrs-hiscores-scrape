import argparse
from enum import Enum


class RequestFailed(Exception):
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(message)


class IsRateLimited(Exception):
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(message)


class HSLookup(Enum):
    regular = {
        'overall': 'https://secure.runescape.com/m=hiscore_oldschool/overall',
        'personal': 'https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal'
    }
    pure = {
        'overall': 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/overall',
        'personal': 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/hiscorepersonal'
    }
    im = {
        'overall': 'https://secure.runescape.com/m=hiscore_oldschool_ironman/overall',
        'personal': 'https://secure.runescape.com/m=hiscore_oldschool_ironman/hiscorepersonal'
    }
    uim = {
        'overall': 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/overall',
        'personal': 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/hiscorepersonal'
    }
    hc = {
        'overall': 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/overall',
        'personal': 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/hiscorepersonal'
    }
    skiller = {
        'overall': 'https://secure.runescape.com/m=hiscore_oldschool_skiller/overall',
        'personal': 'https://secure.runescape.com/m=hiscore_oldschool_skiller/hiscorepersonal'
    }

    def overall(self) -> str:
        return self.value['overall']

    def personal(self) -> str:
        return self.value['personal']

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_string(s: str) -> 'HSLookup':
        try:
            return HSLookup[s]
        except KeyError:
            valid_values = ', '.join(HSLookup.__members__.keys())
            raise argparse.ArgumentTypeError(valid_values)


class HSApi(Enum):
    regular = {
        'csv': 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws',
        'json': 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.json',
    },
    pure = {
        'csv': 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/index_lite.ws',
        'json': 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/index_lite.json',
    },
    im = {
        'csv': 'https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws',
        'json': 'https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json',
    },
    uim = {
        'csv': 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.ws',
        'json': 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.json',
    },
    hc = {
        'csv': 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws',
        'json': 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.json',
    },
    skiller = {
        'csv': 'https://secure.runescape.com/m=hiscore_oldschool_skiller/index_lite.ws',
        'json': 'https://secure.runescape.com/m=hiscore_oldschool_skiller/index_lite.json',
    }

    def __str__(self):
        return self.name

    def csv(self) -> str:
        return self.value['csv']

    def json(self) -> str:
        return self.value['json']

    @staticmethod
    def from_string(s: str) -> 'HSApi':
        try:
            return HSApi[s]
        except KeyError:
            valid_values = ', '.join(HSApi.__members__.keys())
            raise argparse.ArgumentTypeError(valid_values)


hs_overall_table_mapper_skills = 0
hs_overall_table_mapper_rest = 0


def hs_overall_table_mapper_increment(cat_type):
    global hs_overall_table_mapper_skills, hs_overall_table_mapper_rest

    if cat_type == 0:
        res = hs_overall_table_mapper_skills
        hs_overall_table_mapper_skills += 1
    else:
        res = hs_overall_table_mapper_rest
        hs_overall_table_mapper_rest += 1

    return res


hs_api_csv_mapper_value = 0


def hs_api_csv_mapper_increment():
    global hs_api_csv_mapper_value
    hs_api_csv_mapper_value += 1
    return hs_api_csv_mapper_value - 1


class HSCategoryMapper(Enum):
    overall = hs_overall_table_mapper_increment(0)
    attack = hs_overall_table_mapper_increment(0)
    defence = hs_overall_table_mapper_increment(0)
    strength = hs_overall_table_mapper_increment(0)
    hitpoints = hs_overall_table_mapper_increment(0)
    ranged = hs_overall_table_mapper_increment(0)
    prayer = hs_overall_table_mapper_increment(0)
    magic = hs_overall_table_mapper_increment(0)
    cooking = hs_overall_table_mapper_increment(0)
    woodcutting = hs_overall_table_mapper_increment(0)
    fletching = hs_overall_table_mapper_increment(0)
    fishing = hs_overall_table_mapper_increment(0)
    firemaking = hs_overall_table_mapper_increment(0)
    crafting = hs_overall_table_mapper_increment(0)
    smithing = hs_overall_table_mapper_increment(0)
    mining = hs_overall_table_mapper_increment(0)
    herblore = hs_overall_table_mapper_increment(0)
    agility = hs_overall_table_mapper_increment(0)
    thieving = hs_overall_table_mapper_increment(0)
    slayer = hs_overall_table_mapper_increment(0)
    farming = hs_overall_table_mapper_increment(0)
    runecrafting = hs_overall_table_mapper_increment(0)
    hunter = hs_overall_table_mapper_increment(0)
    construction = hs_overall_table_mapper_increment(0)
    # start non skilling stuff, for some reason its split up in 2
    league_points = hs_overall_table_mapper_increment(1)
    dmm = hs_overall_table_mapper_increment(1)
    bh_hunter = hs_overall_table_mapper_increment(1)
    bh_rogue = hs_overall_table_mapper_increment(1)
    bh_legacy_hunter = hs_overall_table_mapper_increment(1)
    bh_legacy_rogue = hs_overall_table_mapper_increment(1)
    cs_all = hs_overall_table_mapper_increment(1)
    cs_beginner = hs_overall_table_mapper_increment(1)
    cs_easy = hs_overall_table_mapper_increment(1)
    cs_medium = hs_overall_table_mapper_increment(1)
    cs_hard = hs_overall_table_mapper_increment(1)
    cs_elite = hs_overall_table_mapper_increment(1)
    cs_master = hs_overall_table_mapper_increment(1)
    lms_rank = hs_overall_table_mapper_increment(1)
    pvp_arena_rank = hs_overall_table_mapper_increment(1)
    sw_zeal = hs_overall_table_mapper_increment(1)
    rifts_closed = hs_overall_table_mapper_increment(1)
    colosseum_glory = hs_overall_table_mapper_increment(1)
    collections_logged = hs_overall_table_mapper_increment(1)
    sire = hs_overall_table_mapper_increment(1)
    hydra = hs_overall_table_mapper_increment(1)
    amoxliatl = hs_overall_table_mapper_increment(1)
    araxxor = hs_overall_table_mapper_increment(1)
    artio = hs_overall_table_mapper_increment(1)
    barrows_chests = hs_overall_table_mapper_increment(1)
    bryophyta = hs_overall_table_mapper_increment(1)
    callisto = hs_overall_table_mapper_increment(1)
    calvarion = hs_overall_table_mapper_increment(1)
    cerberus = hs_overall_table_mapper_increment(1)
    cox = hs_overall_table_mapper_increment(1)
    cox_cm = hs_overall_table_mapper_increment(1)
    chaos_elemental = hs_overall_table_mapper_increment(1)
    chaos_fanatic = hs_overall_table_mapper_increment(1)
    saradomin = hs_overall_table_mapper_increment(1)
    corp = hs_overall_table_mapper_increment(1)
    crazy_archaeologist = hs_overall_table_mapper_increment(1)
    dks_prime = hs_overall_table_mapper_increment(1)
    dks_rex = hs_overall_table_mapper_increment(1)
    dks_supreme = hs_overall_table_mapper_increment(1)
    deranged_archaeologist = hs_overall_table_mapper_increment(1)
    duke = hs_overall_table_mapper_increment(1)
    bandos = hs_overall_table_mapper_increment(1)
    giant_mole = hs_overall_table_mapper_increment(1)
    gg = hs_overall_table_mapper_increment(1)
    hespori = hs_overall_table_mapper_increment(1)
    kq = hs_overall_table_mapper_increment(1)
    kbd = hs_overall_table_mapper_increment(1)
    kraken = hs_overall_table_mapper_increment(1)
    armadyl = hs_overall_table_mapper_increment(1)
    zamorak = hs_overall_table_mapper_increment(1)
    lunar_chests = hs_overall_table_mapper_increment(1)
    mimic = hs_overall_table_mapper_increment(1)
    nex = hs_overall_table_mapper_increment(1)
    nightmare = hs_overall_table_mapper_increment(1)
    psn = hs_overall_table_mapper_increment(1)
    obor = hs_overall_table_mapper_increment(1)
    phantom_muspah = hs_overall_table_mapper_increment(1)
    sarachnis = hs_overall_table_mapper_increment(1)
    scorpia = hs_overall_table_mapper_increment(1)
    scurrius = hs_overall_table_mapper_increment(1)
    skotizo = hs_overall_table_mapper_increment(1)
    sol = hs_overall_table_mapper_increment(1)
    spindel = hs_overall_table_mapper_increment(1)
    tempoross = hs_overall_table_mapper_increment(1)
    gauntlet = hs_overall_table_mapper_increment(1)
    cg = hs_overall_table_mapper_increment(1)
    hueycoatl = hs_overall_table_mapper_increment(1)
    leviathan = hs_overall_table_mapper_increment(1)
    royal_titans = hs_overall_table_mapper_increment(1)
    whisperer = hs_overall_table_mapper_increment(1)
    tob = hs_overall_table_mapper_increment(1)
    hmt = hs_overall_table_mapper_increment(1)
    thermy = hs_overall_table_mapper_increment(1)
    toa = hs_overall_table_mapper_increment(1)
    toa_em = hs_overall_table_mapper_increment(1)
    zuk = hs_overall_table_mapper_increment(1)
    jad = hs_overall_table_mapper_increment(1)
    vardorvis = hs_overall_table_mapper_increment(1)
    venenatis = hs_overall_table_mapper_increment(1)
    vetion = hs_overall_table_mapper_increment(1)
    vorkath = hs_overall_table_mapper_increment(1)
    wt = hs_overall_table_mapper_increment(1)
    yama = hs_overall_table_mapper_increment(1)
    zalcano = hs_overall_table_mapper_increment(1)
    zulrah = hs_overall_table_mapper_increment(1)

    def get_category(self) -> int:
        return 0 if HSCategoryMapper.overall.value <= self.value <= HSCategoryMapper.construction.value else 1

    def debug() -> list:
        return [f'{v}: {v.value}' for v in HSCategoryMapper]

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_string(s: str) -> 'HSCategoryMapper':
        try:
            return HSCategoryMapper[s]
        except KeyError:
            valid_values = ', '.join(HSCategoryMapper.__members__.keys())
            raise argparse.ArgumentTypeError(valid_values)


class HSApiCsvMapper(Enum):
    overall = hs_api_csv_mapper_increment()
    attack = hs_api_csv_mapper_increment()
    defence = hs_api_csv_mapper_increment()
    strength = hs_api_csv_mapper_increment()
    hitpoints = hs_api_csv_mapper_increment()
    ranged = hs_api_csv_mapper_increment()
    prayer = hs_api_csv_mapper_increment()
    magic = hs_api_csv_mapper_increment()
    cooking = hs_api_csv_mapper_increment()
    woodcutting = hs_api_csv_mapper_increment()
    fletching = hs_api_csv_mapper_increment()
    fishing = hs_api_csv_mapper_increment()
    firemaking = hs_api_csv_mapper_increment()
    crafting = hs_api_csv_mapper_increment()
    smithing = hs_api_csv_mapper_increment()
    mining = hs_api_csv_mapper_increment()
    herblore = hs_api_csv_mapper_increment()
    agility = hs_api_csv_mapper_increment()
    thieving = hs_api_csv_mapper_increment()
    slayer = hs_api_csv_mapper_increment()
    farming = hs_api_csv_mapper_increment()
    runecrafting = hs_api_csv_mapper_increment()
    hunter = hs_api_csv_mapper_increment()
    construction = hs_api_csv_mapper_increment()
    league_points = hs_api_csv_mapper_increment()
    dmm = hs_api_csv_mapper_increment()
    bh_hunter = hs_api_csv_mapper_increment()
    bh_rogue = hs_api_csv_mapper_increment()
    bh_legacy_hunter = hs_api_csv_mapper_increment()
    bh_legacy_rogue = hs_api_csv_mapper_increment()
    cs_all = hs_api_csv_mapper_increment()
    cs_beginner = hs_api_csv_mapper_increment()
    cs_easy = hs_api_csv_mapper_increment()
    cs_medium = hs_api_csv_mapper_increment()
    cs_hard = hs_api_csv_mapper_increment()
    cs_elite = hs_api_csv_mapper_increment()
    cs_master = hs_api_csv_mapper_increment()
    lms_rank = hs_api_csv_mapper_increment()
    pvp_arena_rank = hs_api_csv_mapper_increment()
    sw_zeal = hs_api_csv_mapper_increment()
    rifts_closed = hs_api_csv_mapper_increment()
    colosseum_glory = hs_api_csv_mapper_increment()
    collections_logged = hs_api_csv_mapper_increment()
    sire = hs_api_csv_mapper_increment()
    hydra = hs_api_csv_mapper_increment()
    amoxliatl = hs_api_csv_mapper_increment()
    araxxor = hs_api_csv_mapper_increment()
    artio = hs_api_csv_mapper_increment()
    barrows_chests = hs_api_csv_mapper_increment()
    bryophyta = hs_api_csv_mapper_increment()
    callisto = hs_api_csv_mapper_increment()
    calvarion = hs_api_csv_mapper_increment()
    cerberus = hs_api_csv_mapper_increment()
    cox = hs_api_csv_mapper_increment()
    cox_cm = hs_api_csv_mapper_increment()
    chaos_elemental = hs_api_csv_mapper_increment()
    chaos_fanatic = hs_api_csv_mapper_increment()
    saradomin = hs_api_csv_mapper_increment()
    corp = hs_api_csv_mapper_increment()
    crazy_archaeologist = hs_api_csv_mapper_increment()
    dks_prime = hs_api_csv_mapper_increment()
    dks_rex = hs_api_csv_mapper_increment()
    dks_supreme = hs_api_csv_mapper_increment()
    deranged_archaeologist = hs_api_csv_mapper_increment()
    duke = hs_api_csv_mapper_increment()
    bandos = hs_api_csv_mapper_increment()
    giant_mole = hs_api_csv_mapper_increment()
    gg = hs_api_csv_mapper_increment()
    hespori = hs_api_csv_mapper_increment()
    kq = hs_api_csv_mapper_increment()
    kbd = hs_api_csv_mapper_increment()
    kraken = hs_api_csv_mapper_increment()
    armadyl = hs_api_csv_mapper_increment()
    zamorak = hs_api_csv_mapper_increment()
    lunar_chests = hs_api_csv_mapper_increment()
    mimic = hs_api_csv_mapper_increment()
    nex = hs_api_csv_mapper_increment()
    nightmare = hs_api_csv_mapper_increment()
    psn = hs_api_csv_mapper_increment()
    obor = hs_api_csv_mapper_increment()
    phantom_muspah = hs_api_csv_mapper_increment()
    royal_titans = hs_api_csv_mapper_increment()
    sarachnis = hs_api_csv_mapper_increment()
    scorpia = hs_api_csv_mapper_increment()
    scurrius = hs_api_csv_mapper_increment()
    skotizo = hs_api_csv_mapper_increment()
    sol = hs_api_csv_mapper_increment()
    spindel = hs_api_csv_mapper_increment()
    tempoross = hs_api_csv_mapper_increment()
    gauntlet = hs_api_csv_mapper_increment()
    cg = hs_api_csv_mapper_increment()
    hueycoatl = hs_api_csv_mapper_increment()
    leviathan = hs_api_csv_mapper_increment()
    whisperer = hs_api_csv_mapper_increment()
    tob = hs_api_csv_mapper_increment()
    tob_hm = hs_api_csv_mapper_increment()
    thermy = hs_api_csv_mapper_increment()
    toa = hs_api_csv_mapper_increment()
    toa_em = hs_api_csv_mapper_increment()
    zuk = hs_api_csv_mapper_increment()
    jad = hs_api_csv_mapper_increment()
    vardorvis = hs_api_csv_mapper_increment()
    venenatis = hs_api_csv_mapper_increment()
    vetion = hs_api_csv_mapper_increment()
    vorkath = hs_api_csv_mapper_increment()
    wt = hs_api_csv_mapper_increment()
    yama = hs_api_csv_mapper_increment()
    zalcano = hs_api_csv_mapper_increment()
    zulrah = hs_api_csv_mapper_increment()
    combat = -1

    def is_skill(self) -> bool:
        return HSApiCsvMapper.overall.value <= self.value <= HSApiCsvMapper.construction.value

    def is_combat(self) -> bool:
        return self.name in {
            "attack", "defence", "strength", "hitpoints",
            "ranged", "prayer", "magic", "combat"
        }

    def debug() -> list:
        return [f'{v}: {v.value}' for v in HSApiCsvMapper]

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_string(s: str) -> 'HSApiCsvMapper':
        try:
            return HSApiCsvMapper[s]
        except KeyError:
            valid_values = ', '.join(HSApiCsvMapper.__members__.keys())
            raise argparse.ArgumentTypeError(valid_values)
