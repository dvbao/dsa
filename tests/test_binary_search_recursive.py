"""Tests for recursive binary search."""

from dsa.search.binary_search_recursive import binary_search_recursive


class TestBinarySearchRecursive:
    def test_empty_list(self):
        assert binary_search_recursive([], 5) is None

    def test_single_element_found(self):
        assert binary_search_recursive([5], 5) == 0

    def test_single_element_not_found(self):
        assert binary_search_recursive([5], 3) is None

    def test_first_element(self):
        assert binary_search_recursive([1, 2, 3, 4, 5], 1) == 0

    def test_last_element(self):
        assert binary_search_recursive([1, 2, 3, 4, 5], 5) == 4

    def test_middle_element(self):
        assert binary_search_recursive([1, 2, 3, 4, 5], 3) == 2

    def test_not_found(self):
        assert binary_search_recursive([1, 2, 3, 4, 5], 6) is None

    def test_negative_numbers(self):
        assert binary_search_recursive([-5, -3, -1, 0, 2], -1) == 2

    def test_duplicate_value_finds_one_match(self):
        result = binary_search_recursive([1, 2, 2, 2, 3], 2)
        assert result in (1, 2, 3)
