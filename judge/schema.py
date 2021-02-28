from pathlib import Path
from typing import Optional
from enum import Enum
from dataclasses import dataclass
from typing_extensions import Literal


@dataclass(frozen=True)
class Sample:
    ext: Literal["in", "out"]
    path: Path
    data: bytes


@dataclass
class TestCasePath:
    name: str
    in_path: Optional[Path] = None
    out_path: Optional[Path] = None


class CompareMode(Enum):
    EXACT_MATCH = "exact-match"
    CRLF_INSENSITIVE_EXACT_MATCH = "crlf-insensitive-exact-match"
    IGNORE_SPACES = "ignore-spaces"
    IGNORE_SPACES_AND_NEWLINES = "ignore-spaces-and-newlines"


class TimerMode(Enum):
    NO_TIME = ""
    GNU_TIME = "gnu-time"


class JudgeStatus(Enum):
    AC = "AC"
    WA = "WA"
    RE = "RE"
    TLE = "TLE"
    MLE = "MLE"


@dataclass
class History:
    status: JudgeStatus
    testcase: TestCasePath
    output: bytes
    exitcode: int
    elapsed: float
    memory: Optional[float] = None