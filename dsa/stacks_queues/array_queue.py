"""Array-based queue implementation."""

from dsa.stacks_queues.base import Queue
from typing import TypeVar
import ctypes

T = TypeVar('T')


class ArrayQueue(Queue[T]):
    """Queue implementation using a circular array.

    Uses a fixed-size array with front and back indices that wrap around.
    The array is resized when capacity is reached.
    """

    DEFAULT_CAPACITY = 10

    def __init__(self):
        """Create an empty queue."""
        self._n = 0
        self._capacity = self.DEFAULT_CAPACITY
        self._A = self._make_array(self._capacity)
        self._front = 0

    def enqueue(self, item: T) -> None:
        if self._n == self._capacity:
            new_capacity = self._capacity * 2
            new_array = self._make_array(new_capacity)
            for index in range(self._n):
                new_array[index] = self._A[(self._front + index) % self._capacity]
            self._A = new_array
            self._capacity = new_capacity
            self._front = 0
        back = (self._front + self._n) % self._capacity
        self._A[back] = item
        self._n += 1

    def dequeue(self) -> T:
        if self._n == 0:
            raise IndexError("dequeue from empty queue")
        item = self._A[self._front]
        self._A[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._n -= 1
        return item

    def front(self) -> T:
        if self._n == 0:
            raise IndexError("front from empty queue")
        return self._A[self._front]

    def __len__(self) -> int:
        return self._n

    def _make_array(self,c):
        return (c * ctypes.py_object) ()    
