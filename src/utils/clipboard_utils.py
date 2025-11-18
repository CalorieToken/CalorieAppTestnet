from kivy.clock import Clock
from kivy.core.clipboard import Clipboard


def secure_copy(text: str, clear_after: float = 30.0) -> None:
    """Copy sensitive text to clipboard and auto-clear after a delay.

    - Copies the provided text to the clipboard immediately.
    - Schedules clipboard to be cleared after `clear_after` seconds if
      the clipboard content hasn't changed in the meantime.
    """
    try:
        Clipboard.copy(text or "")
    except Exception:
        return

    def _clear_clipboard(_dt):
        try:
            current = Clipboard.paste()
            if current == (text or ""):
                Clipboard.copy("")
        except Exception:
            pass

    try:
        Clock.schedule_once(_clear_clipboard, clear_after)
    except Exception:
        pass
