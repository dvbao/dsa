"""Focused tests for :class:`LinkedStack` (10 cases, 4 special cases)."""

import gc
import time
import weakref

import pytest

from dsa.stacks_queues.linked_stack import LinkedStack


PERFORMANCE_LIMIT_SECONDS = 0.1


class _Payload:
    pass


class TestLinkedStack:
    def test_new_stack_is_empty(self):
        stack = LinkedStack()

        assert stack.is_empty()
        assert len(stack) == 0

    def test_push_updates_top_and_length(self):
        stack = LinkedStack()

        stack.push(42)

        assert not stack.is_empty()
        assert len(stack) == 1
        assert stack.top() == 42

    def test_pop_uses_lifo_order(self):
        stack = LinkedStack()
        for value in (1, 2, 3):
            stack.push(value)

        assert [stack.pop(), stack.pop(), stack.pop()] == [3, 2, 1]
        assert stack.is_empty()

    def test_top_does_not_remove_item(self):
        stack = LinkedStack()
        stack.push("top")

        assert stack.top() == "top"
        assert stack.top() == "top"
        assert len(stack) == 1

    def test_interleaved_push_and_pop(self):
        stack = LinkedStack()
        stack.push(1)
        stack.push(2)
        assert stack.pop() == 2
        stack.push(3)

        assert stack.pop() == 3
        assert stack.pop() == 1
        assert stack.is_empty()

    def test_accepts_none_and_keeps_object_identity(self):
        stack = LinkedStack()
        marker = object()
        stack.push(None)
        stack.push(marker)

        assert stack.pop() is marker
        assert stack.pop() is None

    def test_special_empty_operations_raise_and_stack_recovers(self):
        """SPECIAL CASE: missing underflow guards must be detected."""
        stack = LinkedStack()

        for _ in range(2):
            with pytest.raises(IndexError):
                stack.pop()
            with pytest.raises(IndexError):
                stack.top()

        assert len(stack) == 0
        stack.push("usable")
        assert stack.pop() == "usable"

    def test_special_repeated_single_node_transitions_reset_head(self):
        """SPECIAL CASE: empty/non-empty transitions must not keep stale nodes."""
        stack = LinkedStack()

        for value in range(100):
            stack.push(value)
            assert stack.pop() == value
            assert stack._head is None
            assert len(stack) == 0

        stack.push("reused")
        assert stack.top() == "reused"

    def test_special_pop_releases_removed_node_and_element(self):
        """SPECIAL CASE: popped linked nodes must not retain their element."""
        stack = LinkedStack()
        payload = _Payload()
        reference = weakref.ref(payload)
        stack.push(payload)

        popped = stack.pop()
        assert popped is payload
        del popped
        del payload
        gc.collect()

        assert reference() is None
        assert stack._head is None

    def test_special_push_pop_performance_is_constant_time(self):
        """SPECIAL CASE: linked push/pop must complete within the time budget."""
        stack = LinkedStack()
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
