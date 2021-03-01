import tempfile
from pathlib import Path

import pytest

from judge.tools import format


@pytest.mark.offline
def test_glob_with_format():
    with tempfile.TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir) / "abc000_a"
        tempdir.mkdir(parents=True, exist_ok=True)
        # save test case as "sample-%i.%e" format

        with (tempdir / "sample-1.in").open("wb") as f:
            f.write(b"1 1 1\n")
        with (tempdir / "sample-1.out").open("wb") as f:
            f.write(b"1\n")
        with (tempdir / "sample-2.in").open("wb") as f:
            f.write(b"2 2 2\n")
        with (tempdir / "sample-2.out").open("wb") as f:
            f.write(b"2\n")
        with (tempdir / "dummy.txt").open("wb") as f:
            f.write(b"dummy\n")

        _format = "sample%s.%e"
        out = format.glob_with_format(directory=tempdir, format=_format)
        assert len(out) == 4


@pytest.mark.offline
def test_collect_testcase():
    with tempfile.TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir) / "abc000_b"
        tempdir.mkdir(parents=True, exist_ok=True)
        # save test case as "sample-%i.%e" format

        with (tempdir / "sample-1.in").open("wb") as f:
            f.write(b"1 1 1\n")
        with (tempdir / "sample-1.out").open("wb") as f:
            f.write(b"1\n")
        with (tempdir / "sample-2.in").open("wb") as f:
            f.write(b"2 2 2\n")
        with (tempdir / "sample-2.out").open("wb") as f:
            f.write(b"2\n")
        with (tempdir / "dummy.txt").open("wb") as f:
            f.write(b"dummy\n")

        rels = format.construct_relationship_of_files(
            [
                tempdir / "sample-1.in",
                tempdir / "sample-1.out",
                tempdir / "sample-2.in",
                tempdir / "sample-2.out",
            ]
        )
        assert len(rels) == 2

        with pytest.raises(FileNotFoundError):
            format.construct_relationship_of_files(
                [
                    tempdir / "sample-1.in",
                    tempdir / "sample-1.out",
                    tempdir / "sample-2.in",
                    tempdir / "sample-2.out",
                    tempdir / "dummy.txt",
                ]
            )
