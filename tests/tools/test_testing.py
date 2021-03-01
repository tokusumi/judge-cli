import tempfile
from pathlib import Path

import pytest

from judge.schema import CompareMode
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

        args = testing.GetTestCasesArgs(
            test=None,
            directory=tempdir,
            format=_format,
        )
        testcases = testing.get_testcases(args)

        # answer corrected
        args = testing.TestingArgs(
            testcases=testcases,
            command="python3 -c 'print(input()[0])'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=1e6,
            compare_mode=CompareMode("exact-match"),
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.AC

        # wrong answer
        args = testing.TestingArgs(
            testcases=testcases,
            command="python3 -c 'print(input())'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=1e6,
            compare_mode=CompareMode("exact-match"),
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.WA

        # Syntax error
        args = testing.TestingArgs(
            testcases=testcases,
            command="python3 -c 'print(input()'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=1e6,
            compare_mode=CompareMode("exact-match"),
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.RE

        # time limit error
        args = testing.TestingArgs(
            testcases=testcases,
            command="python3 -c 'print(input())'",
            gnu_time="gnu-time",
            mle=1e5,
            tle=1e-9,
            compare_mode=CompareMode("exact-match"),
            jobs=job,
        )
        histories = testing.test(args)
        for history in histories:
            assert history.status == testing.JudgeStatus.TLE

        # memory limit error
        args = testing.TestingArgs(
            testcases=testcases,
            command="python3 -c 'print(input()[0])'",
            gnu_time="gnu-time",
            mle=1e-9,
            tle=1e6,
            compare_mode=CompareMode("exact-match"),
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

        # answer corrected
        args = testing.TestingArgs(
            testcases=[],
            command="python3 -c 'print(input()[0])'",
            gnu_time="gnu-time",
            mle=None,
            tle=None,
            compare_mode=CompareMode("exact-match"),
            jobs=job,
        )
        histories = testing.test(args)
        _histories = [1 for _ in histories]
        assert not _histories


@pytest.mark.offline
@pytest.mark.parametrize("job", [None, 2])
def test_mode_only_exact(job):
    with tempfile.TemporaryDirectory() as _tempdir:
        _tempdir = Path(_tempdir)
        tempdir = _tempdir / "abc000_a"
        tempdir.mkdir(parents=True, exist_ok=True)

        with (tempdir / "sample-1.in").open("wb") as f:
            f.write(b"1 1 1\n")
        with (tempdir / "sample-1.out").open("wb") as f:
            f.write(b"1 1\n2 2\n\n")

        _format = "sample%s.%e"

        args = testing.GetTestCasesArgs(
            test=None,
            directory=tempdir,
            format=_format,
        )
        testcases = testing.get_testcases(args)

        def helper(answer, mode, status):
            file = _tempdir / "temp.txt"
            with file.open("wb") as f:
                f.write(answer)

            args = testing.TestingArgs(
                testcases=testcases,
                command=f"python3 {file}",
                gnu_time="gnu-time",
                mle=1e5,
                tle=1e6,
                compare_mode=mode,
                jobs=job,
            )
            histories = testing.test(args)
            for history in histories:
                assert history.status == status

        # ignore CRLF
        helper(
            br'print("1 1\r\n2 2\r\n")',
            CompareMode.CRLF_INSENSITIVE_EXACT_MATCH,
            testing.JudgeStatus.AC,
        )

        # not ignore extra spaces
        helper(
            br'print("1     1\n2 2\n")',
            CompareMode.CRLF_INSENSITIVE_EXACT_MATCH,
            testing.JudgeStatus.WA,
        )

        # ignore extra spaces
        helper(
            br'print("1     1\r\n2 2\r\n")',
            CompareMode.IGNORE_SPACES,
            testing.JudgeStatus.AC,
        )

        # cannot ignore extra newlines
        helper(
            br'print("1     1\r\n\r\n2 2")',
            CompareMode.IGNORE_SPACES,
            testing.JudgeStatus.WA,
        )

        # ignore extra newlines
        helper(
            br'print("1     1\r\n\r\n2 2")',
            CompareMode.IGNORE_SPACES_AND_NEWLINES,
            testing.JudgeStatus.AC,
        )
