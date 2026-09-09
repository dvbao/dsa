"""Focused tests for :class:`ArrayQueue` (10 cases, 4 special cases)."""

import time

import pytest

from dsa.stacks_queues.array_queue import ArrayQueue


PERFORMANCE_LIMIT_SECONDS = 0.1


class TestArrayQueue:
    def test_new_queue_is_empty(self):
        queue = ArrayQueue()

        assert queue.is_empty()
        assert len(queue) == 0

    def test_enqueue_updates_front_and_length(self):
        queue = ArrayQueue()

        queue.enqueue(42)

        assert not queue.is_empty()
        assert len(queue) == 1
        assert queue.front() == 42

    def test_dequeue_uses_fifo_order(self):
        queue = ArrayQueue()
        for value in (1, 2, 3):
            queue.enqueue(value)

        assert [queue.dequeue(), queue.dequeue(), queue.dequeue()] == [1, 2, 3]
        assert queue.is_empty()

    def test_front_does_not_remove_item(self):
        queue = ArrayQueue()
        queue.enqueue("front")

        assert queue.front() == "front"
        assert queue.front() == "front"
        assert len(queue) == 1

    def test_interleaved_enqueue_and_dequeue(self):
        queue = ArrayQueue()
        queue.enqueue(1)
        queue.enqueue(2)
        assert queue.dequeue() == 1
        queue.enqueue(3)

        assert queue.dequeue() == 2
        assert queue.dequeue() == 3
        assert queue.is_empty()

    def test_accepts_none_and_keeps_object_identity(self):
        queue = ArrayQueue()
        marker = object()
        queue.enqueue(None)
        queue.enqueue(marker)

        assert queue.dequeue() is None
        assert queue.front() is marker
        assert queue.dequeue() is marker

    def test_special_empty_operations_raise_and_queue_recovers(self):
        """SPECIAL CASE: missing underflow guards must be detected."""
        queue = ArrayQueue()

        for _ in range(2):
            with pytest.raises(IndexError):
                queue.dequeue()
            with pytest.raises(IndexError):
                queue.front()

        assert len(queue) == 0
        queue.enqueue("usable")
        assert queue.dequeue() == "usable"

    def test_special_circular_wraparound_without_resize(self):
        """SPECIAL CASE: wrapped indices must not overwrite live values."""
        queue = ArrayQueue()
        for value in range(10):
            queue.enqueue(value)
        assert [queue.dequeue() for _ in range(7)] == list(range(7))
        for value in range(10, 17):
            queue.enqueue(value)

        assert queue._capacity == queue.DEFAULT_CAPACITY
        assert [queue.dequeue() for _ in range(10)] == list(range(7, 17))

    def test_special_resize_after_wraparound_preserves_fifo_order(self):
        """SPECIAL CASE: resizing a wrapped array must linearize it correctly."""
        queue = ArrayQueue()
        for value in range(10):
            queue.enqueue(value)
        for _ in range(6):
            queue.dequeue()
        for value in range(10, 17):
            queue.enqueue(value)

        assert queue._capacity == 20
        assert queue._front == 0
        assert [queue.dequeue() for _ in range(11)] == list(range(6, 17))

    def test_special_enqueue_dequeue_performance_is_amortized_constant(self):
        """SPECIAL CASE: 100k FIFO pairs must stay in the time budget."""
        queue = ArrayQueue()
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
