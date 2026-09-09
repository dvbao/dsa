"""Focused tests for :class:`ArrayList` (10 cases, 4 special cases)."""

import ctypes
import time

import pytest

from dsa.lists.array_list import ArrayList


PERFORMANCE_LIMIT_SECONDS = 2.0


class TestArrayList:
    def test_new_list_is_empty(self):
        lst = ArrayList()

        assert lst.is_empty()
        assert len(lst) == 0
        assert list(lst) == []

    def test_append_preserves_order_and_length(self):
        lst = ArrayList()

        for value in (10, 20, 30):
            lst.append(value)

        assert len(lst) == 3
        assert [lst[index] for index in range(len(lst))] == [10, 20, 30]

    def test_getitem_and_setitem(self):
        lst = ArrayList()
        for value in ("a", "b", "c"):
            lst.append(value)

        assert lst[1] == "b"
        lst[1] = "changed"

        assert lst[1] == "changed"
        assert list(lst) == ["a", "changed", "c"]

    def test_insert_at_beginning_middle_and_end(self):
        lst = ArrayList()
        lst.append(2)
        lst.append(4)

        lst.insert(0, 1)
        lst.insert(2, 3)
        lst.insert(len(lst), 5)

        assert list(lst) == [1, 2, 3, 4, 5]

    def test_delete_at_beginning_middle_and_end(self):
        lst = ArrayList()
        for value in range(5):
            lst.append(value)

        del lst[0]
        del lst[1]
        del lst[len(lst) - 1]

        assert list(lst) == [1, 3]
        assert len(lst) == 2

    def test_iteration_contains_and_arbitrary_values(self):
        lst = ArrayList()
        marker = object()
        for value in (None, marker, "text"):
            lst.append(value)

        assert list(iter(lst)) == [None, marker, "text"]
        assert marker in lst
        assert "missing" not in lst

    def test_special_invalid_indices_raise_without_mutating(self):
        """SPECIAL CASE: every invalid boundary must raise and preserve state."""
        lst = ArrayList()
        lst.append(10)
        lst.append(20)

        with pytest.raises(IndexError):
            _ = lst[-1]
        with pytest.raises(IndexError):
            _ = lst[len(lst)]
        with pytest.raises(IndexError):
            lst[-1] = 99
        with pytest.raises(IndexError):
            lst[len(lst)] = 99
        with pytest.raises(IndexError):
            del lst[-1]
        with pytest.raises(IndexError):
            del lst[len(lst)]
        with pytest.raises(IndexError):
            lst.insert(-1, 99)
        with pytest.raises(IndexError):
            lst.insert(len(lst) + 1, 99)

        assert list(lst) == [10, 20]

    def test_special_resize_preserves_values_and_ctypes_storage(self):
        """SPECIAL CASE: cross many capacity boundaries without data loss."""
        lst = ArrayList()

        for value in range(257):
            lst.append(value)

        assert isinstance(lst._A, ctypes.Array)
        assert lst._capacity >= len(lst)
        assert list(lst) == list(range(257))

    def test_special_interleaved_operations_match_python_list(self):
        """SPECIAL CASE: shifting after mixed inserts/deletes matches a model."""
        lst = ArrayList()
        expected = []

        for value in range(300):
            lst.append(value)
            expected.append(value)
            if value % 7 == 0:
                index = len(expected) // 2
                lst.insert(index, -value)
                expected.insert(index, -value)
            if value % 11 == 0:
                index = len(expected) // 3
                del lst[index]
                del expected[index]

        assert list(lst) == expected
        assert len(lst) == len(expected)

    def test_special_append_performance_is_amortized_constant_time(self):
        """SPECIAL CASE: 100k appends must stay within the course time budget."""
        lst = ArrayList()
        item_count = 100_000

        start = time.perf_counter()
        for value in range(item_count):
            lst.append(value)
        elapsed = time.perf_counter() - start

        assert elapsed < PERFORMANCE_LIMIT_SECONDS, (
            f"Appending {item_count:,} items took {elapsed:.3f}s; "
            f"limit is {PERFORMANCE_LIMIT_SECONDS:.1f}s"
        )
        assert len(lst) == item_count
        assert lst[0] == 0
        assert lst[item_count - 1] == item_count - 1
