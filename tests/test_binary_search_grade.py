"""Grading tests for iterative binary search (6 basic + 4 special)."""

from contextlib import contextmanager
from dataclasses import dataclass
import signal
import threading
import time

from dsa.search.binary_search import binary_search


SPECIAL_TIMEOUT_SECONDS = 1.5


@contextmanager
def _time_limit(seconds: float):
    """Limit one special case without relying on a shared conftest file."""
    start = time.perf_counter()
    can_interrupt = (
        hasattr(signal, "setitimer")
        and threading.current_thread() is threading.main_thread()
    )
    if can_interrupt:
        previous_handler = signal.getsignal(signal.SIGALRM)

        def handle_timeout(_signum, _frame):
            raise AssertionError(f"test exceeded the {seconds:.2f}s time limit")

        signal.signal(signal.SIGALRM, handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        if can_interrupt:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_handler)
        elapsed = time.perf_counter() - start
        assert elapsed < seconds, (
            f"test took {elapsed:.3f}s; limit is {seconds:.2f}s"
        )


@dataclass(order=True, frozen=True)
class _Record:
    key: int


class TestBinarySearchGrade:
    # Six basic cases
    def test_empty_list_returns_none(self):
        assert binary_search([], 7) is None

    def test_single_element_found(self):
        assert binary_search([7], 7) == 0

    def test_single_element_missing(self):
        assert binary_search([7], 8) is None

    def test_finds_first_middle_and_last_elements(self):
        data = [1, 3, 5, 7, 9]

        assert binary_search(data, 1) == 0
        assert binary_search(data, 5) == 2
        assert binary_search(data, 9) == 4

    def test_missing_values_inside_and_outside_range(self):
        data = [2, 4, 6, 8]

        assert binary_search(data, 1) is None
        assert binary_search(data, 5) is None
        assert binary_search(data, 9) is None

    def test_supports_negative_values_and_strings(self):
        assert binary_search([-20, -4, -1, 0, 11], -4) == 1
        assert binary_search(["ant", "bee", "cat", "dog"], "cat") == 2

    # Four special cases
    def test_special_large_duplicate_block_returns_a_valid_match(self):
        data = [-1] * 50_000 + [4] * 200_000 + [9] * 50_000

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            index = binary_search(data, 4)

        assert index is not None
        assert 50_000 <= index < 250_000
        assert data[index] == 4

    def test_special_handles_arbitrarily_large_integer_values(self):
        huge = 10**300
        data = [-huge, -(10**150), 0, 10**150, huge]

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            assert binary_search(data, -huge) == 0
            assert binary_search(data, huge) == 4
            assert binary_search(data, huge - 1) is None

    def test_special_searches_custom_comparable_objects(self):
        data = [_Record(key) for key in range(0, 20_000, 2)]
        target = _Record(12_346)

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            index = binary_search(data, target)

        assert index == 6_173
        assert data[index] is target or data[index] == target

    def test_special_many_searches_on_a_large_list_are_logarithmic(self):
        data = list(range(0, 2_000_000, 2))
        targets = [(query * 104_729) % 2_000_000 for query in range(20_000)]

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            results = [binary_search(data, target) for target in targets]

        for target, result in zip(targets, results):
            if target % 2 == 0:
                assert result == target // 2
            else:
                assert result is None
