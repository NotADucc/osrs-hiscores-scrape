from dataclasses import dataclass
from enum import Enum

HS_PAGE_SIZE: int = 25
MAX_CATEGORY_SIZE: int = 80_000


class HSAccountTypes(Enum):
    """
    Enum of OSRS hiscore account types, each type maps to the corresponding hiscore endpoint used to retrieve stats.

    Attributes:
        regular
        pure
        im.
        uim
        hc
        skiller
    """
    regular = 'hiscore_oldschool'
    pure = 'hiscore_oldschool_skiller_defence'
    im = 'hiscore_oldschool_ironman'
    uim = 'hiscore_oldschool_ultimate'
    hc = 'hiscore_oldschool_hardcore_ironman'
    skiller = 'hiscore_oldschool_skiller'

    def lookup_overall(self) -> str:
        return f'https://secure.runescape.com/m={self.value}/overall'

    def lookup_personal(self) -> str:
        return f'https://secure.runescape.com/m={self.value}/hiscorepersonal'

    def api_csv(self) -> str:
        return f'https://secure.runescape.com/m={self.value}/index_lite.ws'

    def api_json(self) -> str:
        return f'https://secure.runescape.com/m={self.value}/index_lite.json'

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s: str) -> 'HSAccountTypes':
        try:
            return HSAccountTypes[s]
        except KeyError:
            valid_values = ', '.join(HSAccountTypes.__members__.keys())
            raise KeyError(f'value given: {s}, valid values [{valid_values}]')


@dataclass
class HSValue():
    """ Internal value type to help with 'HSType'. """
    category: int
    category_value: int
    csv_value: int


class HSIncrementer():
    """ Internal incrementer to help with 'HSType'. """

    def __init__(self):
        self._arr = [0] * 3

    def skill_increment(self) -> HSValue:
        cat_val, csv_val = self._arr[0], self._arr[2]
        self._arr[0] += 1
        self._arr[2] += 1
        return HSValue(category=0, category_value=cat_val, csv_value=csv_val)

    def misc_increment(self, has_csv_mapping=True) -> HSValue:
        cat_val, csv_val = self._arr[1], self._arr[2]
        self._arr[1] += 1

        if not has_csv_mapping:
            csv_val = -1
        else:
            self._arr[2] += 1

        return HSValue(category=1, category_value=cat_val, csv_value=csv_val)


HSCategoryMapperIncrementer = HSIncrementer()


class HSType(Enum):
    """ 
    Enum of OSRS hiscore categories, each value contains data to make hiscore lookup easier.
    """
    overall = HSCategoryMapperIncrementer.skill_increment()
    attack = HSCategoryMapperIncrementer.skill_increment()
    defence = HSCategoryMapperIncrementer.skill_increment()
    strength = HSCategoryMapperIncrementer.skill_increment()
    hitpoints = HSCategoryMapperIncrementer.skill_increment()
    ranged = HSCategoryMapperIncrementer.skill_increment()
    prayer = HSCategoryMapperIncrementer.skill_increment()
    magic = HSCategoryMapperIncrementer.skill_increment()
    cooking = HSCategoryMapperIncrementer.skill_increment()
    woodcutting = HSCategoryMapperIncrementer.skill_increment()
    fletching = HSCategoryMapperIncrementer.skill_increment()
    fishing = HSCategoryMapperIncrementer.skill_increment()
    firemaking = HSCategoryMapperIncrementer.skill_increment()
    crafting = HSCategoryMapperIncrementer.skill_increment()
    smithing = HSCategoryMapperIncrementer.skill_increment()
    mining = HSCategoryMapperIncrementer.skill_increment()
    herblore = HSCategoryMapperIncrementer.skill_increment()
    agility = HSCategoryMapperIncrementer.skill_increment()
    thieving = HSCategoryMapperIncrementer.skill_increment()
    slayer = HSCategoryMapperIncrementer.skill_increment()
    farming = HSCategoryMapperIncrementer.skill_increment()
    runecrafting = HSCategoryMapperIncrementer.skill_increment()
    hunter = HSCategoryMapperIncrementer.skill_increment()
    construction = HSCategoryMapperIncrementer.skill_increment()
    sailing = HSCategoryMapperIncrementer.skill_increment()
    # start non skilling stuff, for some reason its split up in 2
    grid_points = HSCategoryMapperIncrementer.misc_increment()
    league_points = HSCategoryMapperIncrementer.misc_increment()
    dmm = HSCategoryMapperIncrementer.misc_increment()
    bh_hunter = HSCategoryMapperIncrementer.misc_increment()
    bh_rogue = HSCategoryMapperIncrementer.misc_increment()
    bh_legacy_hunter = HSCategoryMapperIncrementer.misc_increment()
    bh_legacy_rogue = HSCategoryMapperIncrementer.misc_increment()
    clue_all = HSCategoryMapperIncrementer.misc_increment()
    clue_beginner = HSCategoryMapperIncrementer.misc_increment()
    clue_easy = HSCategoryMapperIncrementer.misc_increment()
    clue_medium = HSCategoryMapperIncrementer.misc_increment()
    clue_hard = HSCategoryMapperIncrementer.misc_increment()
    clue_elite = HSCategoryMapperIncrementer.misc_increment()
    clue_master = HSCategoryMapperIncrementer.misc_increment()
    lms_rank = HSCategoryMapperIncrementer.misc_increment()
    pvp_arena_rank = HSCategoryMapperIncrementer.misc_increment()
    sw_zeal = HSCategoryMapperIncrementer.misc_increment()
    rifts_closed = HSCategoryMapperIncrementer.misc_increment()
    colosseum_glory = HSCategoryMapperIncrementer.misc_increment()
    collections_logged = HSCategoryMapperIncrementer.misc_increment()
    # bosses
    sire = HSCategoryMapperIncrementer.misc_increment()
    hydra = HSCategoryMapperIncrementer.misc_increment()
    amoxliatl = HSCategoryMapperIncrementer.misc_increment()
    araxxor = HSCategoryMapperIncrementer.misc_increment()
    artio = HSCategoryMapperIncrementer.misc_increment()
    barrows_chests = HSCategoryMapperIncrementer.misc_increment()
    bryophyta = HSCategoryMapperIncrementer.misc_increment()
    callisto = HSCategoryMapperIncrementer.misc_increment()
    calvarion = HSCategoryMapperIncrementer.misc_increment()
    cerberus = HSCategoryMapperIncrementer.misc_increment()
    cox = HSCategoryMapperIncrementer.misc_increment()
    cox_cm = HSCategoryMapperIncrementer.misc_increment()
    chaos_elemental = HSCategoryMapperIncrementer.misc_increment()
    chaos_fanatic = HSCategoryMapperIncrementer.misc_increment()
    saradomin = HSCategoryMapperIncrementer.misc_increment()
    corp = HSCategoryMapperIncrementer.misc_increment()
    crazy_archaeologist = HSCategoryMapperIncrementer.misc_increment()
    dks_prime = HSCategoryMapperIncrementer.misc_increment()
    dks_rex = HSCategoryMapperIncrementer.misc_increment()
    dks_supreme = HSCategoryMapperIncrementer.misc_increment()
    deranged_archaeologist = HSCategoryMapperIncrementer.misc_increment()
    doom_mokhaiotl = HSCategoryMapperIncrementer.misc_increment()
    duke = HSCategoryMapperIncrementer.misc_increment()
    bandos = HSCategoryMapperIncrementer.misc_increment()
    giant_mole = HSCategoryMapperIncrementer.misc_increment()
    gg = HSCategoryMapperIncrementer.misc_increment()
    hespori = HSCategoryMapperIncrementer.misc_increment()
    kq = HSCategoryMapperIncrementer.misc_increment()
    kbd = HSCategoryMapperIncrementer.misc_increment()
    kraken = HSCategoryMapperIncrementer.misc_increment()
    armadyl = HSCategoryMapperIncrementer.misc_increment()
    zamorak = HSCategoryMapperIncrementer.misc_increment()
    lunar_chests = HSCategoryMapperIncrementer.misc_increment()
    mimic = HSCategoryMapperIncrementer.misc_increment()
    nex = HSCategoryMapperIncrementer.misc_increment()
    nightmare = HSCategoryMapperIncrementer.misc_increment()
    psn = HSCategoryMapperIncrementer.misc_increment()
    obor = HSCategoryMapperIncrementer.misc_increment()
    phantom_muspah = HSCategoryMapperIncrementer.misc_increment()
    sarachnis = HSCategoryMapperIncrementer.misc_increment()
    scorpia = HSCategoryMapperIncrementer.misc_increment()
    scurrius = HSCategoryMapperIncrementer.misc_increment()
    shellbane_gryphon = HSCategoryMapperIncrementer.misc_increment()
    skotizo = HSCategoryMapperIncrementer.misc_increment()
    sol = HSCategoryMapperIncrementer.misc_increment()
    spindel = HSCategoryMapperIncrementer.misc_increment()
    tempoross = HSCategoryMapperIncrementer.misc_increment()
    gauntlet = HSCategoryMapperIncrementer.misc_increment()
    cg = HSCategoryMapperIncrementer.misc_increment()
    hueycoatl = HSCategoryMapperIncrementer.misc_increment()
    leviathan = HSCategoryMapperIncrementer.misc_increment()
    royal_titans = HSCategoryMapperIncrementer.misc_increment()
    whisperer = HSCategoryMapperIncrementer.misc_increment()
    tob = HSCategoryMapperIncrementer.misc_increment()
    hmt = HSCategoryMapperIncrementer.misc_increment()
    thermy = HSCategoryMapperIncrementer.misc_increment()
    toa = HSCategoryMapperIncrementer.misc_increment()
    toa_em = HSCategoryMapperIncrementer.misc_increment()
    zuk = HSCategoryMapperIncrementer.misc_increment()
    jad = HSCategoryMapperIncrementer.misc_increment()
    vardorvis = HSCategoryMapperIncrementer.misc_increment()
    venenatis = HSCategoryMapperIncrementer.misc_increment()
    vetion = HSCategoryMapperIncrementer.misc_increment()
    vorkath = HSCategoryMapperIncrementer.misc_increment()
    wt = HSCategoryMapperIncrementer.misc_increment()
    yama = HSCategoryMapperIncrementer.misc_increment()
    zalcano = HSCategoryMapperIncrementer.misc_increment()
    zulrah = HSCategoryMapperIncrementer.misc_increment()
    combat = HSValue(-1, -1, -1)

    def get_category(self) -> int:
        """ OSRS hiscore category type. """
        return self.value.category

    def get_category_value(self) -> int:
        """ OSRS hiscore category type value. """
        return self.value.category_value

    def get_csv_value(self) -> int:
        """ OSRS hiscore csv value. """
        return self.value.csv_value

    def is_skill(self) -> bool:
        """ Determine whether the OSRS category represents a skill. """
        return self.get_category() == 0

    def is_misc(self) -> bool:
        """ Determine whether the OSRS category represents misc. """
        return self.get_category() == 1

    def is_combat(self) -> bool:
        """ Determine whether the OSRS category represents a combat stat. """
        return self.name in {
            "attack", "defence", "strength", "hitpoints",
            "ranged", "prayer", "magic", "combat"
        }

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def csv_len() -> int:
        return len([item for item in list(HSType) if item.get_csv_value() != -1])

    @staticmethod
    def get_csv_types() -> list['HSType']:
        return [item for item in list(HSType) if item.get_csv_value() != -1]

    @staticmethod
    def debug() -> list[str]:
        return [f'{v}: {(v.get_category(), v.get_category_value(), v.get_csv_value())}' for v in HSType]

    @staticmethod
    def from_string(s: str) -> 'HSType':
        try:
            return HSType[s]
        except KeyError:
            valid_values = ', '.join(HSType.__members__.keys())
            raise KeyError(f'value given: {s}, valid values [{valid_values}]')
