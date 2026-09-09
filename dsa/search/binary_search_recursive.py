"""Recursive binary search algorithm."""

from typing import List, Optional

from dsa.search.base import T


def binary_search_recursive(
    data: List[T],
    target: T,
    low: int = 0,
    high: Optional[int] = None,
) -> Optional[int]:
    """Return an index containing target, or None when target is absent.

    The input list must be sorted in ascending order.

    The low and high parameters identify the current search range. Their
    default values allow callers to start a search with only data and target;
    recursive calls use them to search a smaller range.

    Time complexity: O(log n)
    Space complexity: O(log n) due to the recursion stack

    Args:
        data: A sorted list to search.
        target: The value to search for.
        low: The lower bound of the search range, inclusive.
        high: The upper bound of the search range, inclusive. A value of None
            represents the last index during the initial call.

    Returns:
        The index of target if found, None otherwise.
    """
    if high is None:
        high = len(data) - 1

    if low > high:
        return None

    middle = low + (high - low) // 2

    if data[middle] == target:
        return middle
    if data[middle] < target:
        return binary_search_recursive(data, target, middle + 1, high)
    return binary_search_recursive(data, target, low, middle - 1)
