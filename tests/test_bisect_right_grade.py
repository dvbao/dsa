"""Grading tests for right insertion-point search (6 basic + 4 special)."""

from bisect import bisect_right as reference_bisect_right
from contextlib import contextmanager
from dataclasses import dataclass
import signal
import threading
import time

from dsa.search.bisect_right import bisect_right


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


class TestBisectRightGrade:
    # Six basic cases
    def test_empty_list_returns_zero(self):
        assert bisect_right([], 5) == 0

    def test_inserts_before_first_element(self):
        assert bisect_right([2, 4, 6], 1) == 0

    def test_inserts_after_last_element(self):
        assert bisect_right([2, 4, 6], 7) == 3

    def test_inserts_between_elements(self):
        assert bisect_right([2, 4, 6], 5) == 2

    def test_existing_unique_value_returns_following_index(self):
        assert bisect_right([2, 4, 6], 4) == 2

    def test_duplicates_return_rightmost_insertion_point(self):
        assert bisect_right([1, 2, 2, 2, 3], 2) == 4

    # Four special cases
    def test_special_large_duplicate_runs_choose_the_right_boundary(self):
        data = [-5] * 100_000 + [7] * 300_000 + [11] * 100_000

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            assert bisect_right(data, 7) == 400_000
            assert bisect_right(data, 6) == 100_000

    def test_special_handles_extreme_integer_boundaries(self):
        huge = 10**300
        data = [-huge, -huge, 0, huge, huge]

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            assert bisect_right(data, -huge) == 2
            assert bisect_right(data, huge) == 5
            assert bisect_right(data, -huge - 1) == 0

    def test_special_supports_custom_comparable_objects(self):
        data = [_Record(key) for key in [1, 3, 3, 3, 8]]

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            assert bisect_right(data, _Record(3)) == 4
            assert bisect_right(data, _Record(7)) == 4

    def test_special_many_large_list_queries_are_logarithmic(self):
        data = list(range(0, 2_000_000, 2))
        targets = [(query * 104_729) % 2_000_001 for query in range(20_000)]
        expected = [reference_bisect_right(data, target) for target in targets]

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            actual = [bisect_right(data, target) for target in targets]

        assert actual == expected
