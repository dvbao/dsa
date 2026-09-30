"""Grading tests for ``LinkedBinaryTree`` (6 basic + 4 special)."""

from contextlib import contextmanager
import signal
import threading
import time

import pytest

from dsa.trees.linked_binary_tree import LinkedBinaryTree


SPECIAL_TIMEOUT_SECONDS = 3.0


@contextmanager
def _time_limit(seconds: float):
    """Limit one special case without relying on a shared conftest file."""
    start = time.perf_counter()
    can_interrupt = (
        hasattr(signal, "setitimer")
        and threading.current_thread() is threading.main_thread()
    )
    if can_interrupt:
        previous_handler = signal.getsignal(signal.SIGALRM)

        def handle_timeout(_signum, _frame):
            raise AssertionError(f"test exceeded the {seconds:.2f}s time limit")

        signal.signal(signal.SIGALRM, handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        if can_interrupt:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_handler)
        elapsed = time.perf_counter() - start
        assert elapsed < seconds, (
            f"test took {elapsed:.3f}s; limit is {seconds:.2f}s"
        )


class TestLinkedBinaryTreeGrade:
    # Six basic cases
    def test_new_tree_is_empty(self):
        tree = LinkedBinaryTree()

        assert tree.is_empty()
        assert len(tree) == 0
        assert tree.root() is None

    def test_add_root_exposes_its_element(self):
        tree = LinkedBinaryTree()
        root = tree.add_root("root")

        assert len(tree) == 1
        assert tree.root() == root
        assert root.element() == "root"
        assert tree.is_root(root)

    def test_children_parent_and_sibling_relationships(self):
        tree = LinkedBinaryTree()
        root = tree.add_root(1)
        left = tree.add_left(root, 2)
        right = tree.add_right(root, 3)

        assert tree.left(root) == left
        assert tree.right(root) == right
        assert tree.parent(left) == root
        assert tree.parent(right) == root
        assert tree.sibling(left) == right
        assert tree.sibling(right) == left
        assert list(tree.children(root)) == [left, right]

    def test_rejects_duplicate_root_and_child_positions(self):
        tree = LinkedBinaryTree()
        root = tree.add_root(1)
        tree.add_left(root, 2)
        tree.add_right(root, 3)

        with pytest.raises(ValueError):
            tree.add_root(4)
        with pytest.raises(ValueError):
            tree.add_left(root, 4)
        with pytest.raises(ValueError):
            tree.add_right(root, 4)

        assert len(tree) == 3

    def test_replace_returns_old_element_and_keeps_position(self):
        tree = LinkedBinaryTree()
        root = tree.add_root("old")

        assert tree.replace(root, "new") == "old"
        assert root.element() == "new"
        assert tree.root() == root
        assert len(tree) == 1

    def test_delete_leaf_and_node_with_one_child(self):
        tree = LinkedBinaryTree()
        root = tree.add_root(1)
        left = tree.add_left(root, 2)
        grandchild = tree.add_right(left, 3)
        leaf = tree.add_right(root, 4)

        assert tree.delete(leaf) == 4
        assert tree.right(root) is None
        assert tree.delete(left) == 2
        assert tree.left(root) == grandchild
        assert tree.parent(grandchild) == root
        assert len(tree) == 2

    # Four special cases
    def test_special_failed_two_child_delete_preserves_tree(self):
        tree = LinkedBinaryTree()
        root = tree.add_root(1)
        left = tree.add_left(root, 2)
        right = tree.add_right(root, 3)

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            with pytest.raises(ValueError):
                tree.delete(root)

        assert len(tree) == 3
        assert tree.left(root) == left
        assert tree.right(root) == right

    def test_special_rejects_foreign_and_deleted_positions(self):
        first = LinkedBinaryTree()
        first_root = first.add_root("first")
        deleted = first.add_left(first_root, "deleted")
        second = LinkedBinaryTree()
        foreign = second.add_root("second")

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            with pytest.raises(ValueError):
                first.add_left(foreign, "invalid")
            assert first.delete(deleted) == "deleted"
            with pytest.raises(ValueError):
                first.parent(deleted)

        assert len(first) == 1
        assert len(second) == 1

    def test_special_attach_transfers_subtrees_and_invalidates_sources(self):
        destination = LinkedBinaryTree()
        destination_root = destination.add_root("destination")

        left_tree = LinkedBinaryTree()
        left_root = left_tree.add_root("left")
        left_child = left_tree.add_right(left_root, "left-child")

        right_tree = LinkedBinaryTree()
        right_root = right_tree.add_root("right")
        right_tree.add_left(right_root, "right-child")

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            destination.attach(destination_root, left_tree, right_tree)

        assert len(destination) == 5
        attached_left = destination.left(destination_root)
        attached_right = destination.right(destination_root)
        attached_left_child = destination.right(attached_left)
        assert attached_left.element() == "left"
        assert attached_right.element() == "right"
        assert attached_left_child.element() == "left-child"
        assert destination.parent(attached_left_child) == attached_left
        assert left_tree.is_empty()
        assert right_tree.is_empty()
        with pytest.raises(ValueError):
            left_tree.parent(left_root)
        with pytest.raises(ValueError):
            left_tree.parent(left_child)

    def test_special_large_complete_tree_keeps_public_invariants(self):
        node_count = 32_767
        tree = LinkedBinaryTree()
        positions = [tree.add_root(0)]

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            next_value = 1
            parent_index = 0
            while next_value < node_count:
                parent = positions[parent_index]
                positions.append(tree.add_left(parent, next_value))
                next_value += 1
                if next_value < node_count:
                    positions.append(tree.add_right(parent, next_value))
                    next_value += 1
                parent_index += 1

            levelorder_values = [p.element() for p in tree.levelorder()]

        assert len(tree) == node_count
        assert levelorder_values == list(range(node_count))
        assert tree.height() == 14
