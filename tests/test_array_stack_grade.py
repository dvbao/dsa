"""Focused tests for :class:`ArrayStack` (10 cases, 4 special cases)."""

import ctypes
import time

import pytest

from dsa.stacks_queues.array_stack import ArrayStack


PERFORMANCE_LIMIT_SECONDS = 0.1


class TestArrayStack:
    def test_new_stack_is_empty(self):
        stack = ArrayStack()

        assert stack.is_empty()
        assert len(stack) == 0

    def test_push_updates_top_and_length(self):
        stack = ArrayStack()

        stack.push(42)

        assert not stack.is_empty()
        assert len(stack) == 1
        assert stack.top() == 42

    def test_pop_uses_lifo_order(self):
        stack = ArrayStack()
        for value in (1, 2, 3):
            stack.push(value)

        assert [stack.pop(), stack.pop(), stack.pop()] == [3, 2, 1]
        assert stack.is_empty()

    def test_top_does_not_remove_item(self):
        stack = ArrayStack()
        stack.push("top")

        assert stack.top() == "top"
        assert stack.top() == "top"
        assert len(stack) == 1

    def test_interleaved_push_and_pop(self):
        stack = ArrayStack()
        stack.push(1)
        stack.push(2)
        assert stack.pop() == 2
        stack.push(3)

        assert stack.pop() == 3
        assert stack.pop() == 1
        assert stack.is_empty()

    def test_accepts_none_and_keeps_object_identity(self):
        stack = ArrayStack()
        marker = object()
        stack.push(None)
        stack.push(marker)

        assert stack.top() is marker
        assert stack.pop() is marker
        assert stack.pop() is None

    def test_special_empty_operations_raise_and_stack_recovers(self):
        """SPECIAL CASE: missing underflow guards must be detected."""
        stack = ArrayStack()

        for _ in range(2):
            with pytest.raises(IndexError):
                stack.pop()
            with pytest.raises(IndexError):
                stack.top()

        assert len(stack) == 0
        stack.push("usable")
        assert stack.pop() == "usable"

    def test_special_resize_boundaries_preserve_lifo_and_ctypes_storage(self):
        """SPECIAL CASE: repeated doubling must retain every stored value."""
        stack = ArrayStack()
        for value in range(257):
            stack.push(value)

        assert isinstance(stack._A, ctypes.Array)
        assert stack._capacity >= len(stack)
        assert [stack.pop() for _ in range(257)] == list(range(256, -1, -1))

    def test_special_pop_clears_vacated_array_slot(self):
        """SPECIAL CASE: a pop must clear the no-longer-active array slot."""
        stack = ArrayStack()
        payload = object()
        stack.push(payload)

        popped = stack.pop()
        assert popped is payload
        assert stack._A[0] is None

    def test_special_push_pop_performance_is_amortized_constant_time(self):
        """SPECIAL CASE: 100k push/pop pairs must stay inside the time budget."""
        stack = ArrayStack()
        item_count = 100_000

        start = time.perf_counter()
        for value in range(item_count):
            stack.push(value)
        checksum = sum(stack.pop() for _ in range(item_count))
        elapsed = time.perf_counter() - start

        assert elapsed < PERFORMANCE_LIMIT_SECONDS, (
            f"Push/pop of {item_count:,} items took {elapsed:.3f}s; "
            f"limit is {PERFORMANCE_LIMIT_SECONDS:.1f}s"
        )
        assert checksum == item_count * (item_count - 1) // 2
        assert stack.is_empty()
