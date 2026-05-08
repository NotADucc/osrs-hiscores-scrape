from enum import Enum


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
    im = 'hiscore_oldschool_ironman'
    uim = 'hiscore_oldschool_ultimate'
    hc = 'hiscore_oldschool_hardcore_ironman'
    pure = 'hiscore_oldschool_skiller_defence'
    skiller = 'hiscore_oldschool_skiller'
    dmm = 'hiscore_oldschool_deadman'
    leagues = 'hiscore_oldschool_seasonal'
    tournament = 'hiscore_oldschool_tournament'
    fsw = 'hiscore_oldschool_fresh_start'

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
            return HSAccountTypes[s.lower()]
        except KeyError:
            valid_values = ', '.join(HSAccountTypes.__members__.keys())
            raise KeyError(f'value given: {s}, valid values [{valid_values}]')
