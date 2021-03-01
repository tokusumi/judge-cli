from pathlib import Path

from judge.rendering.history import Verbose
from judge.rendering.history import render_history as rh
from judge.schema import History, JudgeStatus, TestCasePath


def render_history(verbose: int) -> None:
    for status in JudgeStatus:
        history = History(
            status,
            TestCasePath("case 1", Path("temp.in"), Path("temp.out")),
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
