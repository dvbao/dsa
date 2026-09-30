"""Hash table implementation of a map."""

from dsa.maps.base import Map
from typing import TypeVar, Iterator, List, Tuple

K = TypeVar('K')
V = TypeVar('V')


class HashMap(Map[K, V]):
    """Map implementation using a hash table with separate chaining.

    Uses an array of buckets where each bucket holds entries that hash
    to the same index. Collisions are resolved by chaining entries in
    a list within each bucket.

    Load factor is maintained below a threshold by resizing the table
    when necessary.
    """

    DEFAULT_CAPACITY = 11
    LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        """Create an empty hash map.

        Args:
            capacity: Initial number of buckets. Defaults to 11.
        """
        if not isinstance(capacity, int):
            raise TypeError('capacity must be an integer')
        if capacity <= 0:
            raise ValueError('capacity must be positive')

        self._table: List[List[Tuple[K, V]]] = [
            [] for _ in range(capacity)
        ]
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, key: K) -> V:
        bucket = self._table[self._hash(key)]
        for stored_key, stored_value in bucket:
            if stored_key == key:
                return stored_value
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        bucket = self._table[self._hash(key)]

        for index, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket[index] = (key, value)
                return

        bucket.append((key, value))
        self._size += 1

        if self._size / len(self._table) > self.LOAD_FACTOR_THRESHOLD:
            self._resize(2 * len(self._table) + 1)

    def __delitem__(self, key: K) -> None:
        bucket = self._table[self._hash(key)]
        for index, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket.pop(index)
                self._size -= 1
                return
        raise KeyError(key)

    def __contains__(self, key: K) -> bool:
        bucket = self._table[self._hash(key)]
        return any(stored_key == key for stored_key, _ in bucket)

    def __iter__(self) -> Iterator[K]:
        for bucket in self._table:
            for key, _ in bucket:
                yield key

    def _hash(self, key: K) -> int:
        """Compute the bucket index for the given key."""
        return hash(key) % len(self._table)

    def _resize(self, new_capacity: int) -> None:
        """Resize the hash table to the given capacity."""
        if new_capacity <= 0:
            raise ValueError('new capacity must be positive')

        old_table = self._table
        self._table = [[] for _ in range(new_capacity)]

        for bucket in old_table:
            for key, value in bucket:
                new_bucket = self._table[self._hash(key)]
                new_bucket.append((key, value))
