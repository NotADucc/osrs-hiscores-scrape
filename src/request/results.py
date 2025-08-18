import datetime
from functools import total_ordering
from typing import Any, Callable, List

from src.request.common import HSType
from src.stats.common import calc_cmb
from src.util import json_wrapper


@total_ordering
class PlayerRecord:
    def __init__(self, username: str, csv: List[str], ts: datetime):
        self.username = username

        first_record = list(map(int, csv[0].split(',')))

        self.ts = ts
        self.rank = first_record[0]
        self.total_level = first_record[1]
        self.combat_lvl = 3
        self.total_xp = first_record[2]
        self.skills = {}
        self.misc = {}

        for hstypes in list(HSType)[1:]:
            csv_val = hstypes.get_csv_value()

            if csv_val == -1:
                continue

            splitted = list(map(int, csv[csv_val].split(',')))

            if hstypes.is_skill():
                # self.skills[mapper_val.name] = { 'rank': splitted[0], 'lvl': splitted[1], 'xp': splitted[2] }
                # just lvl for now, saving rank, lvl, xp and maybe virtual lvl is gonna be too much
                # or have a flag that can enable it
                self.skills[hstypes.name] = splitted[1]

            elif hstypes.is_misc():
                if splitted[0] == -1:
                    continue
                # self.misc[mapper_val.name] = { 'rank': splitted[0], 'kc': splitted[1] }
                self.misc[hstypes.name] = splitted[1]

        cmb_level = calc_cmb(self.skills[HSType.attack.name], self.skills[HSType.defence.name],
                             self.skills[HSType.strength.name], self.skills[HSType.hitpoints.name], self.skills[HSType.ranged.name], self.skills[HSType.prayer.name], self.skills[HSType.magic.name])
        self.combat_lvl = cmb_level

    def lacks_requirements(self, requirements: dict[HSType, Callable[[Any], bool]]) -> bool:
        return not self.meets_requirements(requirements=requirements)

    def meets_requirements(self, requirements: dict[HSType, Callable[[Any], bool]]) -> bool:
        for key, pred in requirements.items():
            if key is HSType.overall:
                val = self.total_level
            elif key is HSType.combat:
                val = self.combat_lvl
            elif key.is_skill():
                val = self.skills.get(key.name, 0)
            elif key.is_misc():
                val = self.misc.get(key.name, 0)
            if not pred(val):
                return False
        return True

    def __lt__(self, other) -> bool:
        if self.total_level < other.total_level:
            return True
        elif self.total_level == other.total_level and self.total_xp < other.total_xp:
            return True
        elif self.total_xp == other.total_xp and self.rank > other.rank:
            return True
        return False

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return not self < other and not other < self

    def to_dict(self):
        return {
            "rank": self.rank,
            "username": self.username,
            "timestamp": self.ts.isoformat(),
            "total_level": self.total_level,
            "combat_lvl": self.combat_lvl,
            "total_xp": self.total_xp,
            "skills": self.skills,
            "misc": self.misc,
        }

    def __str__(self):
        return json_wrapper.to_json(self.to_dict(), separators=(',', ':'))


@total_ordering
class CategoryRecord:
    def __init__(self, rank: int, score: int, username: str):
        self.rank = rank
        self.score = score
        self.username = username

    def is_better_rank_than(self, other: 'CategoryRecord') -> bool:
        if other is None:
            return False
        return self.rank < other.rank

    def is_worse_rank_than(self, other: 'CategoryRecord') -> bool:
        if other is None:
            return False
        return self.rank > other.rank

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "score": self.score,
            "username": self.username
        }

    def __lt__(self, other: 'CategoryRecord') -> bool:
        # technically the smaller rank is greater than bigger rank but this is for sorts
        return self.rank < other.rank

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.rank == other.rank

    def __str__(self) -> str:
        return json_wrapper.to_json(self.to_dict(), separators=(',', ':'))


class CategoryInfo:
    def __init__(self, name: str, ts: datetime):
        self.name = name
        self.ts = ts
        self.count = 0
        self.total_score = 0
        self.max = None
        self.min = None

    def add(self, record: CategoryRecord) -> None:
        self.count += 1
        self.total_score += record.score
        # the > and < should technically be reversed since smaller rank is greate rthan larger rank
        if not self.max or self.max.is_worse_rank_than(record):
            self.max = record

        if not self.min or self.min.is_better_rank_than(record):
            self.min = record

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "timestamp": self.ts.isoformat(),
            "count": self.count,
            "total_score": self.total_score,
            "max": self.max.to_dict() if self.max else None,
            "min": self.min.to_dict() if self.min else None,
        }

    def __str__(self) -> str:
        return json_wrapper.to_json(self.to_dict(), separators=(',', ':'))
