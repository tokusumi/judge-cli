from enum import Enum
from pathlib import Path
from typing import Optional, Union

from prompt_toolkit.completion import PathCompleter, WordCompleter
from pydantic import BaseModel, DirectoryPath, FilePath

from judge.tools import prompt


def test_type_to_completer():
    class EnumClass(Enum):
        a = "a"
        b = "b"

    class Model(BaseModel):
        enum_: EnumClass
        oenum_: Optional[EnumClass]
        path_: Path
        spath_: Union[Path, str]
        filepath_: FilePath
        directorypath_: DirectoryPath

    fields = Model.__fields__

    comp = prompt.type_to_completer(fields["enum_"])
    assert isinstance(comp, WordCompleter)
    assert comp.words == ["a", "b"]

    comp = prompt.type_to_completer(fields["oenum_"])
    assert isinstance(comp, WordCompleter)
    assert comp.words == ["a", "b"]

    comp = prompt.type_to_completer(fields["path_"])
    assert isinstance(comp, PathCompleter)

    comp = prompt.type_to_completer(fields["spath_"])
    assert isinstance(comp, PathCompleter)

    comp = prompt.type_to_completer(fields["filepath_"])
    assert isinstance(comp, PathCompleter)

    comp = prompt.type_to_completer(fields["directorypath_"])
    assert isinstance(comp, PathCompleter)
    assert comp.only_directories
