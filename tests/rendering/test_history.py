from pathlib import Path
import tempfile

from judge.rendering.history import Verbose
from judge.rendering.history import render_history as rh
from judge.schema import History, JudgeStatus, TestCasePath


def render_history(verbose: int) -> None:
    with tempfile.TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir) / "abc000_a"
        tempdir.mkdir(parents=True, exist_ok=True)
        temp_in = tempdir / "temp.in"
        temp_out = tempdir / "temp.out"
        with temp_in.open("wb") as f:
            f.write(b"1 2 3")
        with temp_out.open("wb") as f:
            f.write(b"3164\n1111")

        for status in JudgeStatus:
            history = History(
                status,
                TestCasePath("case 1", temp_in, temp_out),
                output=b"123\n456\n",
                exitcode=0,
                elapsed=10,
                memory=15,
            )
            _verbose: Verbose
            for v in Verbose:
                if verbose == v.value:
                    _verbose = v
            rh(history, _verbose)


def test_rendering_history():
    render_history(2)
    render_history(5)
    render_history(7)
    render_history(10)
