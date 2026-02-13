from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from functools import total_ordering
from typing import Any, List

from src.request.common import HSType
from src.request.dto import HSFilterEntry
from src.stats.common import calc_combat_level
from src.util import json_wrapper


class PlayerRecordInfo(ABC):
    @abstractmethod
    def get_rank(self) -> int:
        pass

    @abstractmethod
    def get_value(self) -> int | float:
        pass


@dataclass
class PlayerRecordScalarInfo(PlayerRecordInfo):
    value: int | float

    def get_rank(self) -> int:
        return -1

    def get_value(self) -> int | float:
        return self.value


@dataclass
class PlayerRecordSkillInfo(PlayerRecordInfo):
    """ Wrapper object to handle playerrecord skill rankings """
    rank: int
    lvl: int
    xp: int

    def get_rank(self) -> int:
        return self.rank

    def get_value(self) -> int:
        return self.lvl


@dataclass
class PlayerRecordMiscInfo(PlayerRecordInfo):
    """ Wrapper object to handle playerrecord misc rankings """
    rank: int
    kc: int

    def get_rank(self) -> int:
        return self.rank

    def get_value(self) -> int:
        return self.kc


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
        self.overall = PlayerRecordSkillInfo(
            rank=first_record[0],
            lvl=first_record[1],
            xp=first_record[2]
        )
        self.combat_lvl = PlayerRecordScalarInfo(value=3)
        self.skills: dict[str, PlayerRecordSkillInfo] = {}
        self.misc: dict[str, PlayerRecordMiscInfo] = {}

        if HSType.csv_len() != len(csv):
            return

        hs_types = list(HSType)

        for hs_type in hs_types[1:]:
            csv_val = hs_type.get_csv_value()

            if csv_val == -1:
                continue

            splitted = [int(x) for x in csv[csv_val].split(',')]

            if hs_type.is_skill():
                self.skills[hs_type.name] = PlayerRecordSkillInfo(
                    rank=splitted[0],
                    lvl=splitted[1],
                    xp=splitted[2]
                )
                # self.skills[hs_type.name] = { 'rank': splitted[0], 'lvl': splitted[1], 'xp': splitted[2] }
                # self.skills[hs_type.name] = splitted[1]
                # just lvl for now, saving rank, lvl, xp and maybe virtual lvl is gonna be too much
                # or have a flag that can enable it

            elif hs_type.is_misc():
                # player can have a score even tho rank is unknown
                if splitted[1] <= 0:
                    continue
                self.misc[hs_type.name] = PlayerRecordMiscInfo(
                    rank=splitted[0],
                    kc=splitted[1]
                )
                # self.misc[hs_type.name] = { 'rank': splitted[0], 'kc': splitted[1] }
                # self.misc[hs_type.name] = splitted[1]

        cmb_level = calc_combat_level(
            attack=self.skills[HSType.attack.name].lvl,
            defence=self.skills[HSType.defence.name].lvl,
            strength=self.skills[HSType.strength.name].lvl,
            hitpoints=self.skills[HSType.hitpoints.name].lvl,
            ranged=self.skills[HSType.ranged.name].lvl,
            prayer=self.skills[HSType.prayer.name].lvl,
            magic=self.skills[HSType.magic.name].lvl
        )

        self.combat_lvl = PlayerRecordScalarInfo(value=cmb_level)

    def get_stat(self, hs_type: HSType) -> PlayerRecordInfo:
        """ 
        Retrieve record value for a given highscore type. 

        Raises:
            ValueError raised if `HSType` is unknown.
        """
        if hs_type is HSType.overall:
            val = self.overall
        elif hs_type is HSType.combat:
            val = self.combat_lvl
        elif hs_type.is_skill():
            val = self.skills.get(
                hs_type.name, PlayerRecordSkillInfo(rank=-1, lvl=-1, xp=-1))
        elif hs_type.is_misc():
            val = self.misc.get(
                hs_type.name, PlayerRecordMiscInfo(rank=-1, kc=-1))
        else:
            raise ValueError(f"Unknown hs type: {hs_type.name}")

        return val

    def lacks_requirements(self, requirements: list[HSFilterEntry]) -> bool:
        """ Check if the player fails any of the given requirements. """
        return not self.meets_requirements(requirements=requirements)

    def meets_requirements(self, requirements: list[HSFilterEntry]) -> bool:
        """ Check if the player satisfies all given requirements. """
        return all(entry.predicate(self.get_stat(entry.hstype).get_value()) for entry in requirements)

    def __lt__(self, other: 'PlayerRecord') -> bool:
        if self.overall.lvl < other.overall.lvl:
            return True
        elif self.overall.lvl == other.overall.lvl \
                and self.overall.xp < other.overall.xp:
            return True
        elif self.overall.xp == other.overall.xp \
                and self.overall.rank > other.overall.rank:
            return True
        return False

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return not self < other and not other < self

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.overall.rank,
            "username": self.username,
            "timestamp": self.ts.isoformat(),
            "total_level": self.overall.lvl,
            "combat_lvl": self.combat_lvl,
            "total_xp": self.overall.xp,
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
        self._max = None
        self._min = None
        self._records: list[CategoryRecord] = []
        self._is_sorted = True
        self._total_score = 0
        self._cached_sum_squared_delta = 0
        self._cached_sum_cubed_delta = 0
        self._cached_sum_quartic_delta = 0

    @property
    def max(self) -> CategoryRecord | None:
        return self._max

    @property
    def min(self) -> CategoryRecord | None:
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
            mean = self._total_score / len(self._records)
            for record in self._records:
                self._cached_sum_squared_delta += (record.score - mean) ** 2
                self._cached_sum_cubed_delta += (record.score - mean) ** 3
                self._cached_sum_quartic_delta += (record.score - mean) ** 4

    def to_dict(self) -> dict[str, Any]:
        def percentile(percent: int) -> float | None:
            if (self.is_empty()):
                return None

            records = self._records
            # have to reverse this since data goes from large to small
            percent = 100 - percent

            k = (n - 1) * (percent / 100)
            f = int(k)
            c = min(f + 1, n - 1)
            return records[f].score + (records[c].score - records[f].score) * (k - f)

        def calc_univariate_analysis(sample: bool) -> tuple[float | None, float | None, float | None, float | None]:
            """ calculates variance, standard deviation, skewness and kurtosis and returns them in that order """
            n = len(self._records)
            n = n if not sample else n - 1

            if n <= 0:
                return (None, None, None, None)

            var = self._cached_sum_squared_delta / n
            std = var ** 0.5
            skew = (self._cached_sum_cubed_delta / n) / (std ** 3)
            kurt = (self._cached_sum_quartic_delta / n) / (std ** 4) - 3

            return (var, std, skew, kurt)

        self._sort()

        # can most likely simplify this entire thing by just using pandas or numpy
        n = len(self._records)
        mean = median = None
        q1, q2, q3 = percentile(25), percentile(50), percentile(75)
        var_population, std_population, skewness_population, kurtosis_population \
            = calc_univariate_analysis(sample=False)
        var_sample, std_sample, skewness_sample, kurtosis_sample \
            = calc_univariate_analysis(sample=True)

        if n:
            mean = self._total_score / n
            mid = n >> 1
            median = self._records[mid].score if (n & 1) == 0 \
                else (self._records[mid-1].score + self._records[mid].score) / 2

        return {
            "name": self.name,
            "timestamp": self.ts.isoformat(),
            "count": n,
            "total_score": self._total_score,
            "mean": mean,
            "median": median,
            "population": {
                "variance": var_population,
                "standard_deviation": std_population,
                "skewness": skewness_population,
                "kurtosis": kurtosis_population,
            },
            "sample": {
                "variance": var_sample,
                "standard_deviation": std_sample,
                "skewness": skewness_sample,
                "kurtosis": kurtosis_sample,
            },
            "quartiles": {
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "iqr": q3 - q1 if q1 and q3 else None
            },
            "max": self._max.to_dict() if self._max else None,
            "min": self._min.to_dict() if self._min else None,
        }

    def __str__(self) -> str:
        return json_wrapper.to_json(self.to_dict(), separators=(',', ':'))
