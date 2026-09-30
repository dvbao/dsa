"""Grading tests for traversal helpers (6 basic + 4 special)."""

from contextlib import contextmanager
import signal
import threading
import time

from dsa.trees.linked_binary_tree import LinkedBinaryTree
from dsa.trees import traversals


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


def _sample_tree():
    """Build a five-node tree using only the public tree interface."""
    tree = LinkedBinaryTree()
    root = tree.add_root(1)
    left = tree.add_left(root, 2)
    tree.add_right(root, 3)
    tree.add_left(left, 4)
    tree.add_right(left, 5)
    return tree


def _all_orders(tree):
    return (
        list(traversals.preorder(tree)),
        list(traversals.inorder(tree)),
        list(traversals.postorder(tree)),
        list(traversals.levelorder(tree)),
    )


class TestTraversalsGrade:
    # Six basic cases
    def test_all_traversals_of_empty_tree_are_empty(self):
        assert _all_orders(LinkedBinaryTree()) == ([], [], [], [])

    def test_all_traversals_of_single_node_match(self):
        tree = LinkedBinaryTree()
        tree.add_root("only")

        assert _all_orders(tree) == (
            ["only"],
            ["only"],
            ["only"],
            ["only"],
        )

    def test_preorder_visits_root_before_subtrees(self):
        assert list(traversals.preorder(_sample_tree())) == [1, 2, 4, 5, 3]

    def test_inorder_visits_left_root_right(self):
        assert list(traversals.inorder(_sample_tree())) == [4, 2, 5, 1, 3]

    def test_postorder_visits_root_after_subtrees(self):
        assert list(traversals.postorder(_sample_tree())) == [4, 5, 2, 3, 1]

    def test_levelorder_visits_one_depth_at_a_time(self):
        assert list(traversals.levelorder(_sample_tree())) == [1, 2, 3, 4, 5]

    # Four special cases
    def test_special_sparse_irregular_tree_has_exact_orders(self):
        tree = LinkedBinaryTree()
        root = tree.add_root("a")
        left = tree.add_left(root, "b")
        right = tree.add_right(root, "c")
        tree.add_right(left, "d")
        right_left = tree.add_left(right, "e")
        tree.add_left(right_left, "f")

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            orders = _all_orders(tree)

        assert orders == (
            ["a", "b", "d", "c", "e", "f"],
            ["b", "d", "a", "f", "e", "c"],
            ["d", "b", "f", "e", "c", "a"],
            ["a", "b", "c", "d", "e", "f"],
        )

    def test_special_duplicate_none_and_object_values_are_preserved(self):
        marker = object()
        tree = LinkedBinaryTree()
        root = tree.add_root(None)
        tree.add_left(root, marker)
        tree.add_right(root, marker)

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            preorder = list(traversals.preorder(tree))
            inorder = list(traversals.inorder(tree))

        assert preorder[0] is None
        assert preorder[1] is marker and preorder[2] is marker
        assert inorder[0] is marker and inorder[1] is None and inorder[2] is marker

    def test_special_deep_one_sided_tree_traverses_all_nodes(self):
        node_count = 700
        tree = LinkedBinaryTree()
        position = tree.add_root(0)
        for value in range(1, node_count):
            position = tree.add_right(position, value)

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            orders = _all_orders(tree)

        ascending = list(range(node_count))
        assert orders[0] == ascending
        assert orders[1] == ascending
        assert orders[2] == list(reversed(ascending))
        assert orders[3] == ascending

    def test_special_large_complete_tree_traverses_in_linear_time(self):
        node_count = 32_767
        tree = LinkedBinaryTree()
        positions = [tree.add_root(0)]
        next_value = 1
        parent_index = 0
        while next_value < node_count:
            parent = positions[parent_index]
            positions.append(tree.add_left(parent, next_value))
            next_value += 1
            positions.append(tree.add_right(parent, next_value))
            next_value += 1
            parent_index += 1

        with _time_limit(SPECIAL_TIMEOUT_SECONDS):
            orders = _all_orders(tree)

        expected_values = set(range(node_count))
        assert orders[3] == list(range(node_count))
        for order in orders:
            assert len(order) == node_count
            assert set(order) == expected_values
