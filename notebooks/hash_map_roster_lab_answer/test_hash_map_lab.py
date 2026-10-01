"""Grading tests for the HashMap Roster Lab (instructor/TA use).

Run with:  pytest test_hash_map_lab.py

To grade a specific student, drop their `HashMap` (Part 1) and/or
`LinearProbingMap` (Part 2) class into `hash_map_lab.py` in place of the
reference ones, keep the filename the same, and rerun this file.
`TestHashMap` covers Part 1; `TestLinearProbingMap` covers Part 2.
"""

import pytest
from hash_map_lab import HashMap, LinearProbingMap, AVAILABLE


class TestHashMap:
    """Part 1: separate chaining."""

    def test_new_map_is_empty(self):
        m = HashMap()
        assert len(m) == 0
        assert m.is_empty()

    def test_setitem_getitem(self):
        m = HashMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        assert m[1001] == {"name": "Alice", "gpa": 3.8}

    def test_len_after_one_insert(self):
        m = HashMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        assert len(m) == 1

    def test_setitem_overwrites_existing_key(self):
        m = HashMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        m[1001] = {"name": "Alice", "gpa": 3.9}
        assert m[1001]["gpa"] == 3.9
        assert len(m) == 1

    def test_contains(self):
        m = HashMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        assert 1001 in m
        assert 9999 not in m

    def test_getitem_missing_raises_keyerror(self):
        m = HashMap()
        with pytest.raises(KeyError):
            m[9999]

    def test_iteration_sees_every_key(self):
        m = HashMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        m[1002] = {"name": "Ben", "gpa": 3.2}
        m[1003] = {"name": "Chloe", "gpa": 3.5}
        assert set(m) == {1001, 1002, 1003}

    def test_delitem_removes_key(self):
        m = HashMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        m[1002] = {"name": "Ben", "gpa": 3.2}
        del m[1002]
        assert 1002 not in m
        assert len(m) == 1

    def test_delitem_missing_raises_keyerror(self):
        m = HashMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        with pytest.raises(KeyError):
            del m[9999]

    def test_resizing_keeps_every_entry_reachable(self):
        small = HashMap(capacity=2)
        for i in range(20):
            small[i] = i
        assert len(small) == 20
        assert all(small[i] == i for i in range(20))

    def test_collision_handling_with_forced_small_capacity(self):
        # capacity=3 guarantees at least one collision among 5 distinct keys
        m = HashMap(capacity=3)
        for i in range(5):
            m[i] = i * 10
        assert len(m) == 5
        assert m[0] == 0
        assert m[4] == 40

    def test_deterministic_collision_matches_the_lab(self):
        # 1001 and 1024 differ by exactly 23; once the table resizes to
        # capacity 23 (the same resize the lab's sample data triggers),
        # both must land in the same bucket and both must still be
        # independently reachable.
        m = HashMap(capacity=23)
        m[1001] = "a"
        m[1024] = "b"
        assert m._hash(1001) == m._hash(1024)
        assert m[1001] == "a"
        assert m[1024] == "b"
        assert len(m) == 2


class TestLinearProbingMap:
    """Part 2: open addressing with linear probing."""

    def test_new_map_is_empty(self):
        m = LinearProbingMap()
        assert len(m) == 0
        assert m.is_empty()

    def test_setitem_getitem(self):
        m = LinearProbingMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        assert m[1001] == {"name": "Alice", "gpa": 3.8}

    def test_setitem_overwrites_existing_key(self):
        m = LinearProbingMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        m[1001] = {"name": "Alice", "gpa": 3.9}
        assert m[1001]["gpa"] == 3.9
        assert len(m) == 1

    def test_contains(self):
        m = LinearProbingMap()
        m[1001] = {"name": "Alice", "gpa": 3.8}
        assert 1001 in m
        assert 9999 not in m

    def test_getitem_missing_raises_keyerror(self):
        m = LinearProbingMap()
        with pytest.raises(KeyError):
            m[9999]

    def test_iteration_sees_every_key(self):
        m = LinearProbingMap()
        m[1001] = "a"
        m[1002] = "b"
        m[1003] = "c"
        assert set(m) == {1001, 1002, 1003}

    def test_delitem_removes_key(self):
        m = LinearProbingMap()
        m[1001] = "a"
        m[1002] = "b"
        del m[1002]
        assert 1002 not in m
        assert len(m) == 1

    def test_delitem_missing_raises_keyerror(self):
        m = LinearProbingMap()
        m[1001] = "a"
        with pytest.raises(KeyError):
            del m[9999]

    def test_resizing_keeps_every_entry_reachable(self):
        small = LinearProbingMap(capacity=2)
        for i in range(20):
            small[i] = i
        assert len(small) == 20
        assert all(small[i] == i for i in range(20))

    def test_probing_finds_the_next_open_slot(self):
        # 2000 and 2011 differ by exactly 11, the default capacity, so
        # both hash to slot 9; the second insert must probe forward.
        m = LinearProbingMap(capacity=11)
        m[2000] = "a"
        m[2011] = "b"
        assert m._hash(2000) == m._hash(2011) == 9
        assert m._table[9] == (2000, "a")
        assert m._table[10] == (2011, "b")
        assert m[2000] == "a"
        assert m[2011] == "b"

    def test_deletion_leaves_a_tombstone_not_none(self):
        m = LinearProbingMap(capacity=11)
        m[2000] = "a"
        m[2011] = "b"
        del m[2000]
        assert m._table[9] is AVAILABLE

    def test_lookup_past_a_tombstone_still_finds_the_key(self):
        # This is the whole point of AVAILABLE: deleting the key in the
        # ideal slot must not break lookups for a different key that had
        # to probe past it.
        m = LinearProbingMap(capacity=11)
        m[2000] = "a"
        m[2011] = "b"
        del m[2000]
        assert m[2011] == "b"
        assert 2011 in m

    def test_reinserting_after_a_tombstone_reuses_the_slot(self):
        m = LinearProbingMap(capacity=11)
        m[2000] = "a"
        m[2011] = "b"
        del m[2000]
        m[2000] = "c"
        assert m._table[9] == (2000, "c")
        assert m[2000] == "c"
        assert m[2011] == "b"

    def test_resize_drops_tombstones_and_keeps_live_entries(self):
        m = LinearProbingMap(capacity=11)
        for i in range(5):
            m[i] = i
        del m[0]
        del m[1]
        # size climbs back past the 0.5 threshold during this loop,
        # forcing a resize that rebuilds from scratch and must not
        # resurrect the two deleted keys
        for i in range(100, 105):
            m[i] = i
        assert 0 not in m
        assert 1 not in m
        assert all(k in m for k in (2, 3, 4, 100, 101, 102, 103, 104))
        assert AVAILABLE not in m._table
