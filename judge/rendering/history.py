from enum import Enum
from pathlib import Path

from typer import echo as techo
from typer import secho
from typer import style as tstyle

from judge.schema import History, JudgeStatus


def file(name: Path) -> str:
    with name.open("r") as f:
        data = f.read()
        return data


class Verbose(int, Enum):
    """
    NOTE: "Result" means judge, case name, elapsed time and memory consumption. "Detail" means input, expected output and our output.

    | verbose | error "Result" | error "Detail" | all "Result" | all "Detail" |
    | --- | --- | --- | --- | --- |
    | error | :heavy_check_mark: | | | |
    | error_detail | :heavy_check_mark: | :heavy_check_mark: | | |
    | all | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | |
    | detail |:heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
    | dd |:heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
    """

    error = 10
    error_detail = 7
    all = 5
    detail = 2
    dd = 0


def render_history(history: History, verbose: Verbose) -> None:

    stat = history.status.value
    if verbose <= Verbose.error:
        if stat != JudgeStatus.AC.value or verbose <= Verbose.all:
            techo("=====================================================")
            elapsed = tstyle(
                f"(Elapsed) {history.elapsed:.02f} ms",
                fg=(stat.color if history.status == JudgeStatus.TLE else None),
            )
            mem_str = f"{history.memory:.02f}" if history.memory else "-"
            memory = tstyle(
                f"(Memory) {mem_str} MB",
                fg=(stat.color if history.status == JudgeStatus.MLE else None),
            )

            techo(f"[{stat.style()}] {history.testcase.name} / {elapsed} / {memory}")

        if verbose <= Verbose.error_detail:
            if stat == JudgeStatus.WA.value or verbose <= Verbose.detail:
                techo("\nInput: ")
                if history.testcase.in_path:
                    techo(file(history.testcase.in_path))

                techo("\nExpected output: ")
                if history.testcase.out_path:
                    techo(file(history.testcase.out_path))

                secho("\nOutput: ", fg=stat.color)
                secho(history.output.decode(), fg=stat.color)
