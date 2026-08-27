"""Array-based list implementation."""

from dsa.lists.base import Sequence
from typing import TypeVar, Iterator
import ctypes

T = TypeVar('T')


class ArrayList(Sequence[T]):
    """Sequence implementation using a dynamic array.

    *Must* use ctypes array as the underlying storage! Provides O(1) random
    access and O(1) amortized append, but O(n) insertion and deletion
    at arbitrary positions.
    """

    def __init__(self):
        """Create an empty array list."""
        self._n = 0
        self._capacity = 1
        self._A = self._make_array(self._capacity)

    def __getitem__(self, index: int) -> T:
        if index < 0 or index >= self._n:
            raise IndexError("list index out of range")
        return self._A[index]

    def __setitem__(self, index: int, value: T) -> None:
        if index < 0 or index >= self._n:
            raise IndexError("list assignment index out of range")
        self._A[index] = value

    def __delitem__(self, index: int) -> None:
        if index < 0 or index >= self._n:
            raise IndexError("list assignment index out of range")
        for position in range(index, self._n - 1):
            self._A[position] = self._A[position + 1]
        self._A[self._n - 1] = None
        self._n -= 1

    def insert(self, index: int, value: T) -> None:
        if index < 0 or index > self._n:
            raise IndexError("list insertion index out of range")
        if self._n == self._capacity:
            self._capacity *= 2
            new_array = self._make_array(self._capacity)
            for position in range(self._n):
                new_array[position] = self._A[position]
            self._A = new_array
        for position in range(self._n, index, -1):
            self._A[position] = self._A[position - 1]
        self._A[index] = value
        self._n += 1

    def __len__(self) -> int:
        return self._n

    def __iter__(self) -> Iterator[T]:
        for index in range(self._n):
            yield self._A[index]

    def _make_array(self,c):
        return (c * ctypes.py_object) ()
