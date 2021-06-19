from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

import typer
from prompt_toolkit import prompt as prompt_toolkit
from prompt_toolkit.completion import Completer, PathCompleter, WordCompleter
from pydantic import BaseSettings, DirectoryPath, FilePath
from pydantic.error_wrappers import ValidationError
from pydantic.fields import ModelField


def type_to_completer(field: ModelField) -> Optional[Completer]:
    type_ = field.type_
    try:
        if issubclass(type_, Enum):
            return WordCompleter([f.value for f in type_])
    except TypeError:
        pass

    if type_ is Path or type_ is FilePath:
        return PathCompleter()
    elif type_ is DirectoryPath:
        return PathCompleter(only_directories=True)

    if field.sub_fields:
        for sub in field.sub_fields:
            completer = type_to_completer(sub)
            if completer:
                return completer
        return None
    return None


def pydantic_prompt(
    msg: str, default: str, field: Optional[ModelField] = None
) -> Callable[[], str]:
    if field is None:
        completer = None
    else:
        completer = type_to_completer(field)
    if default:
        msg = f"{msg} [{default}]"
    msg = f"{msg}: "

    def _pydantic_prompt() -> str:
        """infer type information into prompt for autocompletion"""

        item = prompt_toolkit(
            msg,
            completer=completer,
            complete_in_thread=True,
        )
        return item

    return _pydantic_prompt


class BasePrompt(BaseSettings):
    """Global configurations."""

    def ask(self, key: str, msg: str) -> None:
        field = self.__fields__.get(key)
        if not field:
            return
        default = self.__getattribute__(key)
        _prompt = pydantic_prompt(msg, default=default, field=field)

        for _ in range(5):
            item: Any = _prompt()
            if item == "":
                if default:
                    item = default
                else:
                    item = None
            v_, err_ = field.validate(item, {}, loc=key, cls=self.__class__)
            if not err_:
                self.__setattr__(key, v_)
                return
            else:
                if not isinstance(err_, list):
                    err_ = [err_]
                err = ValidationError(err_, self.__class__)
                try:
                    raise err
                except ValidationError as e:
                    if e:
                        typer.secho(
                            "\n".join([f.get("msg", "") for f in e.errors()]),
                            fg=typer.colors.RED,
                        )
                    continue
