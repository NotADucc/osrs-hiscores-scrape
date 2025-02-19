import math

from enum import Enum

def calc_cmb(att, de, st, hp, ra, pr, ma) :
    base = 0.25 * (de + hp + pr // 2)
    melee = 0.325 * (att + st)
    ranged = 0.325 * (ra // 2 + ra)
    mage = 0.325 * (ma // 2 + ma)
    mx = melee if melee > ranged else ranged
    mx = mx if mx > mage else mage
    return base + mx

class RequestFailed(Exception):
    pass

class HSOverall(Enum):
    regular = 'https://secure.runescape.com/m=hiscore_oldschool/overall'
    pure = 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/overall'
    im = 'https://secure.runescape.com/m=hiscore_oldschool_ironman/overall'
    uim = 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/overall'
    hc = 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/overall'
    def __str__(self):
        return self.name
        
    @staticmethod
    def from_string(s):
        try:
            return HSOverall[s]
        except KeyError:
            raise ValueError()
       
class HSLookup(Enum):
	regular = 'https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal'
	pure = 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/hiscorepersonal'
	im = 'https://secure.runescape.com/m=hiscore_oldschool_ironman/hiscorepersonal'
	uim = 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/hiscorepersonal'
	hc = 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/hiscorepersonal'
	def __str__(self):
		return self.name
	
	@staticmethod
	def from_string(s):
		try:
			return HSLookup[s]
		except KeyError:
			raise ValueError()
        
class HSApi(Enum):
    regular = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws'
    pure = 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/index_lite.ws'
    im = 'https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws'
    uim = 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.ws'
    hc = 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws'
    regular_json = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.json'
    pure_json = 'https://secure.runescape.com/m=hiscore_oldschool_skiller_defence/index_lite.json'
    im_json = 'https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json'
    uim_json = 'https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.json'
    hc_json = 'https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.json'
    def __str__(self):
        return self.name
        
class HSOverallTableMapper(Enum):
	overall = (0, 0)
	attack = (0, 1)
	defence = (0, 2)
	strength = (0, 3)
	hitpoints = (0, 4)
	ranged = (0, 5)
	prayer = (0, 6)
	magic = (0, 7)
	cooking = (0, 8)
	woodcutting = (0, 9)
	fletching = (0, 10)
	fishing = (0, 11)
	firemaking = (0, 12)
	crafting = (0, 13)
	smithing = (0, 14)
	mining = (0, 15)
	herblore = (0, 16)
	agility = (0, 17)
	thieving = (0, 18)
	slayer = (0, 19)
	farming = (0, 20)
	runecrafting = (0, 21)
	hunter = (0, 22)
	construction = (0, 23)
	league_points = (1, 0)
	dmm = (1, 0)
	bh_hunter = (1, 1)
	bh_rogue = (1, 2)
	bh_legacy_hunter = (1, 3)
	bh_legacy_rogue = (1, 4)
	cs_all = (1, 5)  
	cs_beginner = (1, 6)
	cs_easy = (1, 7)
	cs_medium = (1, 8)
	cs_hard = (1, 9)
	cs_elite = (1, 10)
	cs_master = (1, 11)
	lms_rank = (1, 12)
	pvp_arena_rank = (1, 13)
	sw_zeal = (1, 14)
	rifts_closed = (1, 15)
	colosseum_glory = (1, 16)
	collections_logged = (1, 17)
	sire = (1, 18)
	hydra = (1, 19)
	amoxliatl = (1, 20)
	araxxor = (1, 21)
	artio = (1, 22)
	barrows_chests = (1, 23)
	bryophyta = (1, 24)
	callisto = (1, 25)
	calvarion = (1, 26)
	cerberus = (1, 27)
	cox = (1, 28)
	cox_cm = (1, 29)
	chaos_elemental = (1, 30)
	chaos_fanatic = (1, 31)
	saradomin = (1, 32)
	corp = (1, 33)
	crazy_archaeologist = (1, 34)
	dks_prime = (1, 35)
	dks_rex = (1, 36)
	dks_supreme = (1, 37)
	deranged_archaeologist = (1, 38)
	duke = (1, 39)
	bandos = (1, 40)
	giant_mole = (1, 41)
	gg = (1, 42)
	hespori = (1, 43)
	kq = (1, 44)
	kbd = (1, 45)
	kraken = (1, 46)
	armadyl = (1, 47)
	zamorak = (1, 48)
	lunar_chests = (1, 49)
	mimic = (1, 50)
	nex = (1, 51)
	nightmare = (1, 52)
	psn = (1, 53)
	obor = (1, 54)
	phantom_muspah = (1, 55)
	royal_titans = (1, 56)
	sarachnis = (1, 57)
	scorpia = (1, 58)
	scurrius = (1, 59)
	skotizo = (1, 60)
	sol = (1, 61)
	spindel = (1, 62)
	tempoross = (1, 63)
	gauntlet = (1, 64)
	cg = (1, 65)
	hueycoatl = (1, 66)
	leviathan = (1, 67)
	al = (1, 68)
	whisperer = (1, 69)
	tob = (1, 70)
	hmt = (1, 71)
	thermy = (1, 72)
	toa = (1, 73)
	toa_em = (1, 74)
	zuk = (1, 75)
	jad = (1, 76)
	vardorvis = (1, 77)
	venenatis = (1, 78)
	vetion = (1, 79)
	vorkath = (1, 80)
	wt = (1, 81)
	zalcano = (1, 82)
	zulrah = (1, 83)
	def __str__(self):
		return self.name
        
	@staticmethod
	def from_string(s):
		try:
			return HSOverallTableMapper[s]
		except KeyError:
			raise ValueError()

class HSApiCsvMapper(Enum):
    overall = 0
    attack = 1
    defence = 2
    strength = 3
    hitpoints = 4
    ranged = 5
    prayer = 6
    magic = 7
    cooking = 8
    woodcutting = 9
    fletching = 10
    fishing = 11
    firemaking = 12
    crafting = 13
    smithing = 14
    mining = 15
    herblore = 16
    agility = 17
    thieving = 18
    slayer = 19
    farming = 20
    runecrafting = 21
    hunter = 22
    construction = 23
    league_points = 24
    dmm = 25
    bh_hunter = 26
    bh_rogue = 27
    bh_legacy_hunter = 28
    bh_legacy_rogue = 29
    cs_all = 30  
    cs_beginner = 31
    cs_easy = 32
    cs_medium = 33
    cs_hard = 34
    cs_elite = 35
    cs_master = 36
    lms_rank = 37
    pvp_arena_rank = 38
    sw_zeal = 39
    rifts_closed = 40
    colosseum_glory = 41
    collections_logged = 42
    sire = 43
    hydra = 44
    amoxliatl = 45
    araxxor = 46
    artio = 47
    barrows_chests = 48
    bryophyta = 49
    callisto = 50
    calvarion = 51
    cerberus = 53
    cox = 54
    cox_cm = 55
    chaos_elemental = 56
    chaos_fanatic = 57
    saradomin = 58
    corp = 59
    crazy_archaeologist = 60
    dks_prime = 61
    dks_rex = 62
    dks_supreme = 63
    deranged_archaeologist = 64
    duke = 65
    bandos = 66
    giant_mole = 67
    gg = 68
    hespori = 69
    kq = 70
    kbd = 71
    kraken = 72
    armadyl = 73
    zamorak = 74
    lunar_chests = 75
    mimic = 76
    nex = 77
    nightmare = 78
    psn = 79
    obor = 80
    phantom_muspah = 81
    royal_titans = 82
    sarachnis = 83
    scorpia = 84
    scurrius = 85
    skotizo = 86
    sol = 87
    spindel = 88
    tempoross = 89
    gauntlet = 90
    cg = 91
    hueycoatl = 92
    leviathan = 93
    whisperer = 94
    tob = 95
    tob_hm = 96
    thermy = 97
    toa = 98
    toa_em = 99
    zuk = 100
    jad = 101
    vardorvis = 102
    venenatis = 103
    vetion = 104
    vorkath = 105
    wt = 106
    zalcano = 107
    zulrah = 108
    def __str__(self):
        return self.name
    