"""Grading tests for the binary min-heap (6 basic + 4 special)."""

from contextlib import contextmanager
import random
import signal
import threading
import time

import pytest

from dsa.priority_queues.heap import Heap


SPECIAL_TIMEOUT_SECONDS = 4.0


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


class TestHeapGrade:
    # Six basic cases
    def test_new_heap_is_empty(self):
        heap = Heap()

        assert heap.is_empty()
        assert len(heap) == 0

    def test_add_single_item_updates_minimum_and_length(self):
        heap = Heap()
        heap.add(5, "five")

        assert not heap.is_empty()
        assert len(heap) == 1
        assert heap.min() == (5, "five")

    def test_add_maintains_minimum_key(self):
        heap = Heap()
        for key in (8, 3, 5, 1, 9):
            heap.add(key, str(key))

        assert heap.min() == (1, "1")
        assert len(heap) == 5

    def test_remove_min_returns_entries_in_key_order(self):
        heap = Heap()
        for key in (3, 1, 4, 2):
            heap.add(key, str(key))

        assert [heap.remove_min()[0] for _ in range(4)] == [1, 2, 3, 4]
        assert heap.is_empty()

    def test_min_does_not_remove_entry(self):
        heap = Heap()
        heap.add(1, "one")

        assert heap.min() == (1, "one")
        assert heap.min() == (1, "one")
        assert len(heap) == 1

    def test_empty_min_and_remove_raise_index_error(self):
        heap = Heap()

        with pytest.raises(IndexError):
            heap.min()
        with pytest.raises(IndexError):
            heap.remove_min()

    # Four special cases
    def test_special_duplicate_keys_preserve_every_value(self):
        heap = Heap()
        values = [object() for _ in range(5_000)]

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            for value in values:
                heap.add(7, value)
            removed = [heap.remove_min() for _ in values]

        assert all(key == 7 for key, _ in removed)
        assert {id(value) for _, value in removed} == {id(value) for value in values}
        assert heap.is_empty()

    def test_special_extreme_keys_and_interleaved_operations(self):
        heap = Heap()
        huge = 10**300

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            heap.add(huge, "largest")
            heap.add(-huge, "smallest")
            heap.add(0, "zero")
            assert heap.remove_min() == (-huge, "smallest")
            heap.add(-(10**200), "new-smallest")
            remaining = [heap.remove_min() for _ in range(3)]

        assert remaining == [
            (-(10**200), "new-smallest"),
            (0, "zero"),
            (huge, "largest"),
        ]

    def test_special_large_randomized_heap_matches_sorted_reference(self):
        generator = random.Random(23_232)
        keys = list(range(25_000))
        generator.shuffle(keys)
        heap = Heap()

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            for key in keys:
                heap.add(key, -key)
            removed = [heap.remove_min() for _ in keys]

        assert removed == [(key, -key) for key in range(25_000)]
        assert heap.is_empty()

    def test_special_large_workload_has_logarithmic_updates(self):
        item_count = 100_000
        heap = Heap()

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            for key in range(item_count, 0, -1):
                heap.add(key, key)
            checksum = 0
            previous = 0
            while not heap.is_empty():
                key, value = heap.remove_min()
                assert key >= previous
                previous = key
                checksum += value

        assert checksum == item_count * (item_count + 1) // 2
