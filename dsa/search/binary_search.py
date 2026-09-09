"""Iterative binary search algorithm."""

from typing import List, Optional, TypeVar

T = TypeVar('T')


def binary_search(data: List[T], target: T) -> Optional[int]:
    """Search for target in a sorted list using binary search.

    Binary search repeatedly divides the search interval in half.
    If the target value is less than the middle element, the search
    continues in the lower half; otherwise, it continues in the upper half.

    Time complexity: O(log n)
    Space complexity: O(1)

    Args:
        data: A sorted list to search.
        target: The value to search for.

    Returns:
        The index of target if found, None otherwise.
    """
    low = 0
    high = len(data) - 1

    while low <= high:
        middle = low + (high - low) // 2

        if data[middle] == target:
            return middle
        if data[middle] < target:
            low = middle + 1
        else:
            high = middle - 1

    return None
