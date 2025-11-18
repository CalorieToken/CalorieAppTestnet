"""
Debouncer utility for delaying execution until after rapid calls have stopped.
Useful for reducing redundant refresh operations.
"""
from kivy.clock import Clock
from typing import Callable, Dict


class Debouncer:
    """
    Debounces function calls by delaying execution until a quiet period.
    
    Usage:
        debouncer = Debouncer(delay=0.5)
        
        # Multiple rapid calls - only last one executes after 500ms
        debouncer.debounce('refresh', lambda dt: refresh_data())
        debouncer.debounce('refresh', lambda dt: refresh_data())
        debouncer.debounce('refresh', lambda dt: refresh_data())
    """
    
    def __init__(self, delay: float = 0.5):
        """
        Initialize debouncer with specified delay.
        
        Args:
            delay: Time in seconds to wait after last call before executing
        """
        self.delay = delay
        self._scheduled: Dict[str, Clock.ClockEvent] = {}
    
    def debounce(self, key: str, callback: Callable) -> None:
        """
        Schedule callback to run after delay, canceling any previous schedule for this key.
        
        Args:
            key: Unique identifier for this debounced operation
            callback: Function to call after delay (receives dt parameter from Clock)
        """
        # Cancel existing scheduled call for this key
        if key in self._scheduled:
            self._scheduled[key].cancel()
        
        # Schedule new call
        self._scheduled[key] = Clock.schedule_once(callback, self.delay)
    
    def cancel(self, key: str) -> None:
        """
        Cancel pending execution for a specific key.
        
        Args:
            key: Identifier of operation to cancel
        """
        if key in self._scheduled:
            self._scheduled[key].cancel()
            del self._scheduled[key]
    
    def cancel_all(self) -> None:
        """Cancel all pending executions."""
        for event in self._scheduled.values():
            event.cancel()
        self._scheduled.clear()
    
    def is_scheduled(self, key: str) -> bool:
        """
        Check if operation is currently scheduled.
        
        Args:
            key: Identifier to check
            
        Returns:
            True if operation is pending
        """
        return key in self._scheduled
