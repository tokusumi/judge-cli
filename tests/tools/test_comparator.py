import pytest

from judge.tools import comparator


@pytest.mark.offline
def test_exact():
    assert comparator.ExactComparator()(
        actual=b"abc def\nghi jkl\n", expected=b"abc def\nghi jkl\n"
    )
    assert not comparator.ExactComparator()(
        actual=b"abc def\nghi jkl\n", expected=b"abc def\nghi jkl"
    )
    assert not comparator.ExactComparator()(
        actual=b"abc def\nghi jkl\n", expected=b"abc def\ngh jkl"
    )


@pytest.mark.offline
@pytest.mark.parametrize(
    "tolerance, digit",
    [
        (1e-2, 2),
        (1e-4, 4),
        (1e-9, 9),
        (1e-13, 13),
        (1e-18, 18),
        (1e-27, 27),
    ],
)
def test_fp_num(tolerance: float, digit: int):
    """check accuracy of float point comparator"""
    d0 = "0" * (digit - 2)
    d9 = "9" * (digit - 2)
    # check exact comparison
    comp = comparator.FloatingPointNumberComparator(rel_tol=0.0, abs_tol=0.0)
    assert comp(actual=f"1.{d0}11".encode(), expected=f"1.{d0}11".encode())
    assert not comp(actual=f"1.{d0}11".encode(), expected=f"1.{d0}12".encode())

    # check relative torelance
    comp = comparator.FloatingPointNumberComparator(rel_tol=tolerance, abs_tol=0.0)
    assert comp(actual=f"2.{d0}00".encode(), expected=f"1.{d9}98".encode())
    assert comp(actual=f"2.{d0}00".encode(), expected=f"2.{d0}02".encode())
    assert not comp(actual=f"2.{d0}00".encode(), expected=f"1.{d9}979".encode())
    assert not comp(actual=f"2.{d0}00".encode(), expected=f"2.{d0}021".encode())

    # check absolute torelance
    comp = comparator.FloatingPointNumberComparator(rel_tol=0.0, abs_tol=tolerance)
    assert comp(actual=f"2.{d0}00".encode(), expected=f"2.{d0}01".encode())
    assert comp(actual=f"2.{d0}00".encode(), expected=f"1.{d9}99".encode())
    assert not comp(actual=f"2.{d0}00".encode(), expected=f"2.{d0}011".encode())
    assert not comp(actual=f"2.{d0}00".encode(), expected=f"1.{d9}989".encode())


@pytest.mark.offline
def test_fp_num_not_floatable():
    """check float point comparator when non-FP values is passed"""
    comp = comparator.FloatingPointNumberComparator(rel_tol=1e-1, abs_tol=1e-1)
    assert comp(actual=b"abc def\nghi jkl\n", expected=b"abc def\nghi jkl\n")
    assert not comp(actual=b"1.23", expected=b"abc def\nghi jkl")
    assert not comp(actual=b"abc def\nghi jkl\n", expected=b"1.23")
    assert comp(actual=b"1.23\n", expected=b"1.23")
    assert comp(actual=b"1.23", expected=b"1.23\n")


@pytest.mark.offline
def test_split():
    comp = comparator.SplitComparator(
        comparator.FloatingPointNumberComparator(rel_tol=0.0, abs_tol=1e-1)
    )
    assert not comp(actual=b"1.0 2.0\n", expected=b"1.1\n")
    assert comp(actual=b"1.0 2.0\n", expected=b"1.1 2.0\n")


@pytest.mark.offline
def test_splitlines():
    comp = comparator.SplitLinesComparator(
        comparator.SplitComparator(
            comparator.FloatingPointNumberComparator(rel_tol=0.0, abs_tol=1e-1)
        )
    )
    assert not comp(actual=b"1.0 2.0\n3.0 4.0\n", expected=b"1.1 2.1\n")
    assert comp(actual=b"1.0\n2.0\n", expected=b"1.1\n2.1\n")


@pytest.mark.offline
def test_crlf_insensitive():
    comp = comparator.CRLFInsensitiveComparator(
        comparator.SplitLinesComparator(
            comparator.SplitComparator(
                comparator.FloatingPointNumberComparator(rel_tol=0.0, abs_tol=1e-1)
            )
        )
    )
    assert not comp(actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.1 2.1\r\n")
    assert comp(actual=b"1.0\r\n2.0\r\n", expected=b"1.1\r\n2.1\r\n")


@pytest.mark.offline
def test_exact_match():
    comp = comparator.exact_match()
    assert not comp(actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.1 2.1\r\n")
    assert comp(actual=b"1.0\r\n2.0\r\n", expected=b"1.0\r\n2.0\r\n")

    # not exact match but ignore CRLF, spaces, new line.
    comp = comparator.exact_match(tolerant=1e-1)
    assert not comp(
        actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.4 2.4\r\n3.4 4.4\r\n"
    )
    assert comp(actual=b"1.0  1.0\n2.0\n", expected=b"1.1 1.1\r\n2.1")


@pytest.mark.offline
def test_crlf_insensitive_exact_match():
    # Can ignore difference between \n and \r\n
    comp = comparator.crlf_insensitive_exact_match()
    assert not comp(
        actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.0 2.0\r\n1.1 2.1\r\n"
    )
    assert comp(actual=b"1.0\n2.0\n", expected=b"1.0\r\n2.0\r\n")

    # same as `comparator.exact_match(tolerance=<float>)`
    comp = comparator.crlf_insensitive_exact_match(tolerant=1e-1)
    assert not comp(
        actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.4 2.4\r\n3.4 4.4\r\n"
    )
    assert comp(actual=b"1.0  1.0\n2.0\n", expected=b"1.1 1.1\r\n2.1")


@pytest.mark.offline
def test_ignore_spaces():
    # Can ignore extra spaces and difference between \n and \r\n
    comp = comparator.ignore_spaces()
    assert not comp(actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.02.0\r\n1.1 2.1\r\n")
    assert comp(actual=b"1.0 1.0\n2.0\n", expected=b"1.0   1.0\r\n2.0\r\n")

    # same as `comparator.exact_match(tolerance=<float>)`
    comp = comparator.ignore_spaces(tolerant=1e-1)
    assert not comp(
        actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.4 2.4\r\n3.4 4.4\r\n"
    )
    assert comp(actual=b"1.0  1.0\n2.0\n", expected=b"1.1 1.1\r\n2.1")


@pytest.mark.offline
def test_ignore_spaces_and_newlines():
    # Can ignore extra spaces, extra newlines and difference between \n and \r\n
    comp = comparator.ignore_spaces_and_newlines()
    assert not comp(actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.02.0\r\n1.1 2.1")
    assert comp(actual=b"1.0 1.0\n2.0\n", expected=b"1.0   1.0\r\n2.0")

    # same as `comparator.exact_match(tolerance=<float>)`
    comp = comparator.ignore_spaces_and_newlines(tolerant=1e-1)
    assert not comp(
        actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.4 2.4\r\n3.4 4.4\r\n"
    )
    assert comp(actual=b"1.0  1.0\n2.0\n", expected=b"1.1 1.1\r\n2.1")


@pytest.mark.offline
def test_non_strict():
    # same as `comparator.ignore_spaces_and_newlines(tolerance=None)`
    comp = comparator.non_strict()
    assert not comp(actual=b"1.0 2.0\r\n3.0 4.0\r\n", expected=b"1.02.0\r\n1.1 2.1")
    assert comp(actual=b"1.0 1.0\n2.0\n", expected=b"1.0   1.0\r\n2.0")
