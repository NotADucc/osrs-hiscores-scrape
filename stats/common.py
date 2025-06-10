from enum import Flag

def calc_cmb(att: int, de: int, st: int, hp: int, ra: int, pr: int, ma: int) -> float:
    base = 0.25 * (de + hp + pr // 2)
    melee = 0.325 * (att + st)
    ranged = 0.325 * (ra // 2 + ra)
    mage = 0.325 * (ma // 2 + ma)
    mx = melee if melee > ranged else ranged
    mx = mx if mx > mage else mage
    return base + mx

class StatsFlag(Flag):
    default = 0
    add_skills = 1 << 0
    add_misc = 1 << 1

    def __str__(self):
        return self.name

    def __add__(self, item):
        return self | item

    def __contains__(self, item):
        return (self.value & item.value) == item.value
