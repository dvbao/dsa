"""Public interface for the search package.

Do not modify this file. Each algorithm is implemented in its own module.
"""

from dsa.search.binary_search import binary_search
from dsa.search.binary_search_recursive import binary_search_recursive
from dsa.search.bisect_left import bisect_left
from dsa.search.bisect_right import bisect_right

__all__ = [
    'binary_search',
    'binary_search_recursive',
    'bisect_left',
    'bisect_right',
]
