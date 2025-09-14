
import math

import pytest

from src.stats.common import calc_combat_level, calc_skill_level


@pytest.mark.parametrize(
    "attack, defence, strength, hitpoints, ranged, prayer, magic,   res",
    [
        (99,    99,     99,     99,         99,      99,     99,    126.1),
        (99,    99,     99,     99,         1,       99,     99,    126.1),
        (99,    99,     99,     99,         1,       99,     1,     126.1),
        (99,    99,     99,     10,         99,      99,     99,    103.85),
        (70,    1,      99,     99,         99,      43,     99,    85.175),
        (1,     1,      1,      1,          1,       1,      1,     1.15),
        (1000,  1,      1,      1,          1,       1,      1,     325.825),
        (-1,   -1,     -1,     -1,         -1,      -1,     -1,     -1.4),
    ]
)
def test_calc_combat_level(attack: int, defence: int, strength: int, hitpoints: int, ranged: int, prayer: int, magic: int, res: float):
    assert math.isclose(calc_combat_level(attack=attack, defence=defence, strength=strength,
                        hitpoints=hitpoints, ranged=ranged, prayer=prayer, magic=magic), res)


@pytest.mark.parametrize(
    "experience, show_virtual_lvl, res",
    [
        (0, True, 1),
        (0, False, 1),
        (82, True, 1),
        (83, True, 2),
        (174, True, 3),

        (5_000, True, 20),
        (5_000, False, 20),
        (101_333, True, 50),
        (101_333, False, 50),
        (302_288, True, 61),
        (302_288, False, 61),

        (13_034_430, True, 98),
        (13_034_430, False, 98),
        (13_034_431, True, 99),
        (13_034_431, False, 99),

        (13_034_431, True, 99),
        (14_391_160, True, 100),
        (115_126_838, True, 121),
        (188_884_740, True, 126),

        (999_999_999, True, 126),
        (999_999_999, False, 99),
    ]
)
def test_calc_skill_level(experience: int, show_virtual_lvl: bool, res: int):
    assert calc_skill_level(experience=experience,
                            show_virtual_lvl=show_virtual_lvl) == res
