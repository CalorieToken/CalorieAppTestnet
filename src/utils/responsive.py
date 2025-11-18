import os
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

# Breakpoints (portrait width oriented) inspired by common mobile/tablet/desktop ranges
_BREAKPOINTS = [
    (360, "xs"),    # very small phones
    (480, "sm"),    # standard phones
    (768, "md"),    # small tablets / large phones landscape
    (1024, "lg"),   # tablets
    (1280, "xl"),   # small desktops
]

_SIZE_FACTORS = {
    "xs": 0.85,
    "sm": 1.00,
    "md": 1.10,
    "lg": 1.20,
    "xl": 1.30,
}

_FONT_FACTORS = {
    "xs": 0.80,
    "sm": 1.00,
    "md": 1.05,
    "lg": 1.10,
    "xl": 1.15,
}

_cached_size_class = None
_cached_size_factor = 1.0
_cached_font_factor = 1.0
_cached_width = None  # Track last computed width for lazy recompute
_dp_cache = {}  # Precomputed common dp values {dp_value: scaled_value}

def _apply_forced_size_class(raw: str) -> str:
    """Map external override to an internal size class."""
    if not raw:
        return ""
    forced = raw.strip().lower()
    if forced in ("xs","sm","md","lg","xl"):
        return forced
    if forced == "phone":
        return "sm"
    return ""

def _needs_recompute(new_width) -> bool:
    """Check if width change crosses a breakpoint boundary (lazy optimization)."""
    global _cached_width
    if _cached_width is None or _cached_size_class is None:
        return True
    
    # If forced size class, never recompute
    if _apply_forced_size_class(os.environ.get("FORCE_SIZE_CLASS", "")):
        return False
    
    old_class = _derive_size_class(_cached_width)
    new_class = _derive_size_class(new_width)
    return old_class != new_class


def _recompute_cache(width=None):
    """Recompute cached size class and scaling factors."""
    global _cached_size_class, _cached_size_factor, _cached_font_factor, _cached_width, _dp_cache
    forced_env = os.environ.get("FORCE_SIZE_CLASS", "")
    forced = _apply_forced_size_class(forced_env)
    
    w = width if width is not None else Window.width
    _cached_width = w
    
    if forced:
        _cached_size_class = forced
    else:
        _cached_size_class = _derive_size_class(w)
    _cached_size_factor = _SIZE_FACTORS.get(_cached_size_class, 1.0)
    _cached_font_factor = _FONT_FACTORS.get(_cached_size_class, 1.0)
    
    # Precompute common dp values for faster lookup
    common_dps = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 48, 56, 64, 72, 80]
    _dp_cache = {dp: dp * _cached_size_factor for dp in common_dps}

def _derive_size_class(width=None):
    w = width if width is not None else Window.width
    last = "xl"
    for bp, name in _BREAKPOINTS:
        if w < bp:
            return name
        last = name
    return last


def get_size_class(width=None):
    """Return current size class (cached; recompute if None)."""
    global _cached_size_class
    if _cached_size_class is None:
        _recompute_cache(width)
    return _cached_size_class


def scale_dp(base) -> float:
    """Scale a base dp/sp value or numeric using cached size factor.

    Accepts numeric or string ("24dp", "18sp", "24"). Returns float.
    Unparsable strings return 0.0 for safety (previous behavior).
    Common values use precomputed cache for faster lookup.
    """
    # Ensure cache initialized
    if _cached_size_class is None:
        _recompute_cache()
    
    # If already numeric
    if isinstance(base, (int, float)):
        # Check precomputed cache for common values
        if base in _dp_cache:
            return _dp_cache[base]
        return base * _cached_size_factor
    
    if isinstance(base, str):
        b = base.strip()
        try:
            if b.endswith("dp") or b.endswith("sp"):
                num = float(b[:-2])
                if num in _dp_cache:
                    return _dp_cache[num]
                return num * _cached_size_factor
            # Plain numeric string
            num = float(b)
            if num in _dp_cache:
                return _dp_cache[num]
            return num * _cached_size_factor
        except Exception:
            return 0.0  # fallback numeric if unparsable
    # Unknown type; return as-is
    return base


def scale_font(base_sp: float) -> float:
    if _cached_font_factor is None or _cached_size_class is None:
        _recompute_cache()
    return base_sp * _cached_font_factor


def init_responsive(app):
    """Initialize responsive system: compute cache, attach size_class, bind resize."""
    _recompute_cache()
    app.size_class = _cached_size_class

    def _on_resize(*args):
        # Lazy recompute: only if crossing breakpoint or forced class not set
        w = Window.width
        if _needs_recompute(w):
            _recompute_cache(w)
            app.size_class = _cached_size_class
    
    Window.bind(size=_on_resize)
    return app.size_class


class ResponsiveContainer(BoxLayout):
    """A centered container that constrains max width based on size class for better large-screen layouts."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Schedule initial adjust after layout
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._adjust(), 0)
        # Bind to window size changes for responsiveness
        Window.bind(size=lambda *a: self._adjust())

    def _max_width_for_class(self, cls):
        mapping = {
            'xs': 360,
            'sm': 420,
            'md': 640,
            'lg': 800,
            'xl': 1080,
        }
        return mapping.get(cls, 640)

    def _adjust(self, *args):
        cls = get_size_class()
        max_w = self._max_width_for_class(cls)
        # Center horizontally if parent wider
        if self.parent:
            pw = self.parent.width
            self.width = min(pw, max_w)
            self.x = (pw - self.width) / 2
        else:
            self.width = min(Window.width, max_w)
            self.x = (Window.width - self.width) / 2


class ResponsiveDebugOverlay(Label):
    """
    Small on-screen badge showing current size class and scale factors.
    Enable with DEBUG_RESPONSIVE=1 environment variable.
    Appears in top-right corner with semi-transparent background.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (180, 70)
        self.halign = 'left'
        self.valign = 'top'
        self.padding = (8, 8)
        self.font_size = '11sp'
        self.markup = True
        
        # Semi-transparent dark background
        with self.canvas.before:
            Color(0, 0, 0, 0.75)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        # Bind to update background position
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Update position on window resize
        Window.bind(size=self._update_position)
        self._update_position()
        self._update_text()
        
        # Refresh text periodically (in case of manual size class changes)
        from kivy.clock import Clock
        Clock.schedule_interval(lambda dt: self._update_text(), 1.0)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_position(self, *args):
        # Position in top-right corner with small margin
        self.x = Window.width - self.width - 10
        self.y = Window.height - self.height - 10

    def _update_text(self, *args):
        cls = get_size_class()
        size_f = _cached_size_factor
        font_f = _cached_font_factor
        forced = os.environ.get("FORCE_SIZE_CLASS", "")
        locked = " 🔒" if forced else ""
        
        self.text = (
            f"[b]Size:[/b] {cls}{locked}\n"
            f"[b]DP:[/b] {size_f:.2f}x  [b]Font:[/b] {font_f:.2f}x\n"
            f"[b]Window:[/b] {int(Window.width)}×{int(Window.height)}"
        )
