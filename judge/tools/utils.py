from typing import Optional, List, BinaryIO, Callable
import tempfile
import contextlib
import shlex
import time
import os
import subprocess
import sys
from dataclasses import dataclass
import signal

from judge.schema import TimerMode


@dataclass
class ExecArgs:
    command: List[str]
    stdin: Optional[BinaryIO]
    input: Optional[bytes]
    preexec_fn: Optional[Callable[[], None]] = None
    timeout: Optional[float] = None


@dataclass
class History:
    proc: subprocess.Popen
    answer: Optional[bytes] = None
    elapsed: float = -1  # ms
    memory: Optional[float] = None  # MB


def _exec(args: ExecArgs) -> History:
    begin = time.perf_counter()
    try:
        proc = subprocess.Popen(
            args.command,
            stdin=args.stdin,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            preexec_fn=args.preexec_fn,
        )  # pylint: disable=subprocess-popen-preexec-fn
    except FileNotFoundError:
        sys.exit(1)
    except PermissionError:
        sys.exit(1)

    answer: Optional[bytes] = None
    try:
        answer, _ = proc.communicate(input=args.input, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        pass
    finally:
        if args.preexec_fn is not None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            proc.terminate()
    end = time.perf_counter()
    return History(proc=proc, elapsed=1000 * (end - begin), answer=answer)


def _exec_no_time(args: ExecArgs) -> History:
    # TODO: we should use contextlib.nullcontext() if possible
    with contextlib.ExitStack() as fh:
        history = _exec(args)
    return history


def _exec_with_gnu_time(args: ExecArgs) -> History:
    with tempfile.NamedTemporaryFile(delete=True) as fh:
        args.command = [
            "/usr/bin/time",
            "-f",
            "%e\n%M",
            "-o",
            fh.name,
            "--",
        ] + args.command

        # if os.name == "nt":
        #     # HACK: without this encoding and decoding, something randomly fails with multithreading; see https://github.com/kmyk/online-judge-tools/issues/468
        #     command = command_str.encode().decode()  # type: ignore

        # We need kill processes called from the "time" command using process groups. Without this, orphans spawn. see https://github.com/kmyk/online-judge-tools/issues/640
        preexec_fn = None
        if os.name == "posix":
            preexec_fn = os.setsid

        # run command
        history = _exec(args)

        # mesurement memory
        with open(fh.name) as fh1:
            reported = fh1.read()
        if reported.strip():
            ela, mem = reported.splitlines()[-2:]
            history.memory = int(mem) / 1000
            history.elapsed = float(ela) * 1000
    return history


def exec_command(
    command_str: str,
    *,
    stdin: Optional[BinaryIO] = None,
    input: Optional[bytes] = None,
    timeout: Optional[float] = None,
    gnu_time: Optional[str] = None,
) -> History:
    if input is not None:
        assert stdin is None
        stdin = subprocess.PIPE  # type: ignore

    args = ExecArgs(
        command=shlex.split(command_str),
        stdin=stdin,
        input=input,
        timeout=timeout,
    )
    if not gnu_time:
        history = _exec_no_time(args)
    elif gnu_time == TimerMode.GNU_TIME.value:
        history = _exec_with_gnu_time(args)
    else:
        raise ValueError(f"{gnu_time} is expected [None, 'gnu-time']")

    return history