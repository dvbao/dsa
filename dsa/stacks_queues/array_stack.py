"""Array-based stack implementation."""

from dsa.stacks_queues.base import Stack
from typing import TypeVar
import ctypes

T = TypeVar('T')


class ArrayStack(Stack[T]):
    """Stack implementation using a Python list as underlying storage."""

    def __init__(self):
        """Create an empty stack."""
        self._n = 0
        self._capacity = 1
        self._A = self._make_array(self._capacity)

    def push(self, item: T) -> None:
        if self._n == self._capacity:
            self._capacity *= 2
            new_array = self._make_array(self._capacity)
            for index in range(self._n):
                new_array[index] = self._A[index]
            self._A = new_array
        self._A[self._n] = item
        self._n += 1

    def pop(self) -> T:
        if self._n == 0:
            raise IndexError("pop from empty stack")
        self._n -= 1
        item = self._A[self._n]
        self._A[self._n] = None
        return item

    def top(self) -> T:
        if self._n == 0:
            raise IndexError("top from empty stack")
        return self._A[self._n - 1]

    def __len__(self) -> int:
        return self._n

    def _make_array(self,c):
        return (c * ctypes.py_object) ()
