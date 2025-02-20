def calc_cmb(att, de, st, hp, ra, pr, ma):
    base = 0.25 * (de + hp + pr // 2)
    melee = 0.325 * (att + st)
    ranged = 0.325 * (ra // 2 + ra)
    mage = 0.325 * (ma // 2 + ma)
    mx = melee if melee > ranged else ranged
    mx = mx if mx > mage else mage
    return base + mx
