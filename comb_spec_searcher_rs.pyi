import enum
from typing import List, Tuple

class RuleBucket(enum.Enum):
    UNDEFINED = enum.auto()
    VERIFICATION = enum.auto()
    EQUIV = enum.auto()
    NORMAL = enum.auto()
    REVERSE = enum.auto()

class ForestRuleKey:
    parent: int
    bucket: RuleBucket
    children: tuple[int]
    key: tuple[int, tuple[int, ...]]
    shifts: tuple[int]

    def __new__(
        cls,
        parent: int,
        children: Tuple[int, ...],
        shifts: Tuple[int, ...],
        bucket: RuleBucket,
    ): ...

class TableMethod:
    def add_rule_key(self, rule_key: ForestRuleKey) -> None: ...
    def is_pumping(self, label: int) -> bool: ...
    def pumping_subuniverse(self) -> List[ForestRuleKey]: ...
    def status(self) -> str: ...
