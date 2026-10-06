"""Reference solution for the BSTMap Office Hours Lab (instructor use only).

Same class and function signatures students see in
notebooks/problems/bst_map_office_hours_lab.ipynb: Part 1 (`BSTMap`),
Part 2 (`OrderedBSTMap`: floor, ceiling, range) and Part 3 (`can_book`,
`next_free_slot`), with every piece filled in.

Grading workflow: to check a specific student's submission, copy their
`BSTMap`, `OrderedBSTMap`, `can_book` and/or `next_free_slot` from their
notebook into a copy of this file, keeping the filename `bst_map_lab.py`,
then run:

    pytest test_bst_map_lab.py

against it from this folder.
"""

from typing import TypeVar, Generic, Iterator, Optional

K = TypeVar('K')
V = TypeVar('V')

# Office hours run from 13:00 to 17:00. Times are stored as minutes since
# midnight, so 13:00 is 780 and 17:00 is 1020.
OPEN = 13 * 60
CLOSE = 17 * 60


def to_minutes(hhmm: str) -> int:
    """'13:45' -> 825 (minutes since midnight)."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def fmt(minutes: int) -> str:
    """825 -> '13:45'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class BSTMap(Generic[K, V]):
    """A map implemented as an unbalanced binary search tree.

    BST property: for every node, every key in its LEFT subtree is
    smaller than the node's key, and every key in its RIGHT subtree is
    larger. Every method below uses that one rule to decide which way
    to walk.
    """

    class _Node:
        """One node of the tree. Provided, nothing to edit here."""
        __slots__ = '_key', '_value', '_left', '_right', '_parent'

        def __init__(self, key, value, parent=None):
            self._key = key
            self._value = value
            self._left = None
            self._right = None
            self._parent = parent

    def __init__(self):
        """Create an empty map.

        Store the root node in `self._root` (None while the tree is
        empty) and the number of entries in `self._size`, starting at 0.
        """
        self._root = None
        self._size = 0

    def __len__(self) -> int:
        """Return the number of key-value pairs stored (self._size)."""
        return self._size

    def _search(self, key: K, node) -> Optional['BSTMap._Node']:
        """Walk down from `node` looking for `key`.

        Return the node whose key equals `key`, or None once you fall
        off the bottom of the tree. Use a loop, not recursion.
        """
        while node is not None:
            if key == node._key:
                return node
            if key < node._key:
                node = node._left
            else:
                node = node._right
        return None

    def __getitem__(self, key: K) -> V:
        """Return the value stored for `key`.

        Raises:
            KeyError: if `key` is not present.
        """
        node = self._search(key, self._root)
        if node is None:
            raise KeyError(key)
        return node._value

    def __contains__(self, key: K) -> bool:
        """Return True if `key` is currently stored."""
        return self._search(key, self._root) is not None

    def __setitem__(self, key: K, value: V) -> None:
        """Associate `value` with `key`.

        Walk down from the root the same way `_search` does:
          * if you reach a node with this exact key, overwrite its value
            (the size does NOT change);
          * otherwise, when the next step would be None, attach a new
            node there as a leaf. Pass `parent=` so the new node knows
            its parent, and add 1 to `self._size`.

        Use a loop, not recursion: Task 10 builds a tree that is one
        long chain.
        """
        if self._root is None:
            self._root = self._Node(key, value)
            self._size = 1
            return

        node = self._root
        while True:
            if key == node._key:
                node._value = value
                return
            if key < node._key:
                if node._left is None:
                    node._left = self._Node(key, value, parent=node)
                    self._size += 1
                    return
                node = node._left
            else:
                if node._right is None:
                    node._right = self._Node(key, value, parent=node)
                    self._size += 1
                    return
                node = node._right

    def __delitem__(self, key: K) -> None:
        """Remove `key` and its value.

        Three cases:
          * 0 children: unhook the node from its parent.
          * 1 child: the child moves up and takes the node's place.
          * 2 children: copy the key and value of the node's in-order
            successor (the smallest key in its RIGHT subtree, see
            `_subtree_min`) into the node, then remove the successor's
            node instead. The successor never has a left child, so
            removing it is always case 0 or case 1.

        When a child moves up, fix BOTH directions of the link: the
        parent's `_left` or `_right` must point to the child, and the
        child's `_parent` must point to the parent. If the removed node
        was the root, update `self._root`.

        Raises:
            KeyError: if `key` is not present.
        """
        node = self._search(key, self._root)
        if node is None:
            raise KeyError(key)

        if node._left is not None and node._right is not None:
            successor = self._subtree_min(node._right)
            node._key = successor._key
            node._value = successor._value
            node = successor

        child = node._left if node._left is not None else node._right
        if child is not None:
            child._parent = node._parent

        if node._parent is None:
            self._root = child
        elif node is node._parent._left:
            node._parent._left = child
        else:
            node._parent._right = child

        self._size -= 1

    def __iter__(self) -> Iterator[K]:
        """Yield every key in increasing order (in-order traversal).

        Use an explicit stack instead of recursion: go left as far as
        you can, pushing every node on the way; pop one, yield its key,
        then continue the same way from its right child.
        """
        stack = []
        node = self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node._left
            node = stack.pop()
            yield node._key
            node = node._right

    def _subtree_min(self, node) -> 'BSTMap._Node':
        """Return the node with the smallest key in the subtree rooted
        at `node`."""
        while node._left is not None:
            node = node._left
        return node

    def _subtree_max(self, node) -> 'BSTMap._Node':
        """Return the node with the largest key in the subtree rooted
        at `node`."""
        while node._right is not None:
            node = node._right
        return node

    def is_empty(self) -> bool:
        """Return True if the map contains no key-value pairs."""
        return len(self) == 0


class OrderedBSTMap(BSTMap[K, V]):
    """A BSTMap that can also answer "nearest key" questions.

    Part 1's `_search` can only answer "is this exact key here?". The
    methods below answer questions about keys that are NOT in the map,
    which is what a schedule really needs ("who is in the room at
    15:05?" when nobody booked exactly 15:05).
    """

    def floor_key(self, key: K) -> Optional[K]:
        """Return the largest stored key that is <= `key`, or None if
        every stored key is larger.

        Walk down from the root exactly like `_search`. Every time you
        step RIGHT, the node you are leaving is smaller than `key`, so
        it is a candidate answer: remember it. When you fall off the
        tree, the last candidate you remembered is the answer. One walk,
        O(h), no matter how many keys are stored.
        """
        best = None
        node = self._root
        while node is not None:
            if key == node._key:
                return node._key
            if key < node._key:
                node = node._left
            else:
                best = node._key
                node = node._right
        return best

    def ceiling_key(self, key: K) -> Optional[K]:
        """Return the smallest stored key that is >= `key`, or None if
        every stored key is smaller.

        Mirror image of `floor_key`: remember the node every time you
        step LEFT.
        """
        best = None
        node = self._root
        while node is not None:
            if key == node._key:
                return node._key
            if key < node._key:
                best = node._key
                node = node._left
            else:
                node = node._right
        return best

    def range_keys(self, lo: K, hi: K) -> Iterator[K]:
        """Yield every stored key k with lo <= k <= hi, in increasing
        order. Start the walk at the root (see `_range`)."""
        yield from self._range(self._root, lo, hi)

    def _range(self, node, lo: K, hi: K) -> Iterator[K]:
        """Yield the keys in [lo, hi] from the subtree rooted at `node`,
        in increasing order, WITHOUT visiting the whole tree:

          * only go into the left subtree if lo < node's key
            (otherwise everything down there is too small);
          * yield the node's own key if lo <= key <= hi;
          * only go into the right subtree if node's key < hi
            (otherwise everything down there is too big).

        Recursion is fine here: `yield from self._range(child, lo, hi)`.
        """
        if node is None:
            return
        if lo < node._key:
            yield from self._range(node._left, lo, hi)
        if lo <= node._key <= hi:
            yield node._key
        if node._key < hi:
            yield from self._range(node._right, lo, hi)


def can_book(schedule: OrderedBSTMap, start: int, duration: int) -> bool:
    """Return True if a meeting [start, start + duration) can be added.

    It can be added only if:
      * it fits inside office hours: OPEN <= start and
        start + duration <= CLOSE, and
      * it does not overlap any booking already in `schedule`.

    `schedule` maps start minute -> (name, duration). Meetings are
    half-open intervals: one that ends at 14:00 does NOT clash with one
    that starts at 14:00.

    You only need two lookups: `schedule.floor_key(start)` and
    `schedule.ceiling_key(start)`. Task 9 asks you why two are enough.
    """
    if start < OPEN or start + duration > CLOSE:
        return False

    prev = schedule.floor_key(start)
    if prev is not None:
        _, prev_duration = schedule[prev]
        if prev + prev_duration > start:
            return False

    nxt = schedule.ceiling_key(start)
    if nxt is not None and nxt < start + duration:
        return False

    return True


def next_free_slot(schedule: OrderedBSTMap, after: int,
                   duration: int) -> Optional[int]:
    """Return the earliest start time t >= `after` at which a meeting
    of `duration` minutes could be booked (inside office hours, no
    clash), or None if nothing fits before CLOSE.

    Don't try every minute. Jump from booking to booking instead:
      1. Start at t = max(after, OPEN).
      2. If the booking at floor_key(t) is still running at t, move t
         to the moment it ends.
      3. Look at nxt = ceiling_key(t). If there is no nxt, or the
         meeting would end by the time nxt starts, t is the answer (as
         long as t + duration <= CLOSE). Otherwise move t to the end of
         nxt and repeat step 3.
    """
    t = max(after, OPEN)

    prev = schedule.floor_key(t)
    if prev is not None:
        _, prev_duration = schedule[prev]
        t = max(t, prev + prev_duration)

    while t + duration <= CLOSE:
        nxt = schedule.ceiling_key(t)
        if nxt is None or t + duration <= nxt:
            return t
        _, nxt_duration = schedule[nxt]
        t = nxt + nxt_duration

    return None


# A fixed schedule everyone in the class uses, so results are comparable.
# Rows are listed in the order students signed up, which is NOT time
# order. Inserted in this order, the 12 bookings build a tree with the
# fewest levels 12 nodes can fit in. The "Load order" switch in the app
# can also insert the same rows sorted by time: watch what that does to
# the tree in Task 10.
SAMPLE_BOOKINGS = [
    # (start, name, minutes)
    ("14:30", "Frank Harris", 20),
    ("13:30", "Chloe Swift", 20),
    ("16:00", "Jack Bennett", 15),
    ("13:00", "Alice Copper", 15),
    ("13:50", "Daniel Lee", 10),
    ("15:15", "Henry Scott", 15),
    ("16:45", "Liam Foster", 15),
    ("13:15", "Ben Carter", 10),
    ("14:10", "Emma Wilson", 15),
    ("15:00", "Grace Turner", 10),
    ("15:40", "Ivy Parker", 20),
    ("16:30", "Kim Nguyen", 10),
]
