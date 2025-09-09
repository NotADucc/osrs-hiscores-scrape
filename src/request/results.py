from datetime import datetime
from functools import total_ordering
from typing import Any, List

from src.request.common import HSType
from src.request.dto import HSFilterEntry
from src.stats.common import calc_combat_level
from src.util import json_wrapper


@total_ordering
class PlayerRecord:
    """
    Represents an OSRS player record parsed from the highscore CSV API endpoint.
    """

    def __init__(self, username: str, csv: List[str], ts: datetime):
        self.username = username

        # first line is rank, total lvl and total xp
        first_record = [int(x) for x in csv[0].split(',')]

        self.ts = ts
        self.rank = first_record[0]
        self.total_level = first_record[1]
        self.combat_lvl = 3
        self.total_xp = first_record[2]
        self.skills = {}
        self.misc = {}

        hs_types = list(HSType)

        if len(hs_types) - 1 != len(csv):
            return

        for hs_type in hs_types[1:]:
            csv_val = hs_type.get_csv_value()

            if csv_val == -1:
                continue

            splitted = [int(x) for x in csv[csv_val].split(',')]

            if hs_type.is_skill():
                # self.skills[mapper_val.name] = { 'rank': splitted[0], 'lvl': splitted[1], 'xp': splitted[2] }
                # just lvl for now, saving rank, lvl, xp and maybe virtual lvl is gonna be too much
                # or have a flag that can enable it
                self.skills[hs_type.name] = splitted[1]

            elif hs_type.is_misc():
                if splitted[0] == -1:
                    continue
                # self.misc[mapper_val.name] = { 'rank': splitted[0], 'kc': splitted[1] }
                self.misc[hs_type.name] = splitted[1]

        cmb_level = calc_combat_level(
            attack=self.skills[HSType.attack.name],
            defence=self.skills[HSType.defence.name],
            strength=self.skills[HSType.strength.name],
            hitpoints=self.skills[HSType.hitpoints.name],
            ranged=self.skills[HSType.ranged.name],
            prayer=self.skills[HSType.prayer.name],
            magic=self.skills[HSType.magic.name]
        )

        self.combat_lvl = cmb_level

    def get_stat(self, hs_type: HSType) -> int | float:
        """ 
        Retrieve record value for a given highscore type. 

        Raises:
            ValueError raised if `HSType` is unknown.
        """
        if hs_type is HSType.overall:
            val = self.total_level
        elif hs_type is HSType.combat:
            val = self.combat_lvl
        elif hs_type.is_skill():
            val = self.skills.get(hs_type.name, 0)
        elif hs_type.is_misc():
            val = self.misc.get(hs_type.name, 0)
        else:
            raise ValueError(f"Unknown hs type: {hs_type.name}")

        return val

    def lacks_requirements(self, requirements: list[HSFilterEntry]) -> bool:
        """ Check if the player fails any of the given requirements. """
        return not self.meets_requirements(requirements=requirements)

    def meets_requirements(self, requirements: list[HSFilterEntry]) -> bool:
        """ Check if the player satisfies all given requirements. """
        return all(entry.predicate(self.get_stat(entry.hstype)) for entry in requirements)

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

    def to_dict(self) -> dict[str, Any]:
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PlayerRecord':
        """ Reconstructs a PlayerRecord from a dict produced by to_dict(). """
        ts = datetime.fromisoformat(data["timestamp"])
        fake_csv = [f"{data['rank']},{data['total_level']},{data['total_xp']}"]
        obj = cls(data["username"], fake_csv, ts)
        obj.combat_lvl = data["combat_lvl"]
        obj.skills = data["skills"]
        obj.misc = data["misc"]

        return obj

    def __str__(self):
        return json_wrapper.to_json(self.to_dict(), separators=(',', ':'))


@total_ordering
class CategoryRecord:
    """ Represents a single entry in a highscore category. """

    def __init__(self, rank: int, score: int, username: str):
        self.rank = rank
        self.score = score
        self.username = username

    def is_better_rank_than(self, other: 'CategoryRecord') -> bool:
        """ Determine if this record has a better (lower) rank than another record. """
        if other is None:
            return False
        return self.rank < other.rank

    def is_worse_rank_than(self, other: 'CategoryRecord') -> bool:
        """ Determine if this record has a worse (higher) rank than another record. """
        if other is None:
            return False
        return self.rank > other.rank

    def to_dict(self) -> dict[str, Any]:
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
    """ Aggregates statistics for a highscore category over multiple records. """

    def __init__(self, name: str, ts: datetime):
        self.name = name
        self.ts = ts
        self.count = 0
        self.total_score = 0
        self.max = None
        self.min = None

    def add(self, record: CategoryRecord) -> None:
        """ Add a CategoryRecord to the aggregation and update statistics. """
        self.count += 1
        self.total_score += record.score
        # the > and < should technically be reversed since smaller rank is greater than larger rank
        if not self.max or self.max.is_worse_rank_than(record):
            self.max = record

        if not self.min or self.min.is_better_rank_than(record):
            self.min = record

    def to_dict(self) -> dict[str, Any]:
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
