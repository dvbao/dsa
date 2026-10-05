"""Binary search tree implementation of a map."""

from dsa.maps.base import Map
from typing import TypeVar, Iterator, Optional

K = TypeVar('K')
V = TypeVar('V')


class BSTMap(Map[K, V]):
    """Map implementation using an unbalanced binary search tree.

    Each node contains a key-value pair. The BST property ensures that
    for each node, all keys in the left subtree are less than the node's
    key, and all keys in the right subtree are greater.

    Note: This unbalanced implementation has O(n) worst-case time complexity
    for all operations when the tree becomes degenerate (e.g., inserting
    sorted keys). See RBTreeMap for a balanced alternative.
    """

    class _Node:
        """A node in the binary search tree."""
        __slots__ = '_key', '_value', '_left', '_right', '_parent'

        def __init__(self, key: K, value: V,
                     parent: Optional['BSTMap._Node'] = None):
            self._key = key
            self._value = value
            self._left: Optional['BSTMap._Node'] = None
            self._right: Optional['BSTMap._Node'] = None
            self._parent = parent

    def __init__(self):
        """Create an empty BST map."""
        self._root: Optional[BSTMap._Node] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, key: K) -> V:
        node = self._search(key, self._root)
        if node is None:
            raise KeyError(key)
        return node._value

    def __setitem__(self, key: K, value: V) -> None:
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
                if node._left is not None:
                    node = node._left
                else:
                    node._left = self._Node(key, value, parent=node)
                    self._size += 1
                    return
            else:
                if node._right is not None:
                    node = node._right
                else:
                    node._right = self._Node(key, value, parent=node)
                    self._size += 1
                    return

    def __delitem__(self, key: K) -> None:
        node = self._search(key, self._root)
        if node is None:
            raise KeyError(key)

        # If node has two children, copy its in-order successor into node.
        # The successor cannot have a left child, so it is then easy to remove.
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

    def __contains__(self, key: K) -> bool:
        return self._search(key, self._root) is not None

    def __iter__(self) -> Iterator[K]:
        stack = []
        node = self._root

        # Iterative in-order traversal avoids recursion depth failures for a
        # degenerate tree created by inserting already-sorted keys.
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node._left
            node = stack.pop()
            yield node._key
            node = node._right

    def _search(self, key: K, node: Optional[_Node]) -> Optional[_Node]:
        """Search for a node with the given key starting from node.

        Returns the node if found, or None if not found.
        """
        while node is not None:
            if key == node._key:
                return node
            if key < node._key:
                node = node._left
            else:
                node = node._right
        return None

    def _subtree_min(self, node: _Node) -> _Node:
        """Return the node with minimum key in subtree rooted at node."""
        while node._left is not None:
            node = node._left
        return node

    def _subtree_max(self, node: _Node) -> _Node:
        """Return the node with maximum key in subtree rooted at node."""
        while node._right is not None:
            node = node._right
        return node
