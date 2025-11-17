import logging
import os
import shelve

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout

# Import version information
from VERSION import __version__
from xrpl.clients import JsonRpcClient

from src.screens.AccountChoiceScreen import AccountChoiceScreen
from src.screens.AccountNamingScreen import AccountNamingScreen
from src.screens.AddTrustlineScreen import AddTrustlineScreen
from src.screens.CreateExtraWalletScreen import CreateExtraWalletScreen
from src.screens.CreateImportWalletScreen import CreateImportWalletScreen
from src.screens.CreateWalletScreen import CreateWalletScreen
from src.screens.DEXTradeScreen import DEXTradeScreen
from src.screens.FirstUseScreen import FirstUseScreen
from src.screens.FoodTrackScreen import FoodTrackScreen
from src.screens.ImportChoiceScreen import ImportChoiceScreen
from src.screens.ImportExtraKeysScreen import ImportExtraKeysScreen
from src.screens.ImportKeysScreen import ImportKeysScreen
from src.screens.IntroScreen import IntroScreen
from src.screens.KeypairImportScreen import KeypairImportScreen
from src.screens.LoginScreen import LoginScreen
from src.screens.MnemonicDisplayScreen import MnemonicDisplayScreen
from src.screens.MnemonicImportScreen import MnemonicImportScreen
from src.screens.MnemonicVerifyScreen import MnemonicVerifyScreen
from src.screens.NFTMintScreen import NFTMintScreen
from src.screens.SendXRPScreen import SendXRPScreen
from src.screens.SettingsScreen import SettingsScreen

# Import screens from src.screens folder.
from src.screens.WalletScreen import WalletScreen
from src.screens.WalletSetupScreen import WalletSetupScreen
from src.utils.conditional_navigation import ConditionalNavigationDrawer, screen_needs_drawer

# Import the robust XRPL client manager
from src.utils.xrpl_client_manager import XRPLClientManager

logging.basicConfig(level=logging.ERROR)  # Reduce log verbosity
# Reduce HTTP debug logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Network configuration with robust failover support
# Global flags for selective offline mode
OFFLINE_MODE = os.environ.get("OFFLINE_MODE", "0").lower() in ("1", "true", "yes")

# Initialize the global XRPL client manager with multiple servers
XRPL_SERVERS = [
    "https://testnet.xrpl-labs.com",  # Primary: XRPL Labs testnet
    "https://s.altnet.rippletest.net:51234",  # Backup: Ripple altnet
    "https://testnet.xrplapi.com",  # Backup: Another testnet API
    "https://xrplcluster.com",  # Backup: Community cluster (if available)
]

if not OFFLINE_MODE:
    # Initialize the robust client manager
    client_manager = XRPLClientManager(servers=XRPL_SERVERS)
    if client_manager.is_connected():
        print(f"[SUCCESS] Connected to XRPL server: {client_manager.get_current_server()}")
        client = client_manager.get_client()
        JSON_RPC_URL = client_manager.get_current_server()
    else:
        print("[ERROR] Could not connect to any XRPL servers - enabling offline mode")
        OFFLINE_MODE = True
        client = None
        JSON_RPC_URL = XRPL_SERVERS[0]  # Keep first server as default
else:
    client_manager = None
    client = None
    JSON_RPC_URL = (
        XRPL_SERVERS[0] if "XRPL_SERVERS" in locals() else "https://testnet.xrpl-labs.com"
    )
    print("🔌 Running in offline mode - XRPL connectivity disabled")


# Root layout class that manages the screen manager only
class RootLayout(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Much simpler - just store screen manager reference
        self.manager = None


# Main app class.
class CalorieAppTestnet(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_application_name(self):
        """Override to prevent auto KV file loading"""
        return "CalorieApp"

    def build(self):
        """Build the main application"""
        # Don't set icon as we don't have one
        # self.icon = "path/to/icon.png"
        self.title = f"CalorieApp Testnet v{__version__}"

        # Configure the window
        Window.size = (300, 630)  # Mobile dimensions
        # Window.top = 90
        # Window.left = 50

        # Window configuration improvements
        Window.softinput_mode = "below_target"
        Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
        Window.keyboard_mode = "managed"

        # Enhanced theme system for better visuals
        # Theme configuration for consistent appearance
        # Updated theme system for KivyMD 1.2.0
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.material_style = "M3"  # Updated from M2 to M3
        self.theme_cls.theme_style = "Light"  # Explicitly set theme style

        # Load KV layout resources (modular only; monolithic removed)
        kv_dir = os.path.join(os.path.dirname(__file__), "kv")
        if os.path.isdir(kv_dir):
            kv_files = []
            base_path = os.path.join(kv_dir, "base.kv")
            if os.path.exists(base_path):
                kv_files.append(base_path)
            for name in sorted(os.listdir(kv_dir)):
                if name.endswith(".kv") and name != "base.kv":
                    kv_files.append(os.path.join(kv_dir, name))
            for kv_file in kv_files:
                try:
                    Builder.load_file(kv_file)
                    logger.info(f"Loaded KV file: {os.path.basename(kv_file)}")
                except Exception as e:
                    logger.error(f"Failed to load {kv_file}: {e}")
        else:
            logger.error("KV directory missing; UI will not render correctly")

        # Initialize XRPL client
        JSON_RPC_URL = "https://testnet.xrpl-labs.com"
        if not OFFLINE_MODE:
            try:
                client = JsonRpcClient(JSON_RPC_URL)
            except Exception as e:
                print(f"Failed to connect to XRPL in build: {e}")
                client = None
        else:
            client = None

        # Create the root layout with navigation drawer from kv file
        self.root_layout = RootLayout()

        # Create screen manager directly since KV might not be loaded properly
        from kivy.uix.screenmanager import ScreenManager

        self.manager = ScreenManager()
        self.root_layout.add_widget(self.manager)

        # Initialize the screens
        self.intro_screen = IntroScreen(name="intro_screen")
        self.first_use_screen = FirstUseScreen(name="first_use_screen")
        self.wallet_setup_screen = WalletSetupScreen(name="wallet_setup_screen")
        self.create_wallet_screen = CreateWalletScreen(name="create_wallet_screen")
        self.create_extrawallet_screen = CreateExtraWalletScreen(name="create_extrawallet_screen")
        self.importkeys_screen = ImportKeysScreen(name="importkeys_screen")
        self.importextrakeys_screen = ImportExtraKeysScreen(name="import_extra_keys_screen")
        self.login_screen = LoginScreen(name="login_screen")
        self.mnemonic_display_screen = MnemonicDisplayScreen(name="mnemonic_display_screen")
        self.mnemonic_import_screen = MnemonicImportScreen(name="mnemonic_import_screen")
        self.account_choice_screen = AccountChoiceScreen(name="account_choice_screen")
        self.import_choice_screen = ImportChoiceScreen(name="import_choice_screen")
        self.keypair_import_screen = KeypairImportScreen(name="keypair_import_screen")
        self.mnemonic_verify_screen = MnemonicVerifyScreen(name="mnemonic_verify_screen")
        self.account_naming_screen = AccountNamingScreen(name="account_naming_screen")
        self.wallet_screen = WalletScreen(client=client, name="wallet_screen")
        # Update offline mode status
        if hasattr(self.wallet_screen, "update_offline_mode"):
            self.wallet_screen.update_offline_mode(OFFLINE_MODE)
        self.sendxrp_screen = SendXRPScreen(client=client, name="sendxrp_screen")
        # Generic token screens can be added here as needed
        # Example: self.send_customtoken_screen = SendTestTokenScreen(client=client, token_id="custom_token", name="send_customtoken_screen")
        self.add_trustline_screen = AddTrustlineScreen(name="add_trustline_screen")
        self.nftmint_screen = NFTMintScreen(name="nftmint_screen")
        self.createimportwallet_screen = CreateImportWalletScreen(name="createimportwallet_screen")
        self.dextrade_screen = DEXTradeScreen(name="dextrade_screen")
        self.foodtrack_screen = FoodTrackScreen(name="foodtrack_screen")
        self.settings_screen = SettingsScreen(name="settings_screen")

        # Add all screens to manager
        self.manager.add_widget(self.intro_screen)
        self.manager.add_widget(self.first_use_screen)
        self.manager.add_widget(self.wallet_setup_screen)
        self.manager.add_widget(self.create_wallet_screen)
        self.manager.add_widget(self.create_extrawallet_screen)
        self.manager.add_widget(self.importkeys_screen)
        self.manager.add_widget(self.importextrakeys_screen)
        self.manager.add_widget(self.login_screen)
        self.manager.add_widget(self.mnemonic_display_screen)
        self.manager.add_widget(self.mnemonic_import_screen)
        self.manager.add_widget(self.account_choice_screen)
        self.manager.add_widget(self.import_choice_screen)
        self.manager.add_widget(self.keypair_import_screen)
        self.manager.add_widget(self.mnemonic_verify_screen)
        self.manager.add_widget(self.account_naming_screen)
        self.manager.add_widget(self.wallet_screen)
        self.manager.add_widget(self.sendxrp_screen)
        # Generic token screens can be added dynamically based on token_config
        self.manager.add_widget(self.add_trustline_screen)
        self.manager.add_widget(self.nftmint_screen)
        self.manager.add_widget(self.createimportwallet_screen)
        self.manager.add_widget(self.dextrade_screen)
        self.manager.add_widget(self.foodtrack_screen)
        self.manager.add_widget(self.settings_screen)

        # Determine initial screen based on wallet data - optimized for speed

        # Bind screen change event to add/remove navigation drawers conditionally
        self.manager.bind(current=self.on_screen_change)

        # Start with intro screen immediately to avoid lag
        self.manager.current = "intro_screen"

        return self.root_layout

    def initial_drawer_setup(self, dt):
        """Initial setup to disable drawer for new users"""
        # Check if this is a new user (no wallet data)
        try:
            with shelve.open("wallet_data") as wallet_data:
                if "password" not in wallet_data:
                    # New user - disable navigation drawer
                    self.disable_navigation_drawer()
                else:
                    # Existing user going to login - enable navigation drawer
                    self.enable_navigation_drawer()
        except Exception:
            # No wallet data file exists - definitely new user
            self.disable_navigation_drawer()

    def navigate_to_wallet(self):
        """Navigate to wallet screen"""
        self.manager.current = "wallet_screen"

    def navigate_to_nft_mint(self):
        """Navigate to NFT mint screen"""
        self.manager.current = "nftmint_screen"

    def navigate_to_create_import_wallet(self):
        """Navigate to create/import wallet screen"""
        self.manager.current = "createimportwallet_screen"

    def navigate_to_dex_trade(self):
        """Navigate to DEX trade screen"""
        self.manager.current = "dextrade_screen"

    def navigate_to_food_track(self):
        """Navigate to food tracking screen"""
        self.manager.current = "foodtrack_screen"

    def navigate_to_settings(self):
        """Navigate to settings screen"""
        self.manager.current = "settings_screen"

    def toggle_current_screen_drawer(self):
        """Toggle navigation drawer for the current screen if it has one"""
        current_screen = self.manager.get_screen(self.manager.current)
        if hasattr(current_screen, "_nav_drawer") and current_screen._nav_drawer:
            if current_screen._nav_drawer.state == "open":
                current_screen._nav_drawer.set_state("close")
            else:
                current_screen._nav_drawer.set_state("open")

    def on_screen_change(self, screen_manager, screen_name):
        """Handle screen changes - add/remove navigation drawer as needed"""
        current_screen = screen_manager.current

        # Get the actual screen widget
        screen_widget = screen_manager.get_screen(current_screen)

        # Check if this screen needs a navigation drawer
        if screen_needs_drawer(current_screen):
            self.add_navigation_drawer_to_screen(screen_widget)
        else:
            self.remove_navigation_drawer_from_screen(screen_widget)

    def add_navigation_drawer_to_screen(self, screen_widget):
        """Add navigation drawer to a specific screen"""
        # Check if drawer already exists
        if hasattr(screen_widget, "_nav_drawer") and screen_widget._nav_drawer:
            return  # Already has drawer

        # Create navigation drawer
        nav_drawer = ConditionalNavigationDrawer()

        # Add drawer to screen
        screen_widget.add_widget(nav_drawer)
        screen_widget._nav_drawer = nav_drawer
        # Rely on PrimaryBottomBar's single menu button to toggle the drawer.
        # We intentionally avoid adding an extra floating overlay menu button
        # to prevent duplicate/overlapping menu triggers.

    def remove_navigation_drawer_from_screen(self, screen_widget):
        """Remove navigation drawer from a specific screen"""
        # Remove existing drawer if present
        if hasattr(screen_widget, "_nav_drawer") and screen_widget._nav_drawer:
            screen_widget.remove_widget(screen_widget._nav_drawer)
            screen_widget._nav_drawer = None
        # Remove overlay menu button if present
        if hasattr(screen_widget, "_menu_overlay") and screen_widget._menu_overlay:
            try:
                screen_widget.remove_widget(screen_widget._menu_overlay)
            except Exception:
                pass
            screen_widget._menu_overlay = None
            screen_widget._menu_fab = None

    def add_hamburger_button_to_screen(self, screen_widget, nav_drawer):
        """Add a bottom-left floating menu button overlay on screens with a drawer"""
        try:
            # Clean up any existing overlay
            if hasattr(screen_widget, "_menu_overlay") and screen_widget._menu_overlay:
                try:
                    screen_widget.remove_widget(screen_widget._menu_overlay)
                except Exception:
                    pass
                screen_widget._menu_overlay = None
                screen_widget._menu_fab = None

            overlay = MDFloatLayout(size_hint=(1, 1))
            fab = MDIconButton(
                icon="menu",
                theme_icon_color="Custom",
                icon_color=get_color_from_hex("#FFFFFF"),
                md_bg_color=get_color_from_hex("#505CA9"),
                size_hint=(None, None),
                pos_hint={"x": 0.03, "y": 0.03},
            )
            fab.bind(on_release=lambda *_: self.toggle_current_screen_drawer())
            overlay.add_widget(fab)
            screen_widget.add_widget(overlay)

            screen_widget._menu_overlay = overlay
            screen_widget._menu_fab = fab
        except Exception:
            # Silently handle menu button errors
            pass

    def on_stop(self):
        """Clean up resources when app stops"""
        pass


if __name__ == "__main__":
    CalorieAppTestnet().run()
