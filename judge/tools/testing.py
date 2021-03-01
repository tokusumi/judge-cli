import concurrent.futures
import contextlib
import os
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, List, Optional

from judge.schema import (CompareMode, History, JudgeStatus, TestCasePath,
                          TimerMode)
from judge.tools import comparator, utils
from judge.tools.format import (construct_relationship_of_files,
                                drop_backup_or_hidden_files, glob_with_format)

MEMORY_WARNING = 500  # megabyte
MEMORY_PRINT = 100  # megabyte


def build_comparater(
    compare_mode: CompareMode,
    error: Optional[float],
    judge_command: Optional[str],
    silent: bool,
) -> comparator.OutputComparator:
    """build_match_function builds the function to compare actual outputs and expected outputs.

    This function doesn't any I/O.
    """

    if judge_command is not None:
        return comparator.SpecialJudge(
            judge_command=judge_command,
            is_silent=silent,
            test_input_path=Path(),
            test_output_path=None,
        )
    elif compare_mode == CompareMode.EXACT_MATCH:
        return comparator.exact_match(error)
    elif compare_mode == CompareMode.CRLF_INSENSITIVE_EXACT_MATCH:
        return comparator.crlf_insensitive_exact_match(error)
    elif compare_mode == CompareMode.IGNORE_SPACES:
        return comparator.ignore_spaces(error)
    elif compare_mode == CompareMode.IGNORE_SPACES_AND_NEWLINES:
        return comparator.ignore_spaces_and_newlines(error)
    else:
        raise ValueError("not defined apropriate match function")


def build_match_call(
    comparater: comparator.OutputComparator,
    test_input_path: Path,
    test_output_path: Optional[Path],
) -> comparator.OutputComparator:
    """build_match_call builds the call method to compare actual outputs and expected outputs.

    This function doesn't any I/O.
    """

    if isinstance(comparater, comparator.SpecialJudge):
        comparater.test_input_path = test_input_path
        comparater.test_expected_path = test_output_path
    return comparater


def run_checking_output(
    answer: bytes,
    test_output_path: Optional[Path],
    match_fn: comparator.OutputComparator,
) -> Optional[bool]:
    """run_checking_output executes matching of the actual output and the expected output.

    This function has file I/O including the execution of the judge command.
    """
    is_special_judge = isinstance(match_fn, comparator.SpecialJudge)
    if test_output_path is None and not is_special_judge:
        return None
    if test_output_path is not None:
        with test_output_path.open("rb") as outf:
            expected = outf.read()
    else:
        # only if --judge option
        expected = b""
    return match_fn(answer, expected)


def judge(
    proc_returncode: Optional[int],
    memory: Optional[float],
    mle: Optional[float],
    is_correct: Optional[bool],
) -> JudgeStatus:
    # check TLE, RE, WA or not
    if proc_returncode is None:
        status = JudgeStatus.TLE
    elif memory is not None and mle is not None and memory > mle:
        status = JudgeStatus.MLE
    elif proc_returncode != 0:
        status = JudgeStatus.RE
    else:
        if is_correct is False:
            status = JudgeStatus.WA
        else:
            status = JudgeStatus.AC
    return status


@dataclass
class TestingArgs:
    testcases: List[TestCasePath]
    command: str
    gnu_time: Optional[str]
    mle: Optional[float]
    tle: Optional[float]
    compare_mode: CompareMode
    jobs: Optional[int] = None
    error: Optional[float] = None
    silent: bool = True
    judge: Optional[str] = None


def test_single_case(
    test_name: str,
    test_input_path: Path,
    test_output_path: Optional[Path],
    comparater: comparator.OutputComparator,
    *,
    lock: Optional[threading.Lock] = None,
    args: TestingArgs,
) -> History:
    # run the binary
    with test_input_path.open("rb") as inf:
        history = utils.exec_command(
            args.command, stdin=inf, timeout=args.tle, gnu_time=args.gnu_time
        )
        # TODO: the `answer` should be bytes, not str
        answer: str = (history.answer or b"").decode(errors="replace")

    # lock is require to avoid mixing logs if in parallel
    nullcontext = (
        contextlib.ExitStack()
    )  # TODO: use contextlib.nullcontext() after updating Python to 3.7
    with lock or nullcontext:
        match_fn = build_match_call(
            comparater=comparater,
            test_input_path=test_input_path,
            test_output_path=test_output_path,
        )
        is_correct = run_checking_output(
            answer=answer.encode(),
            test_output_path=test_output_path,
            match_fn=match_fn,
        )
        status = judge(
            proc_returncode=history.proc.returncode,
            memory=history.memory,
            mle=args.mle,
            is_correct=is_correct,
        )

    return History(
        status=status,
        testcase=TestCasePath(
            name=test_name, in_path=test_input_path, out_path=test_output_path
        ),
        output=answer.encode(),
        exitcode=history.proc.returncode,
        elapsed=history.elapsed,
        memory=history.memory,
    )


def check_gnu_time(gnu_time: str) -> bool:
    if gnu_time != TimerMode.GNU_TIME.value:
        # Only support GNU time
        return False
    gnu_time = "/usr/bin/time"
    try:
        with tempfile.NamedTemporaryFile(delete=True) as fh:
            subprocess.check_call(
                [gnu_time, "-f", "%M KB", "-o", fh.name, "--", "true"]
            )
            with open(fh.name) as fh1:
                data = fh1.read()
            if data:
                return True
    except NameError:
        raise  # NameError is not a runtime error caused by the environment, but a coding mistake
    except AttributeError:
        raise  # AttributeError is also a mistake
    except Exception:
        pass
    return False


@dataclass
class GetTestCasesArgs:
    test: List[Path]
    directory: Path
    format: str
    ignore_backup: bool = True


def get_testcases(args: GetTestCasesArgs) -> List[TestCasePath]:
    # list tests
    if not args.test:
        args.test = glob_with_format(args.directory, args.format)  # by default
    if args.ignore_backup:
        args.test = drop_backup_or_hidden_files(args.test)
    tests = construct_relationship_of_files(args.test)
    return tests


def test(args: TestingArgs) -> Generator[History, None, None]:
    # check wheather GNU time is available
    if args.gnu_time and not check_gnu_time(args.gnu_time):
        # print("GNU time is not available: %s", args.gnu_time)
        args.gnu_time = None
    if args.mle is not None and args.gnu_time is None:
        raise RuntimeError("--mle is used but GNU time does not exist")

    # comparater
    comparater = build_comparater(
        compare_mode=args.compare_mode,
        error=args.error,
        judge_command=args.judge,
        silent=args.silent,
    )

    # run tests
    if args.jobs is None:
        for testcase in sorted(args.testcases, key=lambda f: f.name):
            if not testcase.in_path:
                continue
            yield test_single_case(
                testcase.name,
                testcase.in_path,
                testcase.out_path,
                comparater,
                args=args,
            )
    else:
        if os.name == "nt":
            # logger.warning("-j/--jobs opiton is unstable on Windows environmet")
            pass
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            lock = threading.Lock()
            futures: List[concurrent.futures.Future[History]] = []
            for testcase in sorted(args.testcases, key=lambda f: f.name):
                if not testcase.in_path:
                    continue
                futures += [
                    executor.submit(
                        test_single_case,
                        testcase.name,
                        testcase.in_path,
                        testcase.out_path,
                        comparater,
                        lock=lock,
                        args=args,
                    )
                ]
            for future in futures:
                yield future.result()
