"""Linked list-based stack implementation."""

from dsa.stacks_queues.base import Stack
from typing import TypeVar, Optional

T = TypeVar('T')


class LinkedStack(Stack[T]):
    """Stack implementation using a singly linked list.

    The top of the stack is maintained at the head of the linked list,
    providing O(1) push and pop operations.
    """

    class _Node:
        """A node in the singly linked list."""
        __slots__ = '_element', '_next'

        def __init__(self, element: T, next: Optional['LinkedStack._Node'] = None):
            self._element = element
            self._next = next

    def __init__(self):
        """Create an empty stack."""
        self._head = None
        self._n = 0

    def push(self, item: T) -> None:
        self._head = self._Node(item, self._head)
        self._n += 1

    def pop(self) -> T:
        if self._head is None:
            raise IndexError("pop from empty stack")
        item = self._head._element
        self._head = self._head._next
        self._n -= 1
        return item

    def top(self) -> T:
        if self._head is None:
            raise IndexError("top from empty stack")
        return self._head._element

    def __len__(self) -> int:
        return self._n
