"""Tests for the left insertion-point search."""

from dsa.search.bisect_left import bisect_left


class TestBisectLeft:
    def test_empty_list(self):
        assert bisect_left([], 5) == 0

    def test_insert_at_beginning(self):
        assert bisect_left([2, 4, 6], 1) == 0

    def test_insert_at_end(self):
        assert bisect_left([2, 4, 6], 7) == 3

    def test_insert_in_middle(self):
        assert bisect_left([2, 4, 6], 3) == 1

    def test_existing_element(self):
        assert bisect_left([2, 4, 6], 4) == 1

    def test_duplicates_returns_leftmost(self):
        assert bisect_left([1, 2, 2, 2, 3], 2) == 1

    def test_all_same_elements(self):
        assert bisect_left([5, 5, 5, 5], 5) == 0
