"""
Password Field Utility with Toggle Visibility
Provides reusable password field components with eye icon toggle
"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField


class PasswordFieldWithToggle(MDBoxLayout):
    """
    A password field with toggle visibility functionality
    Combines MDTextField with an eye icon for password reveal/hide
    """

    def __init__(self, **kwargs):
        # Extract TextField specific kwargs
        text_field_kwargs = {}
        layout_kwargs = {}

        # Separate TextField and layout kwargs
        text_field_props = [
            "hint_text",
            "mode",
            "line_color_focus",
            "hint_text_color_focus",
            "fill_color_normal",
            "fill_color_focus",
            "font_style",
            "text",
        ]

        for key, value in kwargs.items():
            if key in text_field_props:
                text_field_kwargs[key] = value
            else:
                layout_kwargs[key] = value

        # Initialize the layout
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height="48dp",
            spacing="8dp",
            **layout_kwargs,
        )

        self.password_visible = False

        # Create the password field
        self.password_field = MDTextField(password=True, size_hint_x=0.9, **text_field_kwargs)

        # Create the toggle icon
        self.toggle_icon = MDIconButton(
            icon="eye",
            theme_icon_color="Custom",
            icon_color=(0.31, 0.36, 0.66, 1),  # rgba('#505CA9')
            size_hint_x=0.1,
            size_hint_y=None,
            height="48dp",
            pos_hint={"center_y": 0.5},
            on_release=self.toggle_password_visibility,
        )

        # Add widgets to layout
        self.add_widget(self.password_field)
        self.add_widget(self.toggle_icon)

    def toggle_password_visibility(self, *args):
        """Toggle password visibility and update the eye icon"""
        self.password_visible = not self.password_visible

        # Toggle the password field visibility
        self.password_field.password = not self.password_visible

        # Update the eye icon
        if self.password_visible:
            self.toggle_icon.icon = "eye-off"
        else:
            self.toggle_icon.icon = "eye"

    @property
    def text(self):
        """Get the password text"""
        return self.password_field.text

    @text.setter
    def text(self, value):
        """Set the password text"""
        self.password_field.text = value

    @property
    def hint_text(self):
        """Get the hint text"""
        return self.password_field.hint_text

    @hint_text.setter
    def hint_text(self, value):
        """Set the hint text"""
        self.password_field.hint_text = value


def create_password_field_with_toggle(hint_text="Enter password", **kwargs):
    """
    Factory function to create a password field with toggle visibility

    Args:
        hint_text: Placeholder text for the password field
        **kwargs: Additional arguments for the password field

    Returns:
        PasswordFieldWithToggle: Configured password field with eye toggle
    """
    default_kwargs = {
        "hint_text": hint_text,
        "mode": "filled",
        "line_color_focus": (0, 0.55, 0.21, 1),  # rgba('#008D36')
        "hint_text_color_focus": (0, 0.55, 0.21, 1),  # rgba('#008D36')
        "fill_color_normal": (0.85, 0.87, 0.93, 1),  # rgba('#dadeed')
        "fill_color_focus": (0.91, 0.92, 0.96, 1),  # rgba('#e9ebf5')
        "font_style": "Body",
    }

    # Merge with provided kwargs
    default_kwargs.update(kwargs)

    return PasswordFieldWithToggle(**default_kwargs)
