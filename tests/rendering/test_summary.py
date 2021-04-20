import tempfile
from pathlib import Path

from judge.rendering.summary import render_summary as rs
from judge.schema import History, JudgeStatus, TestCasePath


def render_summary() -> None:
    with tempfile.TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir) / "abc000_a"
        tempdir.mkdir(parents=True, exist_ok=True)
        temp_in = tempdir / "temp.in"
        temp_out = tempdir / "temp.out"
        with temp_in.open("wb") as f:
            f.write(b"1 2 3")
        with temp_out.open("wb") as f:
            f.write(b"3164\n1111")

        histories = [
            History(
                status,
                TestCasePath(
                    f"sample-{i}",
                    temp_in,
                    temp_out if status != JudgeStatus.RE else None,
                ),
                output=b"123\n456\n" if status != JudgeStatus.RE else b"",
                exitcode=0 if status != JudgeStatus.RE else 1,
                elapsed=10 if status == JudgeStatus.TLE else 1,
                memory=15 if status == JudgeStatus.MLE else 1,
            )
            for i, status in enumerate(JudgeStatus)
        ]
        rs(histories)


def test_rendering_summary():
    render_summary()
