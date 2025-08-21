import datetime
from functools import total_ordering
from typing import Any, Callable, List

from src.request.common import HSType
from src.stats.common import calc_cmb
from src.util import json_wrapper


@total_ordering
class PlayerRecord:
    """
    Represents an OSRS player record parsed from the highscore CSV API endpoint.

    Attributes:
        username (str): The player's username.
        ts (datetime): Timestamp of when this record was retrieved.
        rank (int): Overall rank of the player.
        total_level (int): Total level across all skills.
        combat_lvl (int): Calculated combat level based on relevant skills.
        total_xp (int): Total experience points across all skills.
        skills (dict[str, int]): Mapping of skill names to their levels.
        misc (dict[str, int]): Mapping of miscellaneous categories to their counts.
    """
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

    def get_stat(self, hs_type: HSType) -> int:
        """
        Retrieve record value for a given highscore type.

        Args:
            hs_type (HSType): The highscore type to query (skill, misc, overall, or combat).

        Returns:
            int: The value corresponding to the given type. Returns 0 if the type is missing.
        """
        if hs_type is HSType.overall:
            val = self.total_level
        elif hs_type is HSType.combat:
            val = self.combat_lvl
        elif hs_type.is_skill():
            val = self.skills.get(hs_type.name, 0)
        elif hs_type.is_misc():
            val = self.misc.get(hs_type.name, 0)
        return val

    def lacks_requirements(self, requirements: dict[HSType, Callable[[Any], bool]]) -> bool:
        """
        Check if the player fails any of the given requirements.

        Args:
            requirements (dict[HSType, Callable[[Any], bool]]): A mapping of HSType keys to
                predicate functions that take a stat value and return True/False.

        Returns:
            bool: True if the player fails at least one requirement, False if all are met.
        """
        return not self.meets_requirements(requirements=requirements)

    def meets_requirements(self, requirements: dict[HSType, Callable[[Any], bool]]) -> bool:
        """
        Check if the player satisfies all given requirements.

        Args:
            requirements (dict[HSType, Callable[[Any], bool]]): A mapping of HSType keys to
                predicate functions that take a stat value and return True/False.

        Returns:
            bool: True if all requirements are met, False otherwise.
        """
        return all(pred(self.get_stat(key)) for key, pred in requirements.items())

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
    """
    Represents a single entry in a highscore category.

    Attributes:
        rank (int): The player's rank in this category.
        score (int): The player's score in this category.
        username (str): The player's username.
    """
    def __init__(self, rank: int, score: int, username: str):
        self.rank = rank
        self.score = score
        self.username = username

    def is_better_rank_than(self, other: 'CategoryRecord') -> bool:
        """
        Determine if this record has a better (lower) rank than another record.
        """
        if other is None:
            return False
        return self.rank < other.rank

    def is_worse_rank_than(self, other: 'CategoryRecord') -> bool:
        """
        Determine if this record has a worse (higher) rank than another record.
        """
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
    """
    Aggregates statistics for a highscore category over multiple records.

    Attributes:
        name (str): The name of the category.
        ts (datetime): Timestamp when the aggregation started.
        count (int): Number of records added.
        total_score (int): Sum of scores of all records added.
        max (CategoryRecord | None): Record with the worst rank (highest number).
        min (CategoryRecord | None): Record with the best rank (lowest number).
    """
    def __init__(self, name: str, ts: datetime):
        self.name = name
        self.ts = ts
        self.count = 0
        self.total_score = 0
        self.max = None
        self.min = None

    def add(self, record: CategoryRecord) -> None:
        """
        Add a CategoryRecord to the aggregation and update statistics.

        Args:
            record (CategoryRecord): The highscore record to add.
        """
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
