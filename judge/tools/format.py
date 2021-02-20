import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

from onlinejudge.type import TestCase


def percentsplit(s: str) -> Generator[str, None, None]:
    for m in re.finditer("[^%]|%(.)", s):
        yield m.group(0)


@dataclass(frozen=True)
class FormatTable:
    i: str
    e: str
    n: str
    b: str
    d: str


def embedd_percentformat(s: str) -> str:
    result = ""
    for c in percentsplit(s):
        if c.startswith("%"):
            if c[1] == "%":
                result += "%"
            else:
                result += f"{{{c[1]}}}"
        else:
            result += c
    return result
