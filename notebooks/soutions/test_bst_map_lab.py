"""Grading tests for the BSTMap Office Hours Lab (instructor/TA use).

Run with:  pytest test_bst_map_lab.py

To grade a specific student, drop their `BSTMap` (Part 1),
`OrderedBSTMap` (Part 2), and/or `can_book` / `next_free_slot` (Part 3)
into `bst_map_lab.py` in place of the reference ones, keep the filename
the same, and rerun this file. `TestBSTMap` covers Part 1,
`TestOrderedBSTMap` covers Part 2, `TestCanBook` and `TestNextFreeSlot`
cover Part 3.
"""

import random
from contextlib import contextmanager

import pytest
from bst_map_lab import (BSTMap, OrderedBSTMap, can_book, next_free_slot,
                         OPEN, CLOSE, SAMPLE_BOOKINGS, to_minutes)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def sample_schedule(chronological=False):
    """The lab's SAMPLE_BOOKINGS, inserted in booking order (or sorted)."""
    rows = sorted(SAMPLE_BOOKINGS, key=lambda r: to_minutes(r[0])) if chronological else SAMPLE_BOOKINGS
    m = OrderedBSTMap()
    for hhmm, name, minutes in rows:
        m[to_minutes(hhmm)] = (name, minutes)
    return m


def check_invariants(m):
    """BST order, parent links both ways, and _size, read from the nodes."""
    keys, stack, node = [], [], m._root
    if node is not None:
        assert node._parent is None, "the root's _parent should be None"
    while stack or node is not None:
        while node is not None:
            for child in (node._left, node._right):
                if child is not None:
                    assert child._parent is node, f"_parent of {child._key} is wrong"
            stack.append(node)
            node = node._left
        node = stack.pop()
        keys.append(node._key)
        node = node._right
    assert keys == sorted(set(keys)), "keys are not in BST order"
    assert len(keys) == m._size == len(m)


def height(node):
    """Number of levels below and including `node` (iterative)."""
    best, stack = 0, [(node, 1)] if node is not None else []
    while stack:
        n, d = stack.pop()
        best = max(best, d)
        stack.extend((c, d + 1) for c in (n._left, n._right) if c is not None)
    return best


def balanced_order(lo, hi):
    """Keys lo..hi in an order that builds a perfectly balanced BST."""
    out, stack = [], [(lo, hi)]
    while stack:
        a, b = stack.pop(0)
        if a > b:
            continue
        mid = (a + b) // 2
        out.append(mid)
        stack.append((a, mid - 1))
        stack.append((mid + 1, b))
    return out


class _Spy:
    def __init__(self, slot, seen):
        self.slot, self.seen = slot, seen

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        self.seen.add(id(obj))
        return self.slot.__get__(obj, objtype)

    def __set__(self, obj, value):
        self.slot.__set__(obj, value)


@contextmanager
def nodes_touched(m):
    """Collect the ids of every node whose _key/_left/_right is read."""
    seen = set()
    node_cls = type(m)._Node
    patched = []
    for name in ("_key", "_left", "_right"):
        for klass in node_cls.__mro__:
            if name in klass.__dict__:
                slot = klass.__dict__[name]
                setattr(klass, name, _Spy(slot, seen))
                patched.append((klass, name, slot))
                break
    try:
        yield seen
    finally:
        for klass, name, slot in patched:
            setattr(klass, name, slot)


def fits(entries, start, minutes):
    """Reference clash check, independent of the student's can_book."""
    return (OPEN <= start and start + minutes <= CLOSE and
            all(not (k < start + minutes and start < k + d) for k, (_, d) in entries.items()))


def brute_free_slot(entries, after, minutes):
    """Minute-by-minute reference answer for next_free_slot."""
    for t in range(max(after, OPEN), CLOSE - minutes + 1):
        if fits(entries, t, minutes):
            return t
    return None


# ---------------------------------------------------------------------
# Part 1
# ---------------------------------------------------------------------
class TestBSTMap:
    """Part 1: the binary search tree."""

    def test_new_map_is_empty(self):
        m = BSTMap()
        assert len(m) == 0
        assert m.is_empty()
        assert m._root is None

    def test_setitem_getitem(self):
        m = BSTMap()
        m[810] = ("Chloe Swift", 20)
        assert m[810] == ("Chloe Swift", 20)
        assert len(m) == 1

    def test_setitem_overwrites_existing_key(self):
        m = BSTMap()
        m[810] = ("Chloe Swift", 20)
        m[810] = ("Chloe Swift", 10)
        assert m[810] == ("Chloe Swift", 10)
        assert len(m) == 1

    def test_contains(self):
        m = BSTMap()
        m[810] = "a"
        assert 810 in m
        assert 811 not in m

    def test_getitem_missing_raises_keyerror(self):
        m = BSTMap()
        m[810] = "a"
        with pytest.raises(KeyError):
            m[811]

    def test_iteration_is_sorted(self):
        m = sample_schedule()
        assert list(m) == sorted(to_minutes(r[0]) for r in SAMPLE_BOOKINGS)

    def test_sample_builds_the_labs_tree(self):
        # Booking order must give the exact tree the lab's screenshots show:
        # root 14:30, children 13:30 / 16:00, 4 levels.
        m = sample_schedule()
        assert m._root._key == to_minutes("14:30")
        assert m._root._left._key == to_minutes("13:30")
        assert m._root._right._key == to_minutes("16:00")
        assert m._root._right._left._key == to_minutes("15:15")
        assert height(m._root) == 4
        check_invariants(m)

    def test_parent_links_after_inserts(self):
        check_invariants(sample_schedule())

    def test_delete_leaf(self):
        m = sample_schedule()
        del m[to_minutes("14:10")]
        assert to_minutes("14:10") not in m
        assert m._root._left._right._right is None   # 13:50's right child
        check_invariants(m)

    def test_delete_node_with_one_child(self):
        m = sample_schedule()
        del m[to_minutes("13:00")]
        assert m._root._left._left._key == to_minutes("13:15")
        assert m._root._left._left._parent is m._root._left
        check_invariants(m)

    def test_delete_node_with_two_children_uses_successor(self):
        m = sample_schedule()
        del m[to_minutes("14:30")]
        assert m._root._key == to_minutes("15:00")       # in-order successor
        assert m._root._right._left._left is None         # successor's old node is gone
        assert len(m) == 11
        check_invariants(m)

    def test_delete_missing_raises_keyerror(self):
        m = sample_schedule()
        with pytest.raises(KeyError):
            del m[to_minutes("15:20")]
        assert len(m) == 12

    def test_delete_everything_in_random_order(self):
        rng = random.Random(232)
        keys = rng.sample(range(1000), 200)
        m = BSTMap()
        for k in keys:
            m[k] = k
        rng.shuffle(keys)
        for i, k in enumerate(keys):
            del m[k]
            if i % 20 == 0:
                check_invariants(m)
        assert len(m) == 0
        assert m._root is None

    def test_sorted_inserts_do_not_hit_the_recursion_limit(self):
        # Task 10's degenerate chain, but long: needs loops, not recursion.
        m = BSTMap()
        for k in range(3000):
            m[k] = k
        assert height(m._root) == 3000
        assert list(m) == list(range(3000))
        assert 2999 in m
        del m[2999]
        assert len(m) == 2999


# ---------------------------------------------------------------------
# Part 2
# ---------------------------------------------------------------------
class TestOrderedBSTMap:
    """Part 2: floor, ceiling, range."""

    def test_floor_exact_between_and_below(self):
        m = sample_schedule()
        assert m.floor_key(to_minutes("15:00")) == to_minutes("15:00")
        assert m.floor_key(to_minutes("15:05")) == to_minutes("15:00")
        assert m.floor_key(to_minutes("23:00")) == to_minutes("16:45")
        assert m.floor_key(to_minutes("12:59")) is None

    def test_ceiling_exact_between_and_above(self):
        m = sample_schedule()
        assert m.ceiling_key(to_minutes("15:15")) == to_minutes("15:15")
        assert m.ceiling_key(to_minutes("15:05")) == to_minutes("15:15")
        assert m.ceiling_key(to_minutes("08:00")) == to_minutes("13:00")
        assert m.ceiling_key(to_minutes("16:46")) is None

    def test_floor_ceiling_on_empty_map(self):
        m = OrderedBSTMap()
        assert m.floor_key(800) is None
        assert m.ceiling_key(800) is None

    def test_floor_ceiling_match_brute_force(self):
        rng = random.Random(7)
        keys = rng.sample(range(0, 500, 3), 60)
        m = OrderedBSTMap()
        for k in keys:
            m[k] = k
        for q in range(-5, 505):
            assert m.floor_key(q) == max((k for k in keys if k <= q), default=None)
            assert m.ceiling_key(q) == min((k for k in keys if k >= q), default=None)

    def test_floor_ceiling_walk_one_path(self):
        # O(h), not O(n): on a balanced tree of 1023 keys (10 levels) a
        # floor/ceiling query must not look at more than one path.
        m = OrderedBSTMap()
        for k in balanced_order(0, 1022):
            m[2 * k] = k
        with nodes_touched(m) as seen:
            assert m.floor_key(701) == 700
        assert len(seen) <= 10
        with nodes_touched(m) as seen:
            assert m.ceiling_key(701) == 702
        assert len(seen) <= 10

    def test_range_inclusive_and_sorted(self):
        m = sample_schedule()
        got = list(m.range_keys(to_minutes("15:00"), to_minutes("15:30")))
        assert got == [to_minutes("15:00"), to_minutes("15:15")]
        everything = list(m.range_keys(0, 24 * 60))
        assert everything == list(m)

    def test_range_empty_cases(self):
        m = sample_schedule()
        assert list(m.range_keys(to_minutes("13:26"), to_minutes("13:29"))) == []
        assert list(m.range_keys(to_minutes("15:30"), to_minutes("15:00"))) == []
        assert list(OrderedBSTMap().range_keys(0, 100)) == []

    def test_range_matches_lab_task_8(self):
        # Task 8: range 15:00-15:30 on the sample tree looks at 5 of 12 nodes.
        m = sample_schedule()
        with nodes_touched(m) as seen:
            list(m.range_keys(to_minutes("15:00"), to_minutes("15:30")))
        assert len(seen) == 5

    def test_range_prunes(self):
        # A narrow range on a big balanced tree must not visit everything.
        m = OrderedBSTMap()
        for k in balanced_order(0, 1022):
            m[k] = k
        with nodes_touched(m) as seen:
            assert list(m.range_keys(500, 504)) == [500, 501, 502, 503, 504]
        assert len(seen) <= 30


# ---------------------------------------------------------------------
# Part 3
# ---------------------------------------------------------------------
class TestCanBook:
    """Part 3: the clash check."""

    def test_empty_schedule_inside_hours(self):
        assert can_book(OrderedBSTMap(), OPEN, 15)
        assert can_book(OrderedBSTMap(), CLOSE - 15, 15)

    def test_outside_office_hours(self):
        m = OrderedBSTMap()
        assert not can_book(m, OPEN - 10, 15)
        assert not can_book(m, CLOSE - 10, 15)
        assert not can_book(m, CLOSE, 10)

    def test_overlaps_the_previous_meeting(self):
        # 13:40 runs into Chloe Swift, 13:30-13:50 (Task 9a).
        assert not can_book(sample_schedule(), to_minutes("13:40"), 10)

    def test_overlaps_the_next_meeting(self):
        # 14:00 for 15 runs into Emma Wilson at 14:10.
        assert not can_book(sample_schedule(), to_minutes("14:00"), 15)

    def test_same_start_as_an_existing_meeting(self):
        assert not can_book(sample_schedule(), to_minutes("15:00"), 10)

    def test_back_to_back_on_both_sides_is_fine(self):
        # 14:00-14:10 touches Daniel Lee's end and Emma Wilson's start (Task 9b).
        assert can_book(sample_schedule(), to_minutes("14:00"), 10)

    def test_matches_brute_force(self):
        m = sample_schedule()
        entries = {k: m[k] for k in m}
        for start in range(OPEN - 20, CLOSE + 5):
            for minutes in (10, 15, 20, 30):
                assert can_book(m, start, minutes) == fits(entries, start, minutes), (start, minutes)


class TestNextFreeSlot:
    """Part 3: the earliest opening."""

    def test_lab_answers(self):
        m = sample_schedule()
        assert next_free_slot(m, to_minutes("13:00"), 10) == to_minutes("14:00")
        assert next_free_slot(m, to_minutes("13:00"), 15) == to_minutes("16:15")
        assert next_free_slot(m, to_minutes("13:00"), 20) is None

    def test_starting_inside_a_running_meeting(self):
        # 13:40 is inside Chloe Swift's meeting (Task 9c, before 14:00 is booked).
        m = sample_schedule()
        assert next_free_slot(m, to_minutes("13:40"), 10) == to_minutes("14:00")

    def test_empty_schedule(self):
        m = OrderedBSTMap()
        assert next_free_slot(m, to_minutes("09:00"), 15) == OPEN
        assert next_free_slot(m, to_minutes("14:07"), 15) == to_minutes("14:07")
        assert next_free_slot(m, CLOSE - 10, 15) is None
        assert next_free_slot(m, CLOSE + 30, 10) is None

    def test_matches_brute_force_on_the_sample(self):
        m = sample_schedule()
        entries = {k: m[k] for k in m}
        for after in range(OPEN - 10, CLOSE + 1):
            for minutes in (10, 15, 20, 30):
                assert next_free_slot(m, after, minutes) == brute_free_slot(entries, after, minutes), \
                    (after, minutes)

    def test_matches_brute_force_on_random_schedules(self):
        rng = random.Random(42)
        for _ in range(40):
            m, entries = OrderedBSTMap(), {}
            for _ in range(rng.randint(0, 14)):
                start, minutes = rng.randrange(OPEN, CLOSE - 10), rng.choice((10, 15, 20, 30))
                if fits(entries, start, minutes):
                    m[start] = entries[start] = ("x", minutes)
            for after in range(OPEN - 15, CLOSE + 1, 11):
                for minutes in (10, 15, 20, 30):
                    assert next_free_slot(m, after, minutes) == brute_free_slot(entries, after, minutes)
