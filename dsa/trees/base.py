"""Abstract base classes defining tree interfaces."""

from abc import ABC, abstractmethod
from collections import deque
from typing import TypeVar, Generic, Iterator, Optional

T = TypeVar('T')


class Tree(ABC, Generic[T]):
    """Abstract base class for a general tree structure.

    A tree is a hierarchical data structure where each node has at most
    one parent and zero or more children. The tree has a distinguished
    root node with no parent.

    This implementation uses a position-based interface where positions
    are opaque objects that represent nodes in the tree. Positions
    support element access but hide internal node structure.

    Core operations and their expected time complexities:
        root()              - Return root position           O(1)
        parent(p)           - Return parent of position p    O(1)
        children(p)         - Iterate over children of p     O(c_p)
        num_children(p)     - Return number of children      O(1) or O(c_p)
        is_root(p)          - Check if p is root            O(1)
        is_leaf(p)          - Check if p has no children    O(1)
        __len__()           - Return total number of nodes  O(1)
        __iter__()          - Iterate over all elements     O(n)

    where c_p is the number of children of position p and n is the
    total number of nodes.
    """

    class Position(ABC):
        """An abstraction representing the location of a single element.

        A position acts as a marker or token within the tree. It supports
        a single method, element(), which returns the element stored at
        that position.
        """

        @abstractmethod
        def element(self) -> T:
            """Return the element stored at this position."""
            pass

        @abstractmethod
        def __eq__(self, other: object) -> bool:
            """Return True if other represents the same position."""
            pass

        def __ne__(self, other: object) -> bool:
            """Return True if other does not represent the same position."""
            return not (self == other)

    @abstractmethod
    def root(self) -> Optional[Position]:
        """Return the root position of the tree (or None if empty).

        Returns:
            The root position, or None if the tree is empty.
        """
        pass

    @abstractmethod
    def parent(self, p: Position) -> Optional[Position]:
        """Return the position of p's parent (or None if p is root).

        Args:
            p: A position in this tree.

        Returns:
            The parent position, or None if p is the root.

        Raises:
            ValueError: If p is not a valid position for this tree.
        """
        pass

    @abstractmethod
    def children(self, p: Position) -> Iterator[Position]:
        """Generate an iteration of positions representing p's children.

        Args:
            p: A position in this tree.

        Yields:
            Positions of each child of p.

        Raises:
            ValueError: If p is not a valid position for this tree.
        """
        pass

    @abstractmethod
    def num_children(self, p: Position) -> int:
        """Return the number of children of position p.

        Args:
            p: A position in this tree.

        Returns:
            The number of children of p.

        Raises:
            ValueError: If p is not a valid position for this tree.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Return the total number of positions (nodes) in the tree."""
        pass

    def is_root(self, p: Position) -> bool:
        """Return True if position p is the root of the tree.

        Args:
            p: A position in this tree.
        """
        return self.root() == p

    def is_leaf(self, p: Position) -> bool:
        """Return True if position p has no children.

        Args:
            p: A position in this tree.
        """
        return self.num_children(p) == 0

    def is_empty(self) -> bool:
        """Return True if the tree contains no positions."""
        return len(self) == 0

    def depth(self, p: Position) -> int:
        """Return the depth of position p (number of ancestors).

        The depth of the root is 0.

        Args:
            p: A position in this tree.

        Returns:
            The number of ancestors of p.
        """
        if self.is_root(p):
            return 0
        else:
            return 1 + self.depth(self.parent(p))

    def height(self, p: Optional[Position] = None) -> int:
        """Return the height of the subtree rooted at position p.

        If p is None, return the height of the entire tree.
        The height of a leaf is 0. The height of an empty tree is -1.

        Args:
            p: A position in this tree, or None for the root.

        Returns:
            The height of the subtree rooted at p.
        """
        if p is None:
            p = self.root()
            if p is None:
                return -1
        return 1 + max((self.height(c) for c in self.children(p)), default=-1)


    def __iter__(self) -> Iterator[T]:
        """Generate an iteration of the tree's elements.

        Default implementation performs a preorder traversal.
        """
        for p in self.preorder():
            yield p.element()

    def preorder(self) -> Iterator[Position]:
        """Generate a preorder iteration of positions in the tree."""
        if not self.is_empty():
            yield from self._subtree_preorder(self.root())

    def _subtree_preorder(self, p: Position) -> Iterator[Position]:
        """Generate a preorder iteration of positions in subtree rooted at p."""
        yield p
        for c in self.children(p):
            yield from self._subtree_preorder(c)

    def postorder(self) -> Iterator[Position]:
        """Generate a postorder iteration of positions in the tree."""
        if not self.is_empty():
            yield from self._subtree_postorder(self.root())

    def _subtree_postorder(self, p: Position) -> Iterator[Position]:
        """Generate positions in the subtree rooted at p in postorder."""
        for c in self.children(p):
            yield from self._subtree_postorder(c)
        yield p

    def levelorder(self) -> Iterator[Position]:
        """Generate a breadth-first (level-order) iteration of positions.

        Visits all nodes at depth 0 (root), then depth 1, then depth 2, etc.
        Uses a queue to track nodes to visit.
        """
        if not self.is_empty():
            pending = deque([self.root()])
            while pending:
                p = pending.popleft()
                yield p
                pending.extend(self.children(p))



class BinaryTree(Tree[T]):
    """Abstract base class for a binary tree structure.

    A binary tree is a tree where each node has at most two children,
    distinguished as left and right children.

    Additional operations beyond Tree:
        left(p)     - Return left child of p     O(1)
        right(p)    - Return right child of p    O(1)
        sibling(p)  - Return sibling of p        O(1)
    """

    @abstractmethod
    def left(self, p: Tree.Position) -> Optional[Tree.Position]:
        """Return the position of p's left child (or None if no left child).

        Args:
            p: A position in this tree.

        Returns:
            The left child position, or None if no left child.

        Raises:
            ValueError: If p is not a valid position for this tree.
        """
        pass

    @abstractmethod
    def right(self, p: Tree.Position) -> Optional[Tree.Position]:
        """Return the position of p's right child (or None if no right child).

        Args:
            p: A position in this tree.

        Returns:
            The right child position, or None if no right child.

        Raises:
            ValueError: If p is not a valid position for this tree.
        """
        pass

    def sibling(self, p: Tree.Position) -> Optional[Tree.Position]:
        """Return the position of p's sibling (or None if no sibling).

        Args:
            p: A position in this tree.

        Returns:
            The sibling position, or None if p has no sibling.
        """
        parent = self.parent(p)
        if parent is None:
            return None
        if p == self.left(parent):
            return self.right(parent)
        else:
            return self.left(parent)

    def children(self, p: Tree.Position) -> Iterator[Tree.Position]:
        """Generate an iteration of positions representing p's children.

        For a binary tree, yields left child (if any) then right child (if any).
        """
        if self.left(p) is not None:
            yield self.left(p)
        if self.right(p) is not None:
            yield self.right(p)

    def num_children(self, p: Tree.Position) -> int:
        """Return the number of children of position p."""
        count = 0
        if self.left(p) is not None:
            count += 1
        if self.right(p) is not None:
            count += 1
        return count


    def __iter__(self) -> Iterator[T]:
        """Generate an iteration of the tree's elements.

        Default implementation performs an inorder traversal.
        """
        for p in self.inorder():
            yield p.element()


    def inorder(self) -> Iterator[Tree.Position]:
        """Generate an inorder iteration of positions in the tree."""
        if not self.is_empty():
            yield from self._subtree_inorder(self.root())

    def _subtree_inorder(self, p: Tree.Position) -> Iterator[Tree.Position]:
        """Generate positions in the subtree rooted at p in inorder."""
        left = self.left(p)
        if left is not None:
            yield from self._subtree_inorder(left)
        yield p
        right = self.right(p)
        if right is not None:
            yield from self._subtree_inorder(right)

