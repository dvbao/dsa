"""Binary heap implementation of a priority queue."""

from dsa.priority_queues.base import PriorityQueue
from typing import TypeVar, Tuple, List

K = TypeVar('K')
V = TypeVar('V')


class Heap(PriorityQueue[K, V]):
    """Priority queue implementation using a binary heap.

    A binary heap is a complete binary tree stored in an array where
    each node's key is less than or equal to its children's keys
    (min-heap property).

    Array representation:
        - Root is at index 0
        - For node at index i:
            - Parent is at (i - 1) // 2
            - Left child is at 2 * i + 1
            - Right child is at 2 * i + 2
    """

    def __init__(self):
        """Create an empty heap."""
        self._data: List[Tuple[K, V]] = []

    def __len__(self) -> int:
        return len(self._data)

    def add(self, key: K, value: V) -> None:
        self._data.append((key, value))
        self._upheap(len(self._data) - 1)

    def min(self) -> Tuple[K, V]:
        if self.is_empty():
            raise IndexError("Heap is empty")
        return self._data[0]

    def remove_min(self) -> Tuple[K, V]:
        if self.is_empty():
            raise IndexError("Heap is empty")

        self._swap(0, len(self._data) - 1)
        result = self._data.pop()
        if self._data:
            self._downheap(0)
        return result

    def _parent(self, i: int) -> int:
        """Return the index of the parent of index i."""
        return (i - 1) // 2

    def _left(self, i: int) -> int:
        """Return the index of the left child of index i."""
        return 2 * i + 1

    def _right(self, i: int) -> int:
        """Return the index of the right child of index i."""
        return 2 * i + 2

    def _has_left(self, i: int) -> bool:
        """Return True if index i has a left child."""
        return self._left(i) < len(self._data)

    def _has_right(self, i: int) -> bool:
        """Return True if index i has a right child."""
        return self._right(i) < len(self._data)

    def _swap(self, i: int, j: int) -> None:
        """Swap the elements at indices i and j."""
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _upheap(self, i: int) -> None:
        """Move the element at index i up to restore heap property."""
        while i > 0:
            parent = self._parent(i)
            if self._data[i][0] >= self._data[parent][0]:
                break
            self._swap(i, parent)
            i = parent

    def _downheap(self, i: int) -> None:
        """Move the element at index i down to restore heap property."""
        while self._has_left(i):
            left = self._left(i)
            small_child = left
            if self._has_right(i):
                right = self._right(i)
                if self._data[right][0] < self._data[left][0]:
                    small_child = right

            if self._data[small_child][0] >= self._data[i][0]:
                break
            self._swap(i, small_child)
            i = small_child
