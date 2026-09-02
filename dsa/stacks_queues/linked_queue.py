"""Linked list-based queue implementation."""

from dsa.stacks_queues.base import Queue
from typing import TypeVar, Optional

T = TypeVar('T')


class LinkedQueue(Queue[T]):
    """Queue implementation using a singly linked list.

    Maintains pointers to both the head (front) and tail (back) of the
    list for O(1) enqueue and dequeue operations.
    """

    class _Node:
        """A node in the singly linked list."""
        __slots__ = '_element', '_next'

        def __init__(self, element: T, next: Optional['LinkedQueue._Node'] = None):
            self._element = element
            self._next = next

    def __init__(self):
        """Create an empty queue."""
        self._head = None
        self._tail = None
        self._n = 0

    def enqueue(self, item: T) -> None:
        new_node = self._Node(item)
        if self._tail is None:
            self._head = new_node
        else:
            self._tail._next = new_node
        self._tail = new_node
        self._n += 1

    def dequeue(self) -> T:
        if self._head is None:
            raise IndexError("dequeue from empty queue")
        item = self._head._element
        self._head = self._head._next
        self._n -= 1
        if self._head is None:
            self._tail = None
        return item

    def front(self) -> T:
        if self._head is None:
            raise IndexError("front from empty queue")
        return self._head._element

    def __len__(self) -> int:
        return self._n
