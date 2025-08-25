

def calc_cmb(att: int, de: int, st: int, hp: int, ra: int, pr: int, ma: int) -> float:
    """
    Calculate the combat level based on osrs stats.

    Args:
        att (int): Attack level.
        de (int): Defence level.
        st (int): Strength level.
        hp (int): Hitpoints level.
        ra (int): Ranged level.
        pr (int): Prayer level.
        ma (int): Magic level.

    Returns:
        float: The calculated combat level.
    """

    base = 0.25 * (de + hp + pr // 2)
    melee = 0.325 * (att + st)
    ranged = 0.325 * (ra // 2 + ra)
    mage = 0.325 * (ma // 2 + ma)
    mx = melee if melee > ranged else ranged
    mx = mx if mx > mage else mage
    return base + mx


def calc_lvl(experience: int, show_virtual_lvl: bool = True) -> int:
    """
    Determine the level based on total experience points.

    Args:
        experience (int): The total accumulated experience points.
        show_virtual_lvl (bool): If False, cap level at 99. If True, include virtual levels up to 126.

    Returns:
        int: The corresponding level.
    """

    xp_table = {
        1: 0, 2: 83, 3: 174, 4: 276, 5: 388, 6: 512, 7: 650, 8: 801, 9: 969, 10: 1_154,
        11: 1_358, 12: 1_584, 13: 1_833, 14: 2_107, 15: 2_411, 16: 2_746, 17: 3_115, 18: 3_523, 19: 3_973, 20: 4_470,
        21: 5_018, 22: 5_624, 23: 6_291, 24: 7_028, 25: 7_842, 26: 8_740, 27: 9_730, 28: 10_824, 29: 12_031, 30: 13_363,
        31: 14_833, 32: 16_456, 33: 18_247, 34: 20_224, 35: 22_406, 36: 24_815, 37: 27_473, 38: 30_408, 39: 33_648, 40: 37_224,
        41: 41_171, 42: 45_429, 43: 50_339, 44: 55_649, 45: 61_512, 46: 67_983, 47: 75_127, 48: 83_014, 49: 91_721, 50: 101_333,
        51: 111_945, 52: 123_660, 53: 136_594, 54: 150_872, 55: 166_636, 56: 184_040, 57: 203_254, 58: 224_466, 59: 247_886, 60: 273_742,
        61: 302_288, 62: 333_804, 63: 368_599, 64: 407_015, 65: 449_428, 66: 496_254, 67: 547_953, 68: 605_033, 69: 668_051, 70: 737_627,
        71: 814_445, 72: 899_257, 73: 992_895, 74: 1_096_278, 75: 1_210_421, 76: 1_336_423, 77: 1_475_181, 78: 1_629_200, 79: 1_798_808, 80: 1_986_068,
        81: 2_192_818, 82: 2_421_087, 83: 2_673_114, 84: 2_951_373, 85: 3_258_594, 86: 3_597_792, 87: 3_972_294, 88: 4_385_776, 89: 4_842_295, 90: 5_346_323,
        91: 5_902_831, 92: 6_517_253, 93: 7_195_629, 94: 7_944_464, 95: 8_771_558, 96: 9_684_577, 97: 10_692_249, 98: 11_805_066, 99: 13_034_431,

        # virtual lvls
        100: 14_391_160, 101: 15_889_109, 102: 17_542_976, 103: 19_368_992, 104: 21_385_073, 105: 23_611_006, 106: 26_068_632,
        107: 28_782_069, 108: 31_777_943, 109: 35_085_654, 110: 38_737_661, 111: 42_769_801, 112: 47_221_641, 113: 52_136_869,
        114: 57_563_718, 115: 63_555_443, 116: 70_170_840, 117: 77_474_828, 118: 85_539_082, 119: 94_442_737, 120: 104_273_167,
        121: 115_126_838, 122: 127110260, 123: 140_341_028, 124: 154_948_977, 125: 171_077_457, 126: 188_884_740
    }

    max_lvl = 126 if show_virtual_lvl else 99

    for level in range(1, max_lvl + 1):
        if experience < xp_table[level]:
            return level - 1

    return max_lvl
