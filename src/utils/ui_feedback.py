from kivymd.uix.snackbar import snackbar
from kivymd.app import MDApp


def _show(message: str, bg_color: tuple | None = None, duration: float = 3.0):
    app = MDApp.get_running_app()
    if not app:
        return
    # Provide sensible default background using current primary palette
    if bg_color is None:
        # app.theme_cls.primary_color returns current theme primary color
        bg_color = app.theme_cls.primary_color
    try:
        snackbar.Snackbar(text=message, bg_color=bg_color, duration=duration).open()
    except Exception:
        # Fail silently to avoid cascading UI errors
        pass


def info(message: str):
    _show(message)


def success(message: str):
    # Slight tint greener if available; fallback to primary
    app = MDApp.get_running_app()
    color = None
    try:
        if hasattr(app.theme_cls, "primary_light"):
            color = app.theme_cls.primary_light
    except Exception:
        pass
    _show(message, bg_color=color)


def error(message: str):
    # Red tone for errors; fallback to primary color
    app = MDApp.get_running_app()
    color = None
    try:
        color = (0.85, 0.2, 0.2, 1)
    except Exception:
        pass
    _show(message, bg_color=color, duration=4.0)
