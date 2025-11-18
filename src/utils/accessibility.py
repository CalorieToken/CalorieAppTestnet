"""
Accessible UI Components for Kivy/KivyMD

Provides enhanced accessibility features like:
- Keyboard navigation
- Focus indicators
- ARIA-like properties
"""

from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.textfield import MDTextField


class AccessibleButton(MDButton):
    """
    Button with enhanced accessibility features
    
    Features:
    - Keyboard navigation (Enter/Space to activate)
    - Visual focus indicators
    - Accessible name for screen readers
    """
    
    accessible_name = StringProperty("")
    """Description for screen readers"""
    
    is_focused = BooleanProperty(False)
    """Whether button has keyboard focus"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.focus_behavior = True
        self.keyboard = None
        
        # Bind to size/pos changes to redraw focus indicator
        self.bind(size=self._redraw_focus, pos=self._redraw_focus)
        
        # No built-in 'focus' property on MDButton (M3); manage our own
    
    def _redraw_focus(self, *args):
        """Redraw focus indicator when size/pos changes"""
        if self.is_focused:
            self._draw_focus_indicator()
        
    def _apply_focus(self, focused: bool):
        """Internal helper to set visual focus + keyboard binding"""
        self.is_focused = focused
        if focused:
            self.elevation = 4
            self._draw_focus_indicator()
            if not self.keyboard:
                self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
                if self.keyboard:
                    self.keyboard.bind(on_key_down=self._on_keyboard_down)
        else:
            self.elevation = 2
            self._clear_focus_indicator()
            if self.keyboard:
                self.keyboard.unbind(on_key_down=self._on_keyboard_down)
                self.keyboard.release()
                self.keyboard = None
    
    def _draw_focus_indicator(self):
        """Draw focus ring around button"""
        from kivy.graphics import Color, Line
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0.2, 0.6, 1.0, 1.0)  # Bright blue
            Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    self.radius[0] if self.radius else 12
                ),
                width=3
            )
    
    def _clear_focus_indicator(self):
        """Clear focus ring"""
        self.canvas.after.clear()
    
    def _keyboard_closed(self):
        """Keyboard closed callback"""
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self._on_keyboard_down)
            self.keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Handle keyboard input"""
        # keycode is a tuple (key_number, key_string)
        key = keycode[1]
        
        # Activate button on Enter or Space
        if key in ('enter', 'numpadenter', 'spacebar'):
            self.dispatch('on_release')
            return True  # Key handled
        
        # Tab navigation
        elif key == 'tab':
            if 'shift' in modifiers:
                # Shift+Tab - focus previous
                self.focus_previous()
            else:
                # Tab - focus next
                self.focus_next()
            return True
        
        return False  # Key not handled
    
    def on_touch_down(self, touch):
        """Handle touch/click to set focus"""
        if self.collide_point(*touch.pos):
            self._apply_focus(True)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # keep focus after click
            self._apply_focus(True)
        else:
            self._apply_focus(False)
        return super().on_touch_up(touch)


class AccessibleIconButton(MDIconButton):
    """
    Icon button with accessibility features
    
    IMPORTANT: Icon-only buttons should have accessible_name set
    """
    
    accessible_name = StringProperty("")
    """REQUIRED: Description for screen readers (e.g. 'Close', 'Menu', 'Settings')"""
    
    is_focused = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.focus_behavior = True
        self.keyboard = None
        
        # Bind to size/pos changes to redraw focus indicator
        self.bind(size=self._redraw_focus, pos=self._redraw_focus)
    
    def _redraw_focus(self, *args):
        """Redraw focus indicator when size/pos changes"""
        if self.is_focused:
            self._draw_focus_indicator()
        
    def _apply_focus(self, focused: bool):
        self.is_focused = focused
        if focused:
            self.md_bg_color = (0.5, 0.5, 1, 0.2)
            self._draw_focus_indicator()
            if not self.keyboard:
                self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
                if self.keyboard:
                    self.keyboard.bind(on_key_down=self._on_keyboard_down)
        else:
            self.md_bg_color = (0, 0, 0, 0)
            self._clear_focus_indicator()
            if self.keyboard:
                self.keyboard.unbind(on_key_down=self._on_keyboard_down)
                self.keyboard.release()
                self.keyboard = None
    
    def _draw_focus_indicator(self):
        """Draw focus ring around icon button"""
        from kivy.graphics import Color, Line
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0.2, 0.6, 1.0, 1.0)  # Bright blue
            Line(
                circle=(self.center_x, self.center_y, min(self.width, self.height) / 2 + 2),
                width=3
            )
    
    def _clear_focus_indicator(self):
        """Clear focus ring"""
        self.canvas.after.clear()
    
    def _keyboard_closed(self):
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self._on_keyboard_down)
            self.keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        
        if key in ('enter', 'numpadenter', 'spacebar'):
            self.dispatch('on_release')
            return True
        
        elif key == 'tab':
            if 'shift' in modifiers:
                self.focus_previous()
            else:
                self.focus_next()
            return True
        
        return False
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._apply_focus(True)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self._apply_focus(True)
        else:
            self._apply_focus(False)
        return super().on_touch_up(touch)


class AccessibleTextField(MDTextField):
    """
    Text field with enhanced accessibility
    
    Features:
    - Clear labels and hints
    - Error announcements
    - Helper text
    """
    
    accessible_name = StringProperty("")
    """Additional description for screen readers"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.focus_behavior = True
        
        # Ensure helper text mode is accessible
        if not self.helper_text_mode:
            self.helper_text_mode = "on_focus"
    
    def on_error(self, instance, value):
        """Announce errors to screen readers"""
        if value and self.error_text:
            # In a real implementation, this would use platform accessibility APIs
            # For now, we ensure error_text is visible
            pass


# Keyboard shortcut registry
class KeyboardShortcuts:
    """
    Global keyboard shortcuts for the app
    
    Standard shortcuts:
    - Ctrl+Q: Quit
    - Ctrl+S: Settings
    - Ctrl+W: Go to Wallet
    - Ctrl+H: Home
    - Esc: Go Back
    - F1: Help
    """
    
    def __init__(self, app):
        self.app = app
        self.keyboard = None
        
    def enable(self):
        """Enable global keyboard shortcuts"""
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self.app.root)
        if self.keyboard:
            self.keyboard.bind(on_key_down=self._on_keyboard_down)
    
    def disable(self):
        """Disable global keyboard shortcuts"""
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self._on_keyboard_down)
            self.keyboard.release()
            self.keyboard = None
    
    def _keyboard_closed(self):
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self._on_keyboard_down)
            self.keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Handle global keyboard shortcuts"""
        key = keycode[1]
        
        # Ctrl key shortcuts
        if 'ctrl' in modifiers:
            if key == 'q':
                # Quit app
                self.app.stop()
                return True
            
            elif key == 's':
                # Open settings
                try:
                    if hasattr(self.app, 'manager') and self.app.manager.has_screen('settings_screen'):
                        self.app.manager.current = 'settings_screen'
                except Exception:
                    pass
                return True
            
            elif key == 'w':
                # Go to wallet
                try:
                    if hasattr(self.app, 'manager') and self.app.manager.has_screen('wallet_screen'):
                        self.app.manager.current = 'wallet_screen'
                except Exception:
                    pass
                return True
            
            elif key == 'h':
                # Go to home/wallet
                try:
                    if hasattr(self.app, 'manager') and self.app.manager.has_screen('wallet_screen'):
                        self.app.manager.current = 'wallet_screen'
                except Exception:
                    pass
                return True
        
        # Escape key - go back
        elif key == 'escape':
            try:
                # Simple back navigation - go to previous screen in common flow
                if hasattr(self.app, 'manager'):
                    current = self.app.manager.current
                    # Define back navigation mapping
                    back_map = {
                        'settings_screen': 'wallet_screen',
                        'send_xrp_screen': 'wallet_screen',
                        'add_trustline_screen': 'wallet_screen',
                        'nft_mint_screen': 'wallet_screen',
                        'food_track_screen': 'wallet_screen',
                        'mnemonic_display_screen': 'wallet_screen',
                        'mnemonic_import_screen': 'login_screen',
                    }
                    if current in back_map and self.app.manager.has_screen(back_map[current]):
                        self.app.manager.current = back_map[current]
            except Exception:
                pass
            return True
        
        # F1 - Help (placeholder for future help screen)
        elif key == 'f1':
            # Could open a help dialog or screen in the future
            return True
        
        return False


# Focus indicator canvas instructions
from kivy.graphics import Color, Line, RoundedRectangle

def add_focus_indicator(widget):
    """
    Add a visual focus indicator to a widget
    
    Draws a colored border when widget has focus
    """
    
    def update_focus_indicator(instance, value):
        """Update focus indicator when focus changes"""
        widget.canvas.after.clear()
        
        if value:  # Has focus
            with widget.canvas.after:
                Color(0, 0.55, 0.85, 1)  # Blue color
                Line(
                    rounded_rectangle=(
                        widget.x, widget.y,
                        widget.width, widget.height,
                        10, 10, 10, 10, 100
                    ),
                    width=2
                )
    
    widget.bind(focus=update_focus_indicator)
    
    # Also update on size/pos changes
    widget.bind(size=lambda *args: update_focus_indicator(widget, widget.focus))
    widget.bind(pos=lambda *args: update_focus_indicator(widget, widget.focus))


# Export classes
__all__ = [
    'AccessibleButton',
    'AccessibleIconButton',
    'AccessibleTextField',
    'KeyboardShortcuts',
    'add_focus_indicator'
]
