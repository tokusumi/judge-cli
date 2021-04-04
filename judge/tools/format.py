import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generator, List

from judge.schema import TestCasePath


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


def glob_with_format(directory: Path, format: str) -> List[Path]:
    embeddable_format = embedd_percentformat(format)
    paths = list(directory.glob(embeddable_format.format(s="*", e="*")))
    return paths


def glob_with_samplename(directory: Path, name: str) -> List[Path]:
    paths = list(directory.glob(f"{name}.*"))
    return paths


def is_backup_or_hidden_file(path: Path) -> bool:
    basename = path.name
    return (
        basename.endswith("~")
        or (basename.startswith("#") and basename.endswith("#"))
        or basename.startswith(".")
    )


def drop_backup_or_hidden_files(paths: List[Path]) -> List[Path]:
    result: List[Path] = []
    for path in paths:
        if is_backup_or_hidden_file(path):
            # logger.warning("ignore a backup file: %s", path)
            pass
        else:
            result += [path]
    return result


def construct_relationship_of_files(paths: List[Path]) -> List[TestCasePath]:
    tests: Dict[str, TestCasePath] = {}
    for path in paths:
        name, ext = os.path.splitext(os.path.basename(path))
        if not tests.get(name):
            tests[name] = TestCasePath(name=name)
        if ext == ".in":
            tests[name].in_path = path
        elif ext == ".out":
            tests[name].out_path = path
        else:
            raise FileNotFoundError("unrecognizable file found: %s", path)

    return list(tests.values())
