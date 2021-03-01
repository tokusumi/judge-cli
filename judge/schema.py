from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
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


class BaseJudgeStatus:
    name = ""
    color = ""

    @classmethod
    def style(self) -> str:
        """define output of typer.style"""
        return typer.style(self.__str__(), fg=self.color)

    @classmethod
    def __str__(self) -> str:
        """define standard string output"""
        return self.name


class AC_(BaseJudgeStatus):
    name = "AC"
    color = typer.colors.GREEN


class WA_(BaseJudgeStatus):
    name = "WA"
    color = typer.colors.RED


class RE_(BaseJudgeStatus):
    name = "RE"
    color = typer.colors.RED


class MLE_(BaseJudgeStatus):
    name = "MLE"
    color = typer.colors.YELLOW


class TLE_(BaseJudgeStatus):
    name = "TLE"
    color = typer.colors.YELLOW


class JudgeStatus(Enum):
    AC = AC_
    WA = WA_
    RE = RE_
    TLE = TLE_
    MLE = MLE_


@dataclass
class History:
    status: JudgeStatus
    testcase: TestCasePath
    output: bytes
    exitcode: int
    elapsed: float
    memory: Optional[float] = None
