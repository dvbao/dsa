"""Focused tests for :class:`LinkedQueue` (10 cases, 4 special cases)."""

from collections import deque
import time

import pytest

from dsa.stacks_queues.linked_queue import LinkedQueue


PERFORMANCE_LIMIT_SECONDS = 0.1


class TestLinkedQueue:
    def test_new_queue_is_empty(self):
        queue = LinkedQueue()

        assert queue.is_empty()
        assert len(queue) == 0

    def test_enqueue_updates_front_and_length(self):
        queue = LinkedQueue()

        queue.enqueue(42)

        assert not queue.is_empty()
        assert len(queue) == 1
        assert queue.front() == 42

    def test_dequeue_uses_fifo_order(self):
        queue = LinkedQueue()
        for value in (1, 2, 3):
            queue.enqueue(value)

        assert [queue.dequeue(), queue.dequeue(), queue.dequeue()] == [1, 2, 3]
        assert queue.is_empty()

    def test_front_does_not_remove_item(self):
        queue = LinkedQueue()
        queue.enqueue("front")

        assert queue.front() == "front"
        assert queue.front() == "front"
        assert len(queue) == 1

    def test_interleaved_enqueue_and_dequeue(self):
        queue = LinkedQueue()
        queue.enqueue(1)
        queue.enqueue(2)
        assert queue.dequeue() == 1
        queue.enqueue(3)

        assert queue.dequeue() == 2
        assert queue.dequeue() == 3
        assert queue.is_empty()

    def test_accepts_none_and_keeps_object_identity(self):
        queue = LinkedQueue()
        marker = object()
        queue.enqueue(None)
        queue.enqueue(marker)

        assert queue.dequeue() is None
        assert queue.front() is marker
        assert queue.dequeue() is marker

    def test_special_empty_operations_raise_and_queue_recovers(self):
        """SPECIAL CASE: missing underflow guards must be detected."""
        queue = LinkedQueue()

        for _ in range(2):
            with pytest.raises(IndexError):
                queue.dequeue()
            with pytest.raises(IndexError):
                queue.front()

        assert len(queue) == 0
        queue.enqueue("usable")
        assert queue.dequeue() == "usable"

    def test_special_last_dequeue_resets_tail_and_allows_reuse(self):
        """SPECIAL CASE: removing the only node must reset both pointers."""
        queue = LinkedQueue()

        for value in range(100):
            queue.enqueue(value)
            assert queue.dequeue() == value
            assert queue._head is None
            assert queue._tail is None
            assert len(queue) == 0

        queue.enqueue("reused")
        assert queue.front() == "reused"

    def test_special_long_interleaving_matches_reference_deque(self):
        """SPECIAL CASE: head/tail links remain valid through many transitions."""
        queue = LinkedQueue()
        expected = deque()

        for value in range(5_000):
            queue.enqueue(value)
            expected.append(value)
            if value % 3 == 0:
                assert queue.dequeue() == expected.popleft()

        actual_remainder = [queue.dequeue() for _ in range(len(queue))]
        assert actual_remainder == list(expected)
        assert queue.is_empty()

    def test_special_enqueue_dequeue_performance_is_constant_time(self):
        """SPECIAL CASE: head/tail operations must complete in the time budget."""
        queue = LinkedQueue()
        item_count = 100_000

        start = time.perf_counter()
        for value in range(item_count):
            queue.enqueue(value)
        checksum = sum(queue.dequeue() for _ in range(item_count))
        elapsed = time.perf_counter() - start

        assert elapsed < PERFORMANCE_LIMIT_SECONDS, (
            f"Enqueue/dequeue of {item_count:,} items took {elapsed:.3f}s; "
            f"limit is {PERFORMANCE_LIMIT_SECONDS:.1f}s"
        )
        assert checksum == item_count * (item_count - 1) // 2
        assert queue.is_empty()
