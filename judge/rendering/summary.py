from typing import List

from typer import echo as techo
from typer import secho
from typer import style as tstyle

from judge.schema import History, JudgeStatus


def render_summary(histories: List[History]) -> None:
    judges = {status: 0 for status in JudgeStatus}
    slowest_idx = 0
    max_mem_idx = 0
    for idx, hist in enumerate(histories):
        judges[hist.status] += 1
        if hist.elapsed >= histories[slowest_idx].elapsed:
            slowest_idx = idx
        if hist.memory:
            _max_mem = histories[max_mem_idx].memory
            if not _max_mem:
                max_mem_idx = idx
                continue
            if hist.memory >= _max_mem:
                max_mem_idx = idx

    techo("=====================================================")
    slow = histories[slowest_idx]
    secho(
        f"slowest: {slow.elapsed:.02f} ms (for {slow.testcase.name})",
        fg=(slow.status.value.color if slow.status == JudgeStatus.TLE else None),
    )
    mem = histories[max_mem_idx]
    mem_str = f"{mem.memory:.02f}" if mem.memory else "-"
    secho(
        f"max memory: {mem_str} MB (for {mem.testcase.name})",
        fg=(mem.status.value.color if mem.status == JudgeStatus.MLE else None),
    )

    if judges[JudgeStatus.AC] == len(histories):
        tot_result = tstyle("Success:", fg=JudgeStatus.AC.value.color)
    elif judges[JudgeStatus.WA] or judges[JudgeStatus.RE]:
        tot_result = tstyle("Failure:", fg=JudgeStatus.WA.value.color)
    else:
        tot_result = tstyle("Failure:", fg=JudgeStatus.TLE.value.color)

    message = ", ".join(
        [
            tstyle(f"{num} {status.value.name}", fg=status.value.color)
            for status, num in judges.items()
            if num > 0
        ]
    )
    techo(f"{tot_result} {message} / {len(histories)} cases")
