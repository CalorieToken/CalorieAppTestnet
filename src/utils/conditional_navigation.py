"""
Conditional Navigation Drawer System
Provides navigation drawer only for screens that need it, improving performance
"""

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationDrawerDivider,
    MDNavigationDrawerHeader,
    MDNavigationDrawerItem,
    MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText,
    MDNavigationDrawerMenu,
)


class ConditionalNavigationDrawer(MDNavigationDrawer):
    """Navigation drawer that only appears on specific screens"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.71, 0.75, 0.86, 1)  # rgba('#b6bedb')
        self.radius = (0, 16, 16, 0)
        self.scrim_color = [0, 0, 0, 0.3]

        # Create navigation menu
        self.setup_navigation_menu()

    def setup_navigation_menu(self):
        """Setup the navigation drawer menu items"""
        nav_menu = MDNavigationDrawerMenu()

        # Header
        header = MDNavigationDrawerHeader(
            spacing=dp(4),
            padding=(dp(12), 0, 0, dp(56)),
        )
        # Add a label for the title since MDNavigationDrawerHeader no longer exposes title properties
        header_label = MDLabel(
            text="CalorieApp",
            theme_text_color="Custom",
            text_color="#202443",
            bold=True,
            halign="left",
        )
        header.add_widget(header_label)
        nav_menu.add_widget(header)

        # Divider
        nav_menu.add_widget(MDNavigationDrawerDivider())

        # Get app instance for navigation
        app = MDApp.get_running_app()

        # Menu items using standard MDNavigationDrawerItem
        menu_items = [
            {"icon": "wallet", "text": "Wallet", "callback": app.navigate_to_wallet},
            {"icon": "brush", "text": "NFT Minter", "callback": app.navigate_to_nft_mint},
            {
                "icon": "wallet-plus",
                "text": "Create/Import Wallet",
                "callback": app.navigate_to_create_import_wallet,
            },
            {
                "icon": "arrow-left-right-bold-outline",
                "text": "DEX Trade",
                "callback": app.navigate_to_dex_trade,
            },
            {"icon": "food", "text": "Food Tracker", "callback": app.navigate_to_food_track},
            {
                "icon": "application-settings",
                "text": "Settings",
                "callback": app.navigate_to_settings,
            },
        ]

        for item in menu_items:
            # Create drawer item
            nav_item = MDNavigationDrawerItem()

            # Add icon as child widget
            if item.get("icon"):
                icon_widget = MDNavigationDrawerItemLeadingIcon(icon=item["icon"])
                icon_widget.icon_color = "#008D36"  # Green icon color
                nav_item.add_widget(icon_widget)

            # Add text as child widget
            if item.get("text"):
                text_widget = MDNavigationDrawerItemText(text=item["text"])
                text_widget.text_color = "#202443"  # Dark text color
                nav_item.add_widget(text_widget)

            # Bind callback
            nav_item.bind(on_press=self._create_nav_callback(item["callback"]))

            # Apply styling colors
            nav_item.focus_color = "#dadeed"
            nav_item.ripple_color = "#c5bdd2"
            nav_item.selected_color = "#4a4939"

            nav_menu.add_widget(nav_item)

        self.add_widget(nav_menu)

    def _create_nav_callback(self, navigation_callback):
        """Create a callback that navigates and closes the drawer"""

        def callback(*args):
            if navigation_callback:
                navigation_callback()
            self.set_state("close")

        return callback


class ScreenWithDrawer(MDFloatLayout):
    """Base layout for screens that need navigation drawer"""

    def __init__(self, screen_content, **kwargs):
        super().__init__(**kwargs)

        # Add the screen content first
        self.add_widget(screen_content)

        # Add navigation drawer on top
        self.nav_drawer = ConditionalNavigationDrawer()
        self.add_widget(self.nav_drawer)

    def toggle_drawer(self):
        """Toggle navigation drawer open/close"""
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
        else:
            self.nav_drawer.set_state("open")


class ScreenWithoutDrawer(MDFloatLayout):
    """Base layout for screens that don't need navigation drawer"""

    def __init__(self, screen_content, **kwargs):
        super().__init__(**kwargs)

        # Only add the screen content
        self.add_widget(screen_content)


def create_screen_layout(screen_content, needs_drawer=False):
    """
    Factory function to create appropriate screen layout

    Args:
        screen_content: The main content widget for the screen
        needs_drawer: Boolean indicating if screen needs navigation drawer

    Returns:
        ScreenWithDrawer or ScreenWithoutDrawer instance
    """
    if needs_drawer:
        return ScreenWithDrawer(screen_content)
    else:
        return ScreenWithoutDrawer(screen_content)


# Screen classification for navigation drawer needs
DRAWER_ENABLED_SCREENS = {
    "wallet_screen",
    "nftmint_screen",
    "createimportwallet_screen",
    "dextrade_screen",
    "foodtrack_screen",
    "settings_screen",
}

DRAWER_DISABLED_SCREENS = {
    "intro_screen",
    "first_use_screen",
    "wallet_setup_screen",
    "create_wallet_screen",
    "importkeys_screen",
    "login_screen",
    "sendxrp_screen",
    "add_trustline_screen",  # Trustline management
    # Generic token send screens can be added dynamically
    "create_extrawallet_screen",
    "import_extra_keys_screen",
}


def screen_needs_drawer(screen_name):
    """Check if a screen needs navigation drawer"""
    return screen_name in DRAWER_ENABLED_SCREENS
