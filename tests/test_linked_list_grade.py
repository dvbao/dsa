"""Focused tests for :class:`LinkedList` (10 cases, 4 special cases)."""

import time

import pytest

from dsa.lists.linked_list import LinkedList


PERFORMANCE_LIMIT_SECONDS = 0.1


class TestLinkedList:
    def test_new_list_is_empty(self):
        lst = LinkedList()

        assert lst.is_empty()
        assert len(lst) == 0
        assert list(lst) == []

    def test_append_preserves_order_and_length(self):
        lst = LinkedList()
        for value in (10, 20, 30):
            lst.append(value)

        assert list(lst) == [10, 20, 30]
        assert len(lst) == 3

    def test_getitem_from_both_halves(self):
        lst = LinkedList()
        for value in range(7):
            lst.append(value)

        assert lst[0] == 0
        assert lst[3] == 3
        assert lst[6] == 6

    def test_setitem_updates_only_target_node(self):
        lst = LinkedList()
        for value in ("a", "b", "c"):
            lst.append(value)

        lst[1] = "changed"

        assert list(lst) == ["a", "changed", "c"]

    def test_insert_at_beginning_middle_and_end(self):
        lst = LinkedList()
        lst.append(2)
        lst.append(4)

        lst.insert(0, 1)
        lst.insert(2, 3)
        lst.insert(len(lst), 5)

        assert list(lst) == [1, 2, 3, 4, 5]

    def test_delete_at_beginning_middle_and_end(self):
        lst = LinkedList()
        for value in range(5):
            lst.append(value)

        del lst[0]
        del lst[1]
        del lst[len(lst) - 1]

        assert list(lst) == [1, 3]
        assert len(lst) == 2

    def test_special_invalid_indices_raise_without_mutating(self):
        """SPECIAL CASE: reject negative/out-of-range access and insertion."""
        lst = LinkedList()
        lst.append(10)
        lst.append(20)

        with pytest.raises(IndexError):
            _ = lst[-1]
        with pytest.raises(IndexError):
            _ = lst[len(lst)]
        with pytest.raises(IndexError):
            lst[-1] = 99
        with pytest.raises(IndexError):
            del lst[len(lst)]
        with pytest.raises(IndexError):
            lst.insert(-1, 99)
        with pytest.raises(IndexError):
            lst.insert(len(lst) + 1, 99)

        assert list(lst) == [10, 20]

    def test_special_single_node_removal_resets_and_allows_reuse(self):
        """SPECIAL CASE: removing the only node must reset head and tail."""
        lst = LinkedList()

        for value in range(50):
            lst.append(value)
            del lst[0]
            assert lst.is_empty()
            assert lst._head is None
            assert lst._tail is None

        lst.append("reused")
        assert list(lst) == ["reused"]

    def test_special_forward_and_backward_links_remain_consistent(self):
        """SPECIAL CASE: mixed mutations must not leave broken node links."""
        lst = LinkedList()
        for value in range(20):
            lst.append(value)
        for index, value in ((0, -1), (11, 99), (len(lst), 20)):
            lst.insert(index, value)
        del lst[0]
        del lst[10]
        del lst[len(lst) - 1]

        forward = []
        previous = None
        node = lst._head
        while node is not None:
            assert node._prev is previous
            forward.append(node._element)
            previous = node
            node = node._next
        assert previous is lst._tail

        backward = []
        following = None
        node = lst._tail
        while node is not None:
            assert node._next is following
            backward.append(node._element)
            following = node
            node = node._prev

        assert forward == list(reversed(backward))
        assert len(forward) == len(lst)

    def test_special_append_and_iteration_performance_is_linear(self):
        """SPECIAL CASE: tail-based append plus iteration must finish quickly."""
        lst = LinkedList()
        item_count = 50_000

        start = time.perf_counter()
        for value in range(item_count):
            lst.append(value)
        checksum = sum(lst)
        elapsed = time.perf_counter() - start

        assert elapsed < PERFORMANCE_LIMIT_SECONDS, (
            f"Appending/iterating {item_count:,} items took {elapsed:.3f}s; "
            f"limit is {PERFORMANCE_LIMIT_SECONDS:.1f}s"
        )
        assert checksum == item_count * (item_count - 1) // 2
