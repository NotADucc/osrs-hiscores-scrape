import datetime
import json
from typing import Any, Callable, List

from request.common import HSApiCsvMapper
from stats.common import calc_cmb

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

        for mapper_val in list(HSApiCsvMapper)[1:]:
            if mapper_val.value == -1:
                continue

            splitted = list(map(int, csv[mapper_val.value].split(',')))

            if mapper_val.is_skill():
                # self.skills[mapper_val.name] = { 'rank': splitted[0], 'lvl': splitted[1], 'xp': splitted[2] }
                # just lvl for now, saving all the information is prob gonna clog it
                self.skills[mapper_val.name] = splitted[1]

            elif mapper_val.is_misc():
                if splitted[0] == -1:
                    continue
                # self.misc[mapper_val.name] = { 'rank': splitted[0], 'kc': splitted[1] }
                self.misc[mapper_val.name] = splitted[1]

        cmb_level = calc_cmb(self.skills[HSApiCsvMapper.attack.name], self.skills[HSApiCsvMapper.defence.name],
                             self.skills[HSApiCsvMapper.strength.name], self.skills[HSApiCsvMapper.hitpoints.name], self.skills[HSApiCsvMapper.ranged.name], self.skills[HSApiCsvMapper.prayer.name], self.skills[HSApiCsvMapper.magic.name])
        self.combat_lvl = cmb_level

    def lacks_requirements(self, requirements: dict[HSApiCsvMapper, Callable[[Any], bool]]) -> bool:
        for key, pred in requirements.items():
            if key is HSApiCsvMapper.overall:
                val = self.total_level
            elif key is HSApiCsvMapper.combat:
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

    def __ne__(self, other) -> bool:
        return not self == other

    def __gt__(self, other) -> bool:
        return other < self

    def __ge__(self, other) -> bool:
        return not self < other

    def __le__(self, other) -> bool:
        return not other < self

    def __str__(self):
        data = {
            "rank": self.rank,
            "username": self.username,
            "timestamp": self.ts.isoformat(),
            "total_level": self.total_level,
            "combat_lvl": self.combat_lvl,
            "total_xp": self.total_xp,
            "skills": self.skills,
            "misc": self.misc,
        }
        return json.dumps(data, separators=(',', ':'))


class CategoryRecord:
    def __init__(self, rank: int, score: int, username: str):
        self.rank = rank
        self.score = score
        self.username = username

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "score": self.score,
            "username": self.username
        }

    def __lt__(self, other: 'CategoryRecord') -> bool:
        return self.rank < other.rank

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return not self < other and not other < self

    def __ne__(self, other) -> bool:
        return not self == other

    def __gt__(self, other) -> bool:
        return other < self

    def __ge__(self, other) -> bool:
        return not self < other

    def __le__(self, other) -> bool:
        return not other < self

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'))


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
        if not self.max or self.max < record:
            self.max = record

        if not self.min or self.min > record:
            self.min = record

    def __str__(self) -> str:
        data = {
            "name": self.name,
            "timestamp": self.ts.isoformat(),
            "count": self.count,
            "total_score": self.total_score,
            "max": self.max.to_dict() if self.max else None,
            "min": self.min.to_dict() if self.min else None,
        }
        return json.dumps(data, separators=(',', ':'))
