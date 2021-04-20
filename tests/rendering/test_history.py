import tempfile
from pathlib import Path

from judge.rendering.history import Verbose
from judge.rendering.history import render_history as rh
from judge.schema import History, JudgeStatus, TestCasePath


class Hist:
    def __init__(self, _tempdir: str) -> None:
        tempdir = Path(_tempdir) / "abc000_a"
        tempdir.mkdir(parents=True, exist_ok=True)
        temp_in = tempdir / "temp.in"
        temp_out = tempdir / "temp.out"
        with temp_in.open("wb") as f:
            f.write(b"1 2 3")
        with temp_out.open("wb") as f:
            f.write(b"3164\n1111")
        self.temp_in = temp_in
        self.temp_out = temp_out

    def render_history(self, status: JudgeStatus, verbose: Verbose) -> None:
        history = History(
            status,
            TestCasePath("case 1", self.temp_in, self.temp_out),
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


def test_rendering_history_detail(capsys):
    verb = Verbose.detail
    res_only = "MB\n"
    out = "123\n456\n\n"
    with tempfile.TemporaryDirectory() as _tempdir:
        hist = Hist(_tempdir)

        hist.render_history(JudgeStatus.AC, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(out)

        hist.render_history(JudgeStatus.WA, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(out)

        hist.render_history(JudgeStatus.RE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(out)

        hist.render_history(JudgeStatus.TLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.MLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)


def test_rendering_history_all(capsys):
    verb = Verbose.all
    res_only = "MB\n"
    with tempfile.TemporaryDirectory() as _tempdir:
        hist = Hist(_tempdir)

        hist.render_history(JudgeStatus.AC, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.WA, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.RE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.TLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.MLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)


def test_rendering_history_error_detail(capsys):
    verb = Verbose.error_detail
    no_out = ""
    res_only = "MB\n"
    out = "123\n456\n\n"
    with tempfile.TemporaryDirectory() as _tempdir:
        hist = Hist(_tempdir)

        hist.render_history(JudgeStatus.AC, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(no_out)

        hist.render_history(JudgeStatus.WA, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(out)

        hist.render_history(JudgeStatus.RE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(out)

        hist.render_history(JudgeStatus.TLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.MLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)


def test_rendering_history_error(capsys):
    verb = Verbose.error
    no_out = ""
    res_only = "MB\n"
    with tempfile.TemporaryDirectory() as _tempdir:
        hist = Hist(_tempdir)

        hist.render_history(JudgeStatus.AC, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(no_out)

        hist.render_history(JudgeStatus.WA, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.RE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.TLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)

        hist.render_history(JudgeStatus.MLE, verb)
        cap = capsys.readouterr()
        assert cap.out.endswith(res_only)
