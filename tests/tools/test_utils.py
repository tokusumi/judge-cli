import tempfile
from pathlib import Path
import pytest
from judge.tools.utils import exec_command


@pytest.mark.offline
def test_exec_command():
    with tempfile.TemporaryDirectory() as tempdir:
        temp_dir = Path(tempdir)
        py_dir = temp_dir / "hello.py"
        in_dir = temp_dir / "hello.in"
        with py_dir.open("w") as f:
            f.write("print(input())")
        with in_dir.open("wb") as f:
            f.write(b"hello\n")
        comm = f"python3 {temp_dir / 'hello.py'}"

        with in_dir.open("rb") as f:
            history = exec_command(
                comm,
                stdin=f,
            )
        assert history.elapsed
        print(history)

        # with in_dir.open("rb") as f:
        #     history = exec_command(
        #         comm,
        #         stdin=f,
        #         gnu_time="time",
        #     )
        # assert history.elapsed
        # assert history.memory
        # print(history)

        with in_dir.open("rb") as f:
            history = exec_command(
                comm,
                stdin=f,
                gnu_time="gnu-time",
            )
        assert history.elapsed
        assert history.memory
        print(history)

        with pytest.raises(ValueError):
            with in_dir.open("rb") as f:
                exec_command(
                    comm,
                    stdin=f,
                    gnu_time="gnutime",
                )
