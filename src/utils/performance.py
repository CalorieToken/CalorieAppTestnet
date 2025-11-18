"""
Performance Optimization Module
Implements caching, debouncing, and async operations to improve app responsiveness
"""
from functools import wraps
from kivy.clock import Clock
import threading
import time


class PerformanceOptimizer:
    """Centralized performance optimization utilities"""
    
    _screen_cache = {}
    _widget_cache = {}
    _last_click_time = {}
    
    @staticmethod
    def cache_screen(screen_name, screen_instance):
        """Cache a screen instance for faster access"""
        PerformanceOptimizer._screen_cache[screen_name] = {
            'instance': screen_instance,
            'cached_at': time.time()
        }
    
    @staticmethod
    def get_cached_screen(screen_name):
        """Retrieve cached screen if available"""
        cache_entry = PerformanceOptimizer._screen_cache.get(screen_name)
        if cache_entry:
            return cache_entry['instance']
        return None
    
    @staticmethod
    def cache_widget(widget_id, widget_instance):
        """Cache a widget reference"""
        PerformanceOptimizer._widget_cache[widget_id] = widget_instance
    
    @staticmethod
    def get_cached_widget(widget_id):
        """Retrieve cached widget"""
        return PerformanceOptimizer._widget_cache.get(widget_id)
    
    @staticmethod
    def clear_cache():
        """Clear all caches"""
        PerformanceOptimizer._screen_cache.clear()
        PerformanceOptimizer._widget_cache.clear()
        PerformanceOptimizer._last_click_time.clear()


def debounce(delay=0.3, leading=True, trailing=False):
    """Debounce decorator to prevent rapid repeated calls.

    Parameters:
        delay (float): Minimum seconds between executions.
        leading (bool): If True, execute immediately on first call.
        trailing (bool): If True and a call was suppressed, schedule one final execution.

    Notes:
        Existing usages that pass only `delay` retain prior behavior (leading execution).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func_id = f"{self.__class__.__name__}.{func.__name__}"
            current_time = time.time()
            last_time = PerformanceOptimizer._last_click_time.get(func_id)

            # First call scenario
            if last_time is None:
                PerformanceOptimizer._last_click_time[func_id] = current_time
                if leading:
                    return func(self, *args, **kwargs)
                # If not leading, schedule trailing execution after delay
                if trailing:
                    Clock.schedule_once(lambda dt: func(self, *args, **kwargs), delay)
                return None

            # Subsequent calls within delay window
            if current_time - last_time < delay:
                if trailing:
                    # Cancel any previously scheduled trailing call by overwriting
                    Clock.schedule_once(lambda dt: func(self, *args, **kwargs), delay - (current_time - last_time))
                return None

            # Outside delay window - execute now
            PerformanceOptimizer._last_click_time[func_id] = current_time
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def async_operation(callback=None):
    """
    Run operation in background thread, optionally call callback on main thread when done
    
    Usage:
        @async_operation(callback='on_data_loaded')
        def load_data(self):
            # Heavy operation here
            return result
        
        def on_data_loaded(self, result):
            # Update UI with result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            def run_async():
                try:
                    result = func(self, *args, **kwargs)
                    if callback and hasattr(self, callback):
                        Clock.schedule_once(lambda dt: getattr(self, callback)(result), 0)
                except Exception as e:
                    print(f"Async operation error in {func.__name__}: {e}")
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            return thread
        return wrapper
    return decorator


def lazy_property(func):
    """
    Lazy property decorator - computes value once and caches it
    
    Usage:
        @lazy_property
        def expensive_widget(self):
            return self.create_complex_widget()
    """
    attr_name = f'_lazy_{func.__name__}'
    
    @wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    
    return property(wrapper)


def throttle(interval=0.1):
    """
    Throttle decorator - ensures function is not called more than once per interval
    
    Usage:
        @throttle(interval=0.5)
        def on_scroll(self, *args):
            # Update UI based on scroll
    """
    def decorator(func):
        last_called = [0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_called[0] >= interval:
                last_called[0] = current_time
                return func(*args, **kwargs)
        return wrapper
    return decorator


class WidgetPool:
    """
    Widget pooling for better performance with dynamic lists
    """
    def __init__(self, widget_class, initial_size=10):
        self.widget_class = widget_class
        self.pool = []
        self.active = []
        
        # Pre-create widgets
        for _ in range(initial_size):
            self.pool.append(widget_class())
    
    def acquire(self):
        """Get a widget from the pool"""
        if self.pool:
            widget = self.pool.pop()
        else:
            widget = self.widget_class()
        
        self.active.append(widget)
        return widget
    
    def release(self, widget):
        """Return widget to pool"""
        if widget in self.active:
            self.active.remove(widget)
            self.pool.append(widget)
            # Reset widget state
            if hasattr(widget, 'reset'):
                widget.reset()
    
    def release_all(self):
        """Return all active widgets to pool"""
        while self.active:
            self.release(self.active[0])


# Screen pre-loading helper
class ScreenPreloader:
    """Pre-load and cache frequently accessed screens"""
    
    def __init__(self, app):
        self.app = app
        self.preload_screens = [
            'wallet_screen',
            'settings_screen',
            'sendxrp_screen'
        ]
    
    def preload(self):
        """Pre-load all configured screens"""
        for screen_name in self.preload_screens:
            try:
                screen = self.app.manager.get_screen(screen_name)
                PerformanceOptimizer.cache_screen(screen_name, screen)
                # Trigger on_pre_enter to initialize widgets
                if hasattr(screen, 'on_pre_enter'):
                    screen.on_pre_enter()
            except Exception as e:
                print(f"Failed to preload {screen_name}: {e}")


# Usage examples for screens:
"""
# In your screen class:

from src.utils.performance import debounce, async_operation, lazy_property

class MyScreen(Screen):
    
    @debounce(delay=0.5)
    def on_button_click(self):
        # This will ignore rapid clicks within 0.5 seconds
        self.process_action()
    
    @async_operation(callback='on_data_received')
    def fetch_data(self):
        # This runs in background thread
        data = api.get_data()
        return data
    
    def on_data_received(self, data):
        # This runs on main thread
        self.update_ui(data)
    
    @lazy_property
    def expensive_layout(self):
        # Computed once, then cached
        return self.create_complex_layout()
"""
