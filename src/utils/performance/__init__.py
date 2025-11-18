"""Performance utilities package

Aggregates both lightweight helpers (debouncer, rate limiter, caches) and
the extended optimization decorators defined in the sibling module
`src.utils.performance.py` so import sites can uniformly use:

    from src.utils.performance import debounce, async_operation

without worrying about the package/file name collision.
"""
from .data_cache import DataCache
from .debouncer import Debouncer
from .resource_guard import RateLimiter, ResourceGuard

# Import extended optimization helpers from parent-level performance.py
try:
    from ..performance import (
        debounce,
        async_operation,
        lazy_property,
        throttle,
        PerformanceOptimizer,
        WidgetPool,
        ScreenPreloader,
    )
except Exception as e:  # Fail gracefully; core features still available
    # Minimal fallbacks (no-op decorators) to avoid import crashes
    def _noop_decorator(*d_args, **d_kwargs):
        def _inner(func):
            return func
        return _inner
    debounce = async_operation = lazy_property = throttle = _noop_decorator
    PerformanceOptimizer = WidgetPool = ScreenPreloader = None  # type: ignore

__all__ = [
    'DataCache',
    'Debouncer',
    'RateLimiter',
    'ResourceGuard',
    'debounce',
    'async_operation',
    'lazy_property',
    'throttle',
    'PerformanceOptimizer',
    'WidgetPool',
    'ScreenPreloader',
]
