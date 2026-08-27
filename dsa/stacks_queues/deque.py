"""Array-based deque implementation."""

from dsa.stacks_queues.base import Deque
from typing import TypeVar
import ctypes

T = TypeVar('T')


class ArrayDeque(Deque[T]):
    """Deque implementation using a circular array.

    Uses a fixed-size array with front and back indices that wrap around.
    The array is resized when capacity is reached.
    """

    DEFAULT_CAPACITY = 10

    def __init__(self):
        """Create an empty deque."""
        self._n = 0
        self._capacity = self.DEFAULT_CAPACITY
        self._A = self._make_array(self._capacity)
        self._front = 0

    def add_first(self, item: T) -> None:
        self._resize_if_full()
        self._front = (self._front - 1) % self._capacity
        self._A[self._front] = item
        self._n += 1

    def add_last(self, item: T) -> None:
        self._resize_if_full()
        back = (self._front + self._n) % self._capacity
        self._A[back] = item
        self._n += 1

    def remove_first(self) -> T:
        if self._n == 0:
            raise IndexError("remove_first from empty deque")
        item = self._A[self._front]
        self._A[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._n -= 1
        return item

    def remove_last(self) -> T:
        if self._n == 0:
            raise IndexError("remove_last from empty deque")
        back = (self._front + self._n - 1) % self._capacity
        item = self._A[back]
        self._A[back] = None
        self._n -= 1
        return item

    def first(self) -> T:
        if self._n == 0:
            raise IndexError("first from empty deque")
        return self._A[self._front]

    def last(self) -> T:
        if self._n == 0:
            raise IndexError("last from empty deque")
        return self._A[(self._front + self._n - 1) % self._capacity]

    def __len__(self) -> int:
        return self._n

    def _resize_if_full(self) -> None:
        if self._n < self._capacity:
            return
        new_capacity = self._capacity * 2
        new_array = self._make_array(new_capacity)
        for index in range(self._n):
            new_array[index] = self._A[(self._front + index) % self._capacity]
        self._A = new_array
        self._capacity = new_capacity
        self._front = 0

    def _make_array(self,c):
        return (c * ctypes.py_object) ()
