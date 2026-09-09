"""Left insertion-point search for sorted lists."""

from typing import List

from dsa.search.base import T


def bisect_left(data: List[T], target: T) -> int:
    """Return the leftmost index where target can be inserted.

    When target already exists, the returned index is before every existing
    occurrence of target.

    Time complexity: O(log n)
    Space complexity: O(1)
    """
    low = 0
    high = len(data)

    while low < high:
        middle = low + (high - low) // 2

        if data[middle] < target:
            low = middle + 1
        else:
            high = middle

    return low
