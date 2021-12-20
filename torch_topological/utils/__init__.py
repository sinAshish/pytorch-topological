"""Utilities module."""

from .general import is_iterable

from .point_clouds import make_disk
from .point_clouds import make_uniform_blob

from .summary_statistics import total_persistence
from .summary_statistics import persistent_entropy
from .summary_statistics import polynomial_function


__all__ = [
    'is_iterable',
    'make_disk',
    'make_uniform_blob',
    'persistent_entropy',
    'polynomial_function',
    'total_persistence'
]