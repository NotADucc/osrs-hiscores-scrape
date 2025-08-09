import argparse
from enum import Enum

class HSAccountTypes(Enum):
    regular = 'hiscore_oldschool'
    pure = 'hiscore_oldschool_skiller_defence'
    im = 'hiscore_oldschool_ironman'
    uim = 'hiscore_oldschool_ultimate'
    hc = 'hiscore_oldschool_hardcore_ironman'
    skiller = 'hiscore_oldschool_skiller'

    def lookup_overall(self) -> str:
        return f'http://secure.runescape.com/m={self.value}/overall'

    def lookup_personal(self) -> str:
        return f'http://secure.runescape.com/m={self.value}/hiscorepersonal'

    def api_csv(self) -> str:
        return f'http://secure.runescape.com/m={self.value}/index_lite.ws'

    def api_json(self) -> str:
        return f'http://secure.runescape.com/m={self.value}/index_lite.json'

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s: str) -> 'HSAccountTypes':
        try:
            return HSAccountTypes[s]
        except KeyError:
            valid_values = ', '.join(HSAccountTypes.__members__.keys())
            raise argparse.ArgumentTypeError(valid_values)


class EnumIncrementer():
    def __init__(self, size: int = 1):
        self.arr = [0] * size

    def increment(self, idx: int = 0) -> int:
        res = self.arr[idx]
        self.arr[idx] += 1
        return res


HSCategoryMapperIncrementer = EnumIncrementer(2)


class HSCategoryMapper(Enum):
    overall = HSCategoryMapperIncrementer.increment(0)
    attack = HSCategoryMapperIncrementer.increment(0)
    defence = HSCategoryMapperIncrementer.increment(0)
    strength = HSCategoryMapperIncrementer.increment(0)
    hitpoints = HSCategoryMapperIncrementer.increment(0)
    ranged = HSCategoryMapperIncrementer.increment(0)
    prayer = HSCategoryMapperIncrementer.increment(0)
    magic = HSCategoryMapperIncrementer.increment(0)
    cooking = HSCategoryMapperIncrementer.increment(0)
    woodcutting = HSCategoryMapperIncrementer.increment(0)
    fletching = HSCategoryMapperIncrementer.increment(0)
    fishing = HSCategoryMapperIncrementer.increment(0)
    firemaking = HSCategoryMapperIncrementer.increment(0)
    crafting = HSCategoryMapperIncrementer.increment(0)
    smithing = HSCategoryMapperIncrementer.increment(0)
    mining = HSCategoryMapperIncrementer.increment(0)
    herblore = HSCategoryMapperIncrementer.increment(0)
    agility = HSCategoryMapperIncrementer.increment(0)
    thieving = HSCategoryMapperIncrementer.increment(0)
    slayer = HSCategoryMapperIncrementer.increment(0)
    farming = HSCategoryMapperIncrementer.increment(0)
    runecrafting = HSCategoryMapperIncrementer.increment(0)
    hunter = HSCategoryMapperIncrementer.increment(0)
    construction = HSCategoryMapperIncrementer.increment(0)
    # start non skilling stuff, for some reason its split up in 2
    league_points = HSCategoryMapperIncrementer.increment(1)
    dmm = HSCategoryMapperIncrementer.increment(1)
    bh_hunter = HSCategoryMapperIncrementer.increment(1)
    bh_rogue = HSCategoryMapperIncrementer.increment(1)
    bh_legacy_hunter = HSCategoryMapperIncrementer.increment(1)
    bh_legacy_rogue = HSCategoryMapperIncrementer.increment(1)
    cs_all = HSCategoryMapperIncrementer.increment(1)
    cs_beginner = HSCategoryMapperIncrementer.increment(1)
    cs_easy = HSCategoryMapperIncrementer.increment(1)
    cs_medium = HSCategoryMapperIncrementer.increment(1)
    cs_hard = HSCategoryMapperIncrementer.increment(1)
    cs_elite = HSCategoryMapperIncrementer.increment(1)
    cs_master = HSCategoryMapperIncrementer.increment(1)
    lms_rank = HSCategoryMapperIncrementer.increment(1)
    pvp_arena_rank = HSCategoryMapperIncrementer.increment(1)
    sw_zeal = HSCategoryMapperIncrementer.increment(1)
    rifts_closed = HSCategoryMapperIncrementer.increment(1)
    colosseum_glory = HSCategoryMapperIncrementer.increment(1)
    collections_logged = HSCategoryMapperIncrementer.increment(1)
    # bosses
    sire = HSCategoryMapperIncrementer.increment(1)
    hydra = HSCategoryMapperIncrementer.increment(1)
    amoxliatl = HSCategoryMapperIncrementer.increment(1)
    araxxor = HSCategoryMapperIncrementer.increment(1)
    artio = HSCategoryMapperIncrementer.increment(1)
    barrows_chests = HSCategoryMapperIncrementer.increment(1)
    bryophyta = HSCategoryMapperIncrementer.increment(1)
    callisto = HSCategoryMapperIncrementer.increment(1)
    calvarion = HSCategoryMapperIncrementer.increment(1)
    cerberus = HSCategoryMapperIncrementer.increment(1)
    cox = HSCategoryMapperIncrementer.increment(1)
    cox_cm = HSCategoryMapperIncrementer.increment(1)
    chaos_elemental = HSCategoryMapperIncrementer.increment(1)
    chaos_fanatic = HSCategoryMapperIncrementer.increment(1)
    saradomin = HSCategoryMapperIncrementer.increment(1)
    corp = HSCategoryMapperIncrementer.increment(1)
    crazy_archaeologist = HSCategoryMapperIncrementer.increment(1)
    dks_prime = HSCategoryMapperIncrementer.increment(1)
    dks_rex = HSCategoryMapperIncrementer.increment(1)
    dks_supreme = HSCategoryMapperIncrementer.increment(1)
    deranged_archaeologist = HSCategoryMapperIncrementer.increment(1)
    doom_mokhaiotl = HSCategoryMapperIncrementer.increment(1)
    duke = HSCategoryMapperIncrementer.increment(1)
    bandos = HSCategoryMapperIncrementer.increment(1)
    giant_mole = HSCategoryMapperIncrementer.increment(1)
    gg = HSCategoryMapperIncrementer.increment(1)
    hespori = HSCategoryMapperIncrementer.increment(1)
    kq = HSCategoryMapperIncrementer.increment(1)
    kbd = HSCategoryMapperIncrementer.increment(1)
    kraken = HSCategoryMapperIncrementer.increment(1)
    armadyl = HSCategoryMapperIncrementer.increment(1)
    zamorak = HSCategoryMapperIncrementer.increment(1)
    lunar_chests = HSCategoryMapperIncrementer.increment(1)
    mimic = HSCategoryMapperIncrementer.increment(1)
    nex = HSCategoryMapperIncrementer.increment(1)
    nightmare = HSCategoryMapperIncrementer.increment(1)
    psn = HSCategoryMapperIncrementer.increment(1)
    obor = HSCategoryMapperIncrementer.increment(1)
    phantom_muspah = HSCategoryMapperIncrementer.increment(1)
    sarachnis = HSCategoryMapperIncrementer.increment(1)
    scorpia = HSCategoryMapperIncrementer.increment(1)
    scurrius = HSCategoryMapperIncrementer.increment(1)
    skotizo = HSCategoryMapperIncrementer.increment(1)
    sol = HSCategoryMapperIncrementer.increment(1)
    spindel = HSCategoryMapperIncrementer.increment(1)
    tempoross = HSCategoryMapperIncrementer.increment(1)
    gauntlet = HSCategoryMapperIncrementer.increment(1)
    cg = HSCategoryMapperIncrementer.increment(1)
    hueycoatl = HSCategoryMapperIncrementer.increment(1)
    leviathan = HSCategoryMapperIncrementer.increment(1)
    royal_titans = HSCategoryMapperIncrementer.increment(1)
    whisperer = HSCategoryMapperIncrementer.increment(1)
    tob = HSCategoryMapperIncrementer.increment(1)
    hmt = HSCategoryMapperIncrementer.increment(1)
    thermy = HSCategoryMapperIncrementer.increment(1)
    toa = HSCategoryMapperIncrementer.increment(1)
    toa_em = HSCategoryMapperIncrementer.increment(1)
    zuk = HSCategoryMapperIncrementer.increment(1)
    jad = HSCategoryMapperIncrementer.increment(1)
    vardorvis = HSCategoryMapperIncrementer.increment(1)
    venenatis = HSCategoryMapperIncrementer.increment(1)
    vetion = HSCategoryMapperIncrementer.increment(1)
    vorkath = HSCategoryMapperIncrementer.increment(1)
    wt = HSCategoryMapperIncrementer.increment(1)
    yama = HSCategoryMapperIncrementer.increment(1)
    zalcano = HSCategoryMapperIncrementer.increment(1)
    zulrah = HSCategoryMapperIncrementer.increment(1)

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


HSApiCsvMapperIncrementer = EnumIncrementer(1)


class HSApiCsvMapper(Enum):
    overall = HSApiCsvMapperIncrementer.increment()
    attack = HSApiCsvMapperIncrementer.increment()
    defence = HSApiCsvMapperIncrementer.increment()
    strength = HSApiCsvMapperIncrementer.increment()
    hitpoints = HSApiCsvMapperIncrementer.increment()
    ranged = HSApiCsvMapperIncrementer.increment()
    prayer = HSApiCsvMapperIncrementer.increment()
    magic = HSApiCsvMapperIncrementer.increment()
    cooking = HSApiCsvMapperIncrementer.increment()
    woodcutting = HSApiCsvMapperIncrementer.increment()
    fletching = HSApiCsvMapperIncrementer.increment()
    fishing = HSApiCsvMapperIncrementer.increment()
    firemaking = HSApiCsvMapperIncrementer.increment()
    crafting = HSApiCsvMapperIncrementer.increment()
    smithing = HSApiCsvMapperIncrementer.increment()
    mining = HSApiCsvMapperIncrementer.increment()
    herblore = HSApiCsvMapperIncrementer.increment()
    agility = HSApiCsvMapperIncrementer.increment()
    thieving = HSApiCsvMapperIncrementer.increment()
    slayer = HSApiCsvMapperIncrementer.increment()
    farming = HSApiCsvMapperIncrementer.increment()
    runecrafting = HSApiCsvMapperIncrementer.increment()
    hunter = HSApiCsvMapperIncrementer.increment()
    construction = HSApiCsvMapperIncrementer.increment()
    # start non skilling stuff
    league_points = HSApiCsvMapperIncrementer.increment()
    dmm = HSApiCsvMapperIncrementer.increment()
    bh_hunter = HSApiCsvMapperIncrementer.increment()
    bh_rogue = HSApiCsvMapperIncrementer.increment()
    bh_legacy_hunter = HSApiCsvMapperIncrementer.increment()
    bh_legacy_rogue = HSApiCsvMapperIncrementer.increment()
    cs_all = HSApiCsvMapperIncrementer.increment()
    cs_beginner = HSApiCsvMapperIncrementer.increment()
    cs_easy = HSApiCsvMapperIncrementer.increment()
    cs_medium = HSApiCsvMapperIncrementer.increment()
    cs_hard = HSApiCsvMapperIncrementer.increment()
    cs_elite = HSApiCsvMapperIncrementer.increment()
    cs_master = HSApiCsvMapperIncrementer.increment()
    lms_rank = HSApiCsvMapperIncrementer.increment()
    pvp_arena_rank = HSApiCsvMapperIncrementer.increment()
    sw_zeal = HSApiCsvMapperIncrementer.increment()
    rifts_closed = HSApiCsvMapperIncrementer.increment()
    colosseum_glory = HSApiCsvMapperIncrementer.increment()
    collections_logged = HSApiCsvMapperIncrementer.increment()
    # bosses
    sire = HSApiCsvMapperIncrementer.increment()
    hydra = HSApiCsvMapperIncrementer.increment()
    amoxliatl = HSApiCsvMapperIncrementer.increment()
    araxxor = HSApiCsvMapperIncrementer.increment()
    artio = HSApiCsvMapperIncrementer.increment()
    barrows_chests = HSApiCsvMapperIncrementer.increment()
    bryophyta = HSApiCsvMapperIncrementer.increment()
    callisto = HSApiCsvMapperIncrementer.increment()
    calvarion = HSApiCsvMapperIncrementer.increment()
    cerberus = HSApiCsvMapperIncrementer.increment()
    cox = HSApiCsvMapperIncrementer.increment()
    cox_cm = HSApiCsvMapperIncrementer.increment()
    chaos_elemental = HSApiCsvMapperIncrementer.increment()
    chaos_fanatic = HSApiCsvMapperIncrementer.increment()
    saradomin = HSApiCsvMapperIncrementer.increment()
    corp = HSApiCsvMapperIncrementer.increment()
    crazy_archaeologist = HSApiCsvMapperIncrementer.increment()
    dks_prime = HSApiCsvMapperIncrementer.increment()
    dks_rex = HSApiCsvMapperIncrementer.increment()
    dks_supreme = HSApiCsvMapperIncrementer.increment()
    deranged_archaeologist = HSApiCsvMapperIncrementer.increment()
    doom_mokhaiotl = HSApiCsvMapperIncrementer.increment()
    duke = HSApiCsvMapperIncrementer.increment()
    bandos = HSApiCsvMapperIncrementer.increment()
    giant_mole = HSApiCsvMapperIncrementer.increment()
    gg = HSApiCsvMapperIncrementer.increment()
    hespori = HSApiCsvMapperIncrementer.increment()
    kq = HSApiCsvMapperIncrementer.increment()
    kbd = HSApiCsvMapperIncrementer.increment()
    kraken = HSApiCsvMapperIncrementer.increment()
    armadyl = HSApiCsvMapperIncrementer.increment()
    zamorak = HSApiCsvMapperIncrementer.increment()
    lunar_chests = HSApiCsvMapperIncrementer.increment()
    mimic = HSApiCsvMapperIncrementer.increment()
    nex = HSApiCsvMapperIncrementer.increment()
    nightmare = HSApiCsvMapperIncrementer.increment()
    psn = HSApiCsvMapperIncrementer.increment()
    obor = HSApiCsvMapperIncrementer.increment()
    phantom_muspah = HSApiCsvMapperIncrementer.increment()
    royal_titans = HSApiCsvMapperIncrementer.increment()
    sarachnis = HSApiCsvMapperIncrementer.increment()
    scorpia = HSApiCsvMapperIncrementer.increment()
    scurrius = HSApiCsvMapperIncrementer.increment()
    skotizo = HSApiCsvMapperIncrementer.increment()
    sol = HSApiCsvMapperIncrementer.increment()
    spindel = HSApiCsvMapperIncrementer.increment()
    tempoross = HSApiCsvMapperIncrementer.increment()
    gauntlet = HSApiCsvMapperIncrementer.increment()
    cg = HSApiCsvMapperIncrementer.increment()
    hueycoatl = HSApiCsvMapperIncrementer.increment()
    leviathan = HSApiCsvMapperIncrementer.increment()
    whisperer = HSApiCsvMapperIncrementer.increment()
    tob = HSApiCsvMapperIncrementer.increment()
    tob_hm = HSApiCsvMapperIncrementer.increment()
    thermy = HSApiCsvMapperIncrementer.increment()
    toa = HSApiCsvMapperIncrementer.increment()
    toa_em = HSApiCsvMapperIncrementer.increment()
    zuk = HSApiCsvMapperIncrementer.increment()
    jad = HSApiCsvMapperIncrementer.increment()
    vardorvis = HSApiCsvMapperIncrementer.increment()
    venenatis = HSApiCsvMapperIncrementer.increment()
    vetion = HSApiCsvMapperIncrementer.increment()
    vorkath = HSApiCsvMapperIncrementer.increment()
    wt = HSApiCsvMapperIncrementer.increment()
    yama = HSApiCsvMapperIncrementer.increment()
    zalcano = HSApiCsvMapperIncrementer.increment()
    zulrah = HSApiCsvMapperIncrementer.increment()
    combat = -1

    def is_skill(self) -> bool:
        return HSApiCsvMapper.overall.value <= self.value <= HSApiCsvMapper.construction.value

    def is_misc(self) -> bool:
        return HSApiCsvMapper.league_points.value <= self.value <= HSApiCsvMapper.zulrah.value

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