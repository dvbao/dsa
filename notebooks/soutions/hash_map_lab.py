"""Reference solution for the HashMap Roster Lab (instructor use only).

Same class signatures students see in notebooks/hash_map_roster_lab.ipynb,
Part 1 (`HashMap`, separate chaining) and Part 2 (`LinearProbingMap`,
linear probing), with every method filled in.

Grading workflow: to check a specific student's submission, copy their
`HashMap` and/or `LinearProbingMap` class from their notebook into a copy
of this file, keeping the filename `hash_map_lab.py`, then run:

    pytest test_hash_map_lab.py

against it from this folder.
"""

from typing import TypeVar, Generic, Iterator, List, Tuple

K = TypeVar('K')
V = TypeVar('V')


class HashMap(Generic[K, V]):
    """A hash table map using separate chaining for collision resolution.

    Stores key-value pairs in an array of buckets. Each bucket is a list
    of (key, value) tuples; every entry whose key hashes to the same
    bucket index is chained together in that bucket's list.
    """

    DEFAULT_CAPACITY = 11
    LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        """Create an empty hash map with `capacity` buckets."""
        self._table: List[List[Tuple[K, V]]] = [[] for _ in range(capacity)]
        self._size = 0

    def __len__(self) -> int:
        """Return the number of key-value pairs stored (self._size)."""
        return self._size

    def __getitem__(self, key: K) -> V:
        """Return the value associated with `key`.

        Raises:
            KeyError: if `key` is not present.
        """
        bucket = self._table[self._hash(key)]
        for stored_key, stored_value in bucket:
            if stored_key == key:
                return stored_value
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        """Associate `value` with `key`, overwriting any existing value
        for that key.

        If adding this entry pushes the load factor (size / capacity)
        above LOAD_FACTOR_THRESHOLD, resize the table (see `_resize`).
        """
        bucket = self._table[self._hash(key)]

        for i, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self._size += 1

        if self._size / len(self._table) > self.LOAD_FACTOR_THRESHOLD:
            self._resize(2 * len(self._table) + 1)

    def __delitem__(self, key: K) -> None:
        """Remove `key` and its associated value.

        Raises:
            KeyError: if `key` is not present.
        """
        bucket = self._table[self._hash(key)]
        for i, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket.pop(i)
                self._size -= 1
                return
        raise KeyError(key)

    def __contains__(self, key: K) -> bool:
        """Return True if `key` is currently stored."""
        bucket = self._table[self._hash(key)]
        return any(stored_key == key for stored_key, _ in bucket)

    def __iter__(self) -> Iterator[K]:
        """Yield every key currently stored, in any order."""
        for bucket in self._table:
            for stored_key, _ in bucket:
                yield stored_key

    def _hash(self, key: K) -> int:
        """Map `key` to a bucket index in range [0, capacity)."""
        return hash(key) % len(self._table)

    def _resize(self, new_capacity: int) -> None:
        """Rebuild the table with `new_capacity` buckets, re-hashing
        every existing entry into its new bucket."""
        old_table = self._table
        self._table = [[] for _ in range(new_capacity)]
        for bucket in old_table:
            for stored_key, stored_value in bucket:
                new_bucket = self._table[self._hash(stored_key)]
                new_bucket.append((stored_key, stored_value))

    def is_empty(self) -> bool:
        """Return True if the map contains no key-value pairs."""
        return len(self) == 0


class _AvailableMarker:
    """Sentinel for a slot that held an entry which was later deleted."""

    def __repr__(self):
        return "AVAILABLE"


AVAILABLE = _AvailableMarker()


class LinearProbingMap(Generic[K, V]):
    """A hash table map using open addressing with linear probing.

    Every slot in self._table is one of:
      * None, never used (a true empty slot)
      * AVAILABLE, held an entry that was later deleted (a "tombstone")
      * (key, value), currently occupied

    When a slot is taken, probing moves to the next slot (index + 1,
    wrapping around with % capacity) until an open one is found.
    """

    DEFAULT_CAPACITY = 11
    LOAD_FACTOR_THRESHOLD = 0.5

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        """Create an empty table with `capacity` slots, every slot None."""
        self._table = [None] * capacity
        self._size = 0

    def __len__(self) -> int:
        """Return the number of key-value pairs stored (self._size)."""
        return self._size

    def __getitem__(self, key: K) -> V:
        """Return the value associated with `key`.

        Raises:
            KeyError: if `key` is not found.
        """
        capacity = len(self._table)
        start = self._hash(key)
        for offset in range(capacity):
            i = (start + offset) % capacity
            slot = self._table[i]
            if slot is None:
                raise KeyError(key)
            if slot is AVAILABLE:
                continue
            stored_key, stored_value = slot
            if stored_key == key:
                return stored_value
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        """Associate `value` with `key`, overwriting any existing value
        for that key.

        Probes from `_hash(key)`; inserts into the first open slot
        (None or AVAILABLE) found along the way if `key` isn't already
        stored. Resizes if the new load factor exceeds the threshold.
        """
        capacity = len(self._table)
        start = self._hash(key)
        first_open = None
        for offset in range(capacity):
            i = (start + offset) % capacity
            slot = self._table[i]
            if slot is None:
                target = first_open if first_open is not None else i
                self._table[target] = (key, value)
                self._size += 1
                if self._size / capacity > self.LOAD_FACTOR_THRESHOLD:
                    self._resize(2 * capacity + 1)
                return
            if slot is AVAILABLE:
                if first_open is None:
                    first_open = i
                continue
            stored_key, _ = slot
            if stored_key == key:
                self._table[i] = (key, value)
                return
        raise RuntimeError("table is full, this should be unreachable "
                           "once resizing is implemented correctly")

    def __delitem__(self, key: K) -> None:
        """Remove `key` and its associated value, leaving an AVAILABLE
        tombstone behind instead of None.

        Raises:
            KeyError: if `key` is not found.
        """
        capacity = len(self._table)
        start = self._hash(key)
        for offset in range(capacity):
            i = (start + offset) % capacity
            slot = self._table[i]
            if slot is None:
                raise KeyError(key)
            if slot is AVAILABLE:
                continue
            stored_key, _ = slot
            if stored_key == key:
                self._table[i] = AVAILABLE
                self._size -= 1
                return
        raise KeyError(key)

    def __contains__(self, key: K) -> bool:
        """Return True if `key` is currently stored."""
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __iter__(self) -> Iterator[K]:
        """Yield every key currently stored (every OCCUPIED slot), in
        any order."""
        for slot in self._table:
            if slot is not None and slot is not AVAILABLE:
                yield slot[0]

    def _hash(self, key: K) -> int:
        """Map `key` to a starting slot index in range [0, capacity)."""
        return hash(key) % len(self._table)

    def _resize(self, new_capacity: int) -> None:
        """Rebuild the table with `new_capacity` slots, re-inserting
        every currently OCCUPIED entry. Old AVAILABLE tombstones are
        dropped for good in the process."""
        old_table = self._table
        self._table = [None] * new_capacity
        self._size = 0
        for slot in old_table:
            if slot is not None and slot is not AVAILABLE:
                stored_key, stored_value = slot
                self[stored_key] = stored_value

    def is_empty(self) -> bool:
        """Return True if the map contains no key-value pairs."""
        return len(self) == 0
