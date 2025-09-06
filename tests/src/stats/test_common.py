
import math
import pytest

from src.stats.common import calc_cmb


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
def test_calc_cmb(attack: int, defence: int, strength: int, hitpoints: int, ranged: int, prayer: int, magic: int, res: float):
    assert math.isclose(calc_cmb(attack=attack, defence=defence, strength=strength,
                        hitpoints=hitpoints, ranged=ranged, prayer=prayer, magic=magic), res)
