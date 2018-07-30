from enum import Enum, auto


class MatchCounts(Enum):
    # More than 1
    MULTIPLE = auto()
    # 1 or more
    SOME = auto()
    # 0 or more
    ANY = auto()
