from pathlib import Path

from judge.rendering.summary import render_summary as rs
from judge.schema import History, JudgeStatus, TestCasePath


def render_summary() -> None:
    histories = [
        History(
            status,
            TestCasePath(
                f"sample-{i}",
                Path("temp.in"),
                Path("temp.out") if status != JudgeStatus.RE else None,
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
