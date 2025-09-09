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
        self._total_score = 0
        self._max = None
        self._min = None
        self._records: list[CategoryRecord] = []
        self._is_sorted = True

    @property
    def max(self):
        return self._max

    @property
    def min(self):
        return self._min

    def add(self, record: CategoryRecord) -> None:
        """ Add a CategoryRecord to the aggregation """
        self._is_sorted = False
        self._total_score += record.score
        self._records.append(record)

        if not self._max or self._max.is_worse_rank_than(record):
            self._max = record

        if not self._min or self._min.is_better_rank_than(record):
            self._min = record

    def is_empty(self) -> bool:
        return len(self._records) == 0

    def _sort(self):
        if not self._is_sorted:
            self._records.sort()
            self._is_sorted = True

    def to_dict(self) -> dict[str, Any]:
        def percentile(percent: int) -> float:
            records = self._records
            
            # have to reverse this since data goes from large to small
            percent = 100 - percent

            k = (len(records) - 1) * (percent / 100)
            f = int(k)
            c = min(f + 1, len(records) - 1)
            return records[f].score + (records[c].score - records[f].score) * (k - f)

        def sum_records(mean: float, power: int) -> float:
            return sum((record.score - mean) ** power for record in self._records)

        self._sort()

        n = len(self._records)
        mean = median = None
        var_population = var_sample = None
        std_population = std_sample = None
        q1 = q2 = q3 = iqr = None
        skewness_population = skewness_sample = None
        kurtosis_population = kurtosis_sample = None

        if n:
            mean = self._total_score / n
            mid = n >> 1
            median = self._records[mid].score if (n & 1) == 0 \
                else (self._records[mid-1].score + self._records[mid].score) / 2

            sum_squared_diff = sum_records(mean=mean, power=2)

            var_population = sum_squared_diff / n
            var_sample = sum_squared_diff / (n - 1) if n > 1 else 0
            
            std_population = var_population ** 0.5
            std_sample = var_sample ** 0.5

            # quantiles
            q1 = percentile(25)
            q2 = percentile(50)
            q3 = percentile(75)
            iqr = q3 - q1

            # skewness
            sum_cubed_diff = sum_records(mean=mean, power=3)
            skewness_population = (sum_cubed_diff / n) / (std_population ** 3)
            skewness_sample = (sum_cubed_diff / n) / (std_sample ** 3)

            # kurtosis
            sum_quartic_diff = sum_records(mean=mean, power=4)
            kurtosis_population = (sum_quartic_diff / n) / (std_population ** 4) - 3
            kurtosis_sample = (sum_quartic_diff / n) / (std_sample ** 4) - 3


        return {
            "name": self.name,
            "timestamp": self.ts.isoformat(),
            "count": n,
            "total_score": self._total_score,
            "mean": mean,
            "median": median,
            "population": {
                "deviation": std_population,
                "variance": var_population,
                "skewness": skewness_population,
                "kurtosis": kurtosis_population,
            },
            "sample": {
                "deviation": std_sample,
                "variance": var_sample,
                "skewness": skewness_sample,
                "kurtosis": kurtosis_sample,
            },
            "quartiles": {
                "q1": q1, 
                "q2": q2, 
                "q3": q3, 
                "iqr": iqr
            },
            "max": self._max.to_dict() if self._max else None,
            "min": self._min.to_dict() if self._min else None,
        }

    def __str__(self) -> str:
        return json_wrapper.to_json(self.to_dict(), separators=(',', ':'))
