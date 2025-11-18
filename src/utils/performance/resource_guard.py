import os
import time
from collections import deque
from typing import Deque, Dict, Tuple, Optional

class RateLimiter:
    """Simple token bucket / sliding window hybrid.

    - Keeps timestamps of recent events in a deque.
    - Enforces max events per window_seconds.
    - Optional burst limit separate from sustained rate.
    """
    def __init__(self, window_seconds: int, max_events: int, burst: Optional[int] = None):
        self.window_seconds = window_seconds
        self.max_events = max_events
        self.burst = burst or max_events
        self.events: Deque[float] = deque()

    def allow(self) -> Tuple[bool, float]:
        now = time.time()
        # Drop outdated events
        cutoff = now - self.window_seconds
        while self.events and self.events[0] < cutoff:
            self.events.popleft()
        if len(self.events) >= self.max_events:
            retry_after = self.events[0] + self.window_seconds - now
            return False, max(retry_after, 0.0)
        # Burst guard (instantaneous)
        if len(self.events) >= self.burst:
            # Treat as soft limit; small retry
            return False, 1.0
        self.events.append(now)
        return True, 0.0

class ResourceGuard:
    """Shared registry of named rate limiters."""
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}

    def register(self, name: str, window_seconds: int, max_events: int, burst: Optional[int] = None):
        self.limiters[name] = RateLimiter(window_seconds, max_events, burst)

    def check(self, name: str) -> Tuple[bool, float]:
        limiter = self.limiters.get(name)
        if not limiter:
            return True, 0.0  # Unrestricted if not registered
        return limiter.allow()

# Global singleton (lightweight)
resource_guard = ResourceGuard()

# Default registrations (can be tuned via env or config later)
resource_guard.register("foodrepo_lookup", window_seconds=60, max_events=20, burst=5)
resource_guard.register("ipfs_add", window_seconds=60, max_events=30, burst=10)
resource_guard.register("bigchaindb_create", window_seconds=3600, max_events=10, burst=3)
# XRPL rate: read from env or default 10/hour
xrpl_rate = int(os.environ.get("XRPL_TX_RATE", "10"))
resource_guard.register("xrpl_tx", window_seconds=3600, max_events=xrpl_rate, burst=min(5, xrpl_rate))

__all__ = ["resource_guard"]
