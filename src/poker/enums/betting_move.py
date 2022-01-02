from enum import Enum, auto


class BettingMove(Enum):
    ALL_IN = auto()
    BET = auto()
    CALLED = auto()
    CHECKED = auto()
    FOLDED = auto()
    RAISED = auto()
