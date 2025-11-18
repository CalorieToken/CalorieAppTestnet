"""
Simple time-based data cache for reducing redundant network calls.
"""
import time
from typing import Any, Optional


class DataCache:
    """
    Time-to-live (TTL) based cache for storing API responses and expensive computations.
    
    Usage:
        cache = DataCache(ttl_seconds=30)
        
        # Try to get from cache
        data = cache.get('account_balance')
        if data is None:
            # Fetch from network
            data = fetch_account_balance()
            cache.set('account_balance', data)
    """
    
    def __init__(self, ttl_seconds: int = 30):
        """
        Initialize cache with specified time-to-live.
        
        Args:
            ttl_seconds: How long cached values remain valid
        """
        self._cache = {}
        self._timestamps = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache if it exists and hasn't expired.
        
        Args:
            key: Cache key to lookup
            
        Returns:
            Cached value if found and fresh, None otherwise
        """
        if key in self._cache:
            age = time.time() - self._timestamps[key]
            if age < self.ttl:
                return self._cache[key]
            else:
                # Expired - clean up
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Store value in cache with current timestamp.
        
        Args:
            key: Cache key
            value: Data to cache
        """
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def invalidate(self, key: str) -> None:
        """
        Remove specific key from cache.
        
        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._timestamps.clear()
    
    def contains(self, key: str) -> bool:
        """
        Check if key exists in cache and is still valid.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists and hasn't expired
        """
        return self.get(key) is not None
