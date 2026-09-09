"""Focused tests for :class:`ArrayDeque` (10 cases, 4 special cases)."""

import time

import pytest

from dsa.stacks_queues.deque import ArrayDeque


PERFORMANCE_LIMIT_SECONDS = 0.1


class TestArrayDeque:
    def test_new_deque_is_empty(self):
        deque = ArrayDeque()

        assert deque.is_empty()
        assert len(deque) == 0

    def test_add_first_builds_reverse_order(self):
        deque = ArrayDeque()
        for value in (1, 2, 3):
            deque.add_first(value)

        assert deque.first() == 3
        assert deque.last() == 1
        assert len(deque) == 3

    def test_add_last_preserves_order(self):
        deque = ArrayDeque()
        for value in (1, 2, 3):
            deque.add_last(value)

        assert deque.first() == 1
        assert deque.last() == 3
        assert len(deque) == 3

    def test_remove_first_and_last_return_correct_ends(self):
        deque = ArrayDeque()
        for value in (1, 2, 3, 4):
            deque.add_last(value)

        assert deque.remove_first() == 1
        assert deque.remove_last() == 4
        assert deque.remove_first() == 2
        assert deque.remove_last() == 3
        assert deque.is_empty()

    def test_first_and_last_do_not_remove_items(self):
        deque = ArrayDeque()
        deque.add_last("left")
        deque.add_last("right")

        assert deque.first() == "left"
        assert deque.last() == "right"
        assert deque.first() == "left"
        assert deque.last() == "right"
        assert len(deque) == 2

    def test_mixed_operations_support_both_ends(self):
        deque = ArrayDeque()
        deque.add_first(2)
        deque.add_first(1)
        deque.add_last(3)
        deque.add_last(4)

        assert deque.remove_first() == 1
        assert deque.remove_last() == 4
        assert deque.first() == 2
        assert deque.last() == 3

    def test_special_all_empty_operations_raise_and_deque_recovers(self):
        """SPECIAL CASE: all four underflow guards are required."""
        deque = ArrayDeque()

        with pytest.raises(IndexError):
            deque.remove_first()
        with pytest.raises(IndexError):
            deque.remove_last()
        with pytest.raises(IndexError):
            deque.first()
        with pytest.raises(IndexError):
            deque.last()

        assert len(deque) == 0
        deque.add_last("usable")
        assert deque.remove_first() == "usable"

    def test_special_wraparound_at_both_ends_without_resize(self):
        """SPECIAL CASE: wrapped front/back indices must not overwrite data."""
        deque = ArrayDeque()
        for value in range(8):
            deque.add_last(value)
        for _ in range(3):
            deque.remove_first()
        for value in (8, 9, 10):
            deque.add_last(value)
        deque.add_first(2)
        deque.add_first(1)

        assert deque._capacity == deque.DEFAULT_CAPACITY
        assert [deque.remove_first() for _ in range(10)] == list(range(1, 11))

    def test_special_resize_after_wraparound_preserves_both_ends(self):
        """SPECIAL CASE: resizing wrapped storage must keep logical order."""
        deque = ArrayDeque()
        for value in range(10):
            deque.add_last(value)
        for _ in range(6):
            deque.remove_first()
        for value in range(10, 16):
            deque.add_last(value)
        deque.add_first(5)
        deque.add_last(16)

        assert deque._capacity == 20
        assert deque.first() == 5
        assert deque.last() == 16
        assert [deque.remove_first() for _ in range(12)] == list(range(5, 17))

    def test_special_both_end_performance_is_amortized_constant_time(self):
        """SPECIAL CASE: 150k mixed operations must stay in the time budget."""
        deque = ArrayDeque()
        item_count = 50_000

        start = time.perf_counter()
        for value in range(item_count):
            deque.add_last(value)
        for _ in range(item_count // 2):
            deque.remove_first()
        for value in range(item_count // 2):
            deque.add_first(-value)
        while not deque.is_empty():
            deque.remove_last()
        elapsed = time.perf_counter() - start

        assert elapsed < PERFORMANCE_LIMIT_SECONDS, (
            f"{item_count * 3:,} mixed operations took {elapsed:.3f}s; "
            f"limit is {PERFORMANCE_LIMIT_SECONDS:.1f}s"
        )
        assert deque.is_empty()
