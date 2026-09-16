"""Linked structure implementation of a binary tree."""

from dsa.trees.base import BinaryTree, Tree
from typing import TypeVar, Optional

T = TypeVar('T')


class LinkedBinaryTree(BinaryTree[T]):
    """Binary tree implementation using a linked structure.

    Each node contains an element and references to parent, left child,
    and right child nodes.
    """

    class _Node:
        """Lightweight node class for storing tree elements."""
        __slots__ = '_element', '_parent', '_left', '_right'

        def __init__(self, element: T,
                     parent: Optional['LinkedBinaryTree._Node'] = None,
                     left: Optional['LinkedBinaryTree._Node'] = None,
                     right: Optional['LinkedBinaryTree._Node'] = None):
            self._element = element
            self._parent = parent
            self._left = left
            self._right = right

    class Position(Tree.Position):
        """An abstraction representing the location of a single element."""

        def __init__(self, container: 'LinkedBinaryTree', node: 'LinkedBinaryTree._Node'):
            """Constructor should not be invoked by user."""
            self._container = container
            self._node = node
            self._generation = container._generation

        def element(self) -> T:
            """Return the element stored at this position."""
            return self._node._element

        def __eq__(self, other: object) -> bool:
            """Return True if other represents the same position."""
            return (isinstance(other, type(self))
                    and self._container is other._container
                    and self._node is other._node
                    and self._generation == other._generation)

    def _validate(self, p: Tree.Position) -> _Node:
        """Return associated node if position is valid."""
        if not isinstance(p, self.Position):
            raise TypeError('p must be a Position of this tree')
        if p._container is not self:
            raise ValueError('p does not belong to this tree')
        if p._generation != self._generation or p._node._parent is p._node:
            raise ValueError('p is no longer valid')
        return p._node

    def _make_position(self, node: Optional[_Node]) -> Optional[Position]:
        """Return Position instance for given node (or None if no node)."""
        return self.Position(self, node) if node is not None else None

    def __init__(self):
        """Create an empty binary tree."""
        self._root = None
        self._size = 0
        self._generation = 0

    def __len__(self) -> int:
        return self._size

    def root(self) -> Optional[Position]:
        return self._make_position(self._root)

    def parent(self, p: Tree.Position) -> Optional[Position]:
        node = self._validate(p)
        return self._make_position(node._parent)

    def left(self, p: Tree.Position) -> Optional[Position]:
        node = self._validate(p)
        return self._make_position(node._left)

    def right(self, p: Tree.Position) -> Optional[Position]:
        node = self._validate(p)
        return self._make_position(node._right)

    def add_root(self, e: T) -> Position:
        """Place element e at the root of an empty tree and return new Position.

        Raises:
            ValueError: If tree is not empty.
        """
        if self._root is not None:
            raise ValueError('root already exists')
        self._root = self._Node(e)
        self._size = 1
        return self._make_position(self._root)

    def add_left(self, p: Tree.Position, e: T) -> Position:
        """Create a new left child for position p, storing element e.

        Returns:
            The Position of the new node.

        Raises:
            ValueError: If position p is invalid or already has a left child.
        """
        node = self._validate(p)
        if node._left is not None:
            raise ValueError('left child already exists')
        node._left = self._Node(e, parent=node)
        self._size += 1
        return self._make_position(node._left)

    def add_right(self, p: Tree.Position, e: T) -> Position:
        """Create a new right child for position p, storing element e.

        Returns:
            The Position of the new node.

        Raises:
            ValueError: If position p is invalid or already has a right child.
        """
        node = self._validate(p)
        if node._right is not None:
            raise ValueError('right child already exists')
        node._right = self._Node(e, parent=node)
        self._size += 1
        return self._make_position(node._right)

    def replace(self, p: Tree.Position, e: T) -> T:
        """Replace the element at position p with e and return old element.

        Args:
            p: A position in this tree.
            e: The new element to store.

        Returns:
            The element that was replaced.
        """
        node = self._validate(p)
        old_element = node._element
        node._element = e
        return old_element

    def delete(self, p: Tree.Position) -> T:
        """Delete the node at position p and replace it with its child, if any.

        Returns:
            The element that was stored at position p.

        Raises:
            ValueError: If position p is invalid or has two children.
        """
        node = self._validate(p)
        if node._left is not None and node._right is not None:
            raise ValueError('cannot delete a node with two children')

        child = node._left if node._left is not None else node._right
        if child is not None:
            child._parent = node._parent

        if node is self._root:
            self._root = child
        elif node is node._parent._left:
            node._parent._left = child
        else:
            node._parent._right = child

        self._size -= 1
        node._parent = node  # A deleted node cannot be used as a position again.
        node._left = None
        node._right = None
        return node._element

    def attach(self, p: Tree.Position, t1: 'LinkedBinaryTree', t2: 'LinkedBinaryTree') -> None:
        """Attach trees t1 and t2 as left and right subtrees of leaf p.

        Args:
            p: A leaf position in this tree.
            t1: A LinkedBinaryTree to attach as left subtree.
            t2: A LinkedBinaryTree to attach as right subtree.

        Raises:
            ValueError: If p is not a leaf.
            TypeError: If t1 or t2 is not a LinkedBinaryTree.
        """
        node = self._validate(p)
        if node._left is not None or node._right is not None:
            raise ValueError('p must be a leaf')
        if not isinstance(t1, LinkedBinaryTree) or not isinstance(t2, LinkedBinaryTree):
            raise TypeError('t1 and t2 must be LinkedBinaryTree instances')
        if t1 is self or t2 is self or t1 is t2:
            raise ValueError('attached trees must be distinct from each other and self')

        self._size += len(t1) + len(t2)
        if t1._root is not None:
            t1._root._parent = node
            node._left = t1._root
        if t2._root is not None:
            t2._root._parent = node
            node._right = t2._root

        for source in (t1, t2):
            source._root = None
            source._size = 0
            source._generation += 1  # Invalidate positions held by the source.
