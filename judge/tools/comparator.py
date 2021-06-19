import abc
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional


class OutputComparator(abc.ABC):
    @abc.abstractmethod
    def __call__(self, actual: bytes, expected: bytes) -> bool:
        """
        :returns: True is the two are matched.
        """
        ...  # pragma: no cover


class ExactComparator(OutputComparator):
    def __call__(self, actual: bytes, expected: bytes) -> bool:
        return actual == expected


class FloatingPointNumberComparator(OutputComparator):
    def __init__(self, *, rel_tol: float = 1e-09, abs_tol: float = 0.0):
        """
        rel_tol (float): relative tolerance. the maximum allowed difference between actual and expected.
        abs_tol (float): minimum absolute tolerance
        NOTE: Support for tolerance greater than 1e-28.
        """
        if 0 < rel_tol <= 1e-28 or 0 < abs_tol <= 1e-28:
            raise ValueError("Must be tolerance > 1e-28")
        self.rel_tol = Decimal(rel_tol)
        self.abs_tol = Decimal(abs_tol)

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        """
        If no errors occur, the result will be: abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol).
        :returns: True if the relative error or absolute error is smaller than the accepted error
        NOTE: If expected or actual is not float, this is equivalent with Exact Comparator
        """
        try:
            x = Decimal(actual.decode())
            y = Decimal(expected.decode())
        except InvalidOperation:
            return actual == expected

        # decimal.Decimal friendly (high accurate) version of math.isclose
        diff = abs(x - y)
        return ((diff <= abs(self.rel_tol * y)) or (diff <= abs(self.rel_tol * x))) or (
            diff <= self.abs_tol
        )


class SplitComparator(OutputComparator):
    def __init__(self, word_comparator: OutputComparator):
        self.word_comparator = word_comparator

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        # str.split() also removes trailing '\r'
        actual_words = actual.split()
        expected_words = expected.split()
        if len(actual_words) != len(expected_words):
            return False
        for x, y in zip(actual_words, expected_words):
            if not self.word_comparator(x, y):
                return False
        return True


class SplitLinesComparator(OutputComparator):
    def __init__(self, line_comparator: OutputComparator):
        self.line_comparator = line_comparator

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        actual_lines = actual.rstrip(b"\n").split(b"\n")
        expected_lines = expected.rstrip(b"\n").split(b"\n")
        if len(actual_lines) != len(expected_lines):
            return False
        for x, y in zip(actual_lines, expected_lines):
            if not self.line_comparator(x, y):
                return False
        return True


class CRLFInsensitiveComparator(OutputComparator):
    def __init__(self, file_comparator: OutputComparator):
        self.file_comparator = file_comparator

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        return self.file_comparator(
            actual.replace(b"\r\n", b"\n"), expected.replace(b"\r\n", b"\n")
        )


def exact_match(tolerant: Optional[float] = None) -> OutputComparator:
    # if tolerant is None, is_exact=True
    if tolerant is None:
        return ExactComparator()

    return CRLFInsensitiveComparator(
        SplitLinesComparator(
            SplitComparator(
                FloatingPointNumberComparator(rel_tol=tolerant, abs_tol=tolerant)
            )
        )
    )


def crlf_insensitive_exact_match(tolerant: Optional[float] = None) -> OutputComparator:
    # if tolerant is None, is_exact=True
    if tolerant is None:
        return CRLFInsensitiveComparator(ExactComparator())

    return CRLFInsensitiveComparator(
        SplitLinesComparator(
            SplitComparator(
                FloatingPointNumberComparator(rel_tol=tolerant, abs_tol=tolerant)
            )
        )
    )


def ignore_spaces(tolerant: Optional[float] = None) -> OutputComparator:
    if tolerant is None:
        word_comparator = ExactComparator()
    else:
        word_comparator = FloatingPointNumberComparator(
            rel_tol=tolerant, abs_tol=tolerant
        )  # type: ignore
    return CRLFInsensitiveComparator(
        SplitLinesComparator(SplitComparator(word_comparator))
    )


def ignore_spaces_and_newlines(tolerant: Optional[float] = None) -> OutputComparator:
    if tolerant is None:
        word_comparator = ExactComparator()
    else:
        word_comparator = FloatingPointNumberComparator(
            rel_tol=tolerant, abs_tol=tolerant
        )  # type: ignore
    return CRLFInsensitiveComparator(SplitComparator(word_comparator))


def non_strict() -> OutputComparator:
    """the result of exact match (non tolerant) as follows,
    - CompareMode.EXACT_MATCH
    - CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
    may turns to be AC if spaces and newlines were ignored.
    It happens if this comparater evaluate it as AC.

    NOTE: this is alias of ignore_spaces_and_newlines for non fp match
    """
    return ignore_spaces_and_newlines(tolerant=None)


class SpecialJudge(OutputComparator):
    def __init__(
        self,
        judge_command: str,
        is_silent: bool,
        test_input_path: Path,
        test_output_path: Optional[Path],
    ):
        self.judge_command = judge_command  # already quoted and joined command
        self.is_silent = is_silent
        self.test_input_path = test_input_path
        self.test_expected_path = test_output_path

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        return self.run(
            actual_output=actual,
            input_path=self.test_input_path,
            expected_output_path=self.test_expected_path,
        )

    def run(
        self,
        *,
        actual_output: bytes,
        input_path: Path,
        expected_output_path: Optional[Path]
    ) -> bool:
        """
        with tempfile.TemporaryDirectory() as tempdir:
            actual_output_path = Path(tempdir) / "actual.out"
            with open(actual_output_path, "wb") as fh:
                fh.write(actual_output)

            # if you use shlex.quote, it fails on Windows. why?
            command = " ".join(
                [
                    self.judge_command,  # already quoted and joined command
                    str(input_path.resolve()),
                    str(actual_output_path.resolve()),
                    str(
                        expected_output_path.resolve()
                        if expected_output_path is not None
                        else ""
                    ),
                ]
            )
            history = exec_command(command)
        return history.proc.returncode == 0
        """
        # not supported yet
        return True
