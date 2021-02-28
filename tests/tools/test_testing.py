import tempfile
from pathlib import Path

import pytest

from judge.tools import testing


@pytest.mark.offline
@pytest.mark.parametrize("job", [None, 2])
def test_judge_status(job):
    with tempfile.TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir) / "abc000_a"
        tempdir.mkdir(parents=True, exist_ok=True)

        with (tempdir / "sample-1.in").open("wb") as f:
            f.write(b"1 1 1\n")
        with (tempdir / "sample-1.out").open("wb") as f:
            f.write(b"1\n")
        with (tempdir / "sample-2.in").open("wb") as f:
            f.write(b"2 2 2\n")
        with (tempdir / "sample-2.out").open("wb") as f:
            f.write(b"2\n")

        _format = "sample%s.%e"

        # answer corrected
        args = testing.TestingArgs(
            test=None,
            directory=tempdir,
            format=_format,
            command="python3 -c 'print(input()[0])'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=None,
            compare_mode="exact-match",
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.AC

        # wrong answer
        args = testing.TestingArgs(
            test=None,
            directory=tempdir,
            format=_format,
            command="python3 -c 'print(input())'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=None,
            compare_mode="exact-match",
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.WA

        # Syntax error
        args = testing.TestingArgs(
            test=None,
            directory=tempdir,
            format=_format,
            command="python3 -c 'print(input()'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=None,
            compare_mode="exact-match",
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.RE

        # time limit error
        args = testing.TestingArgs(
            test=None,
            directory=tempdir,
            format=_format,
            command="python3 -c 'print(input())'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=1e-9,
            compare_mode="exact-match",
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.TLE

        # memory limit error
        args = testing.TestingArgs(
            test=None,
            directory=tempdir,
            format=_format,
            command="python3 -c 'print(input()[0])'",
            gnu_time="gnu-time",
            mle=1e-9,
            tle=None,
            compare_mode="exact-match",
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.MLE


@pytest.mark.offline
@pytest.mark.parametrize("job", [None, 2])
def test_raise(job):
    with tempfile.TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir) / "abc000_a"
        tempdir.mkdir(parents=True, exist_ok=True)

        _format = "sample%s.%e"

        # answer corrected
        args = testing.TestingArgs(
            test=None,
            directory=tempdir,
            format=_format,
            command="python3 -c 'print(input()[0])'",
            gnu_time="gnu-time",
            mle=None,
            tle=None,
            compare_mode="exact-match",
            jobs=job,
        )
        histories = testing.test(args)
        assert len(histories) == 0
