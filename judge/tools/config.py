from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Type, TypeVar

import toml
from pydantic import BaseSettings, HttpUrl

from judge.tools.prompt import BasePrompt

if TYPE_CHECKING:
    Model = TypeVar("Model", bound="BaseJudgeConfig")


class BaseJudgeConfig(BasePrompt, BaseSettings):
    """Global configurations."""

    @classmethod
    def from_toml(cls: Type["Model"], path: Path, auto_error: bool = True) -> "Model":
        _path = path / ".judgecli"
        if not path.exists():
            path.mkdir(parents=True)
        if not _path.exists():
            _path.touch()

        d = toml.load(open(_path)).get("judgecli", {})
        if d.get("workdir") is not None:
            if d.get("workdir") != str(path.resolve()):
                raise KeyError("Found irrelevant configuration file.")
        else:
            d["workdir"] = path
        if not d:
            return cls()
        if auto_error:
            return cls(**d)
        else:
            return cls.construct(**d)

    def save(self, path: Path) -> None:
        c_file = path / ".judgecli"
        if not c_file.exists():
            c_file.touch()

        body = toml.load(c_file.open())

        part = body.get("judgecli", {})
        if not isinstance(part, dict):
            raise ValueError("check [judgecli] section in .judgecli")

        for key, value in self.dict().items():
            if isinstance(value, Enum):
                value = value.value
            elif isinstance(value, Path):
                value = str(value.resolve())
            elif isinstance(value, HttpUrl):
                value = str(value)
            part[key] = value
        body["judgecli"] = part
        toml.dump(body, c_file.open("w"))
