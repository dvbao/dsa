"""Linked list implementation."""

from dsa.lists.base import Sequence
from typing import TypeVar, Iterator, Optional

T = TypeVar('T')


class LinkedList(Sequence[T]):
    """Sequence implementation using a doubly linked list.

    Each element is stored in a node containing the value and references
    to the previous and next nodes. Provides O(1) insertion/deletion at
    known positions but O(n) random access.
    """

    class _Node:
        """A node in the doubly linked list."""
        __slots__ = '_element', '_prev', '_next'

        def __init__(self, element: T, prev: Optional['LinkedList._Node'] = None,
                     next: Optional['LinkedList._Node'] = None):
            self._element = element
            self._prev = prev
            self._next = next

    def __init__(self):
        """Create an empty linked list."""
        self._head = None
        self._tail = None
        self._n = 0

    def append(self, value: T) -> None:
        new_node = self._Node(value, self._tail, None)
        if self._tail is None:
            self._head = new_node
        else:
            self._tail._next = new_node
        self._tail = new_node
        self._n += 1

    def __getitem__(self, index: int) -> T:
        return self._node_at(index)._element

    def __setitem__(self, index: int, value: T) -> None:
        self._node_at(index)._element = value

    def __delitem__(self, index: int) -> None:
        node = self._node_at(index)
        if node._prev is None:
            self._head = node._next
        else:
            node._prev._next = node._next
        if node._next is None:
            self._tail = node._prev
        else:
            node._next._prev = node._prev
        self._n -= 1

    def insert(self, index: int, value: T) -> None:
        if index < 0 or index > self._n:
            raise IndexError('index out of range')
        if index == self._n:
            self.append(value)
            return

        next_node = self._node_at(index)
        new_node = self._Node(value, next_node._prev, next_node)
        if next_node._prev is None:
            self._head = new_node
        else:
            next_node._prev._next = new_node
        next_node._prev = new_node
        self._n += 1

    def __len__(self) -> int:
        return self._n

    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current is not None:
            yield current._element
            current = current._next

    def _node_at(self, index: int) -> _Node:
        if index < 0 or index >= self._n:
            raise IndexError('index out of range')
        if index < self._n // 2:
            current = self._head
            for _ in range(index):
                current = current._next
        else:
            current = self._tail
            for _ in range(self._n - 1, index, -1):
                current = current._prev
        return current
