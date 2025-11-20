import logging
import os
import shelve
import threading

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout

# Import version information
from src.VERSION import __version__
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
from src.screens.BarcodeScanScreen import BarcodeScanScreen
from src.screens.CameraScanScreen import CameraScanScreen
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
from src.core.feature_flags import ENABLE_WEB3_BROWSER
if ENABLE_WEB3_BROWSER:
    from src._deferred.Web3BrowserScreen import Web3BrowserScreen  # type: ignore
from src.screens.WebViewScreen import WebViewScreen
from src.utils.wallet_connect.xaman_connector import XamanConnector
from src.utils.responsive import init_responsive, get_size_class, scale_dp, scale_font, ResponsiveDebugOverlay

# Import screens from src.screens folder.
from src.screens.WalletScreen import WalletScreen
from src.screens.WalletSetupScreen import WalletSetupScreen
from src.utils.conditional_navigation import ConditionalNavigationDrawer, screen_needs_drawer
# Ensure custom accessible widgets are registered before loading KV files
try:
    from src.utils.accessibility import AccessibleButton, AccessibleIconButton  # noqa: F401
except Exception:
    AccessibleButton = None  # type: ignore
    AccessibleIconButton = None  # type: ignore

# Import the robust XRPL client manager
from src.utils.xrpl_client_manager import XRPLClientManager
# Accessibility utilities (keyboard shortcuts, focus helpers)
try:
    from src.utils.accessibility import KeyboardShortcuts
except Exception:
    KeyboardShortcuts = None

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
        self._theme_pref_key = "ui_theme_style"
        self._palette_pref_key = "ui_primary_palette"
        # Wallet connector (XRPL testnet via Xaman stub)
        self.wallet_connector = XamanConnector()
        # Accessibility shortcuts
        self.shortcuts = None
        # Track deferred initialization
        self._screens_loaded = False
        self._loading_screens = False

    def get_application_name(self):
        """Override to prevent auto KV file loading"""
        return "CalorieApp"

    def build(self):
        """Build the main application"""
        # Don't set icon as we don't have one
        # self.icon = "path/to/icon.png"
        self.title = f"CalorieApp Testnet v{__version__}"

        # Configure the window: allow override; otherwise keep existing size (more responsive)
        try:
            force_w = os.environ.get("APP_FORCE_WIDTH")
            force_h = os.environ.get("APP_FORCE_HEIGHT")
            dev_viewport = os.environ.get("DEV_PHONE_VIEWPORT")  # e.g. "390x844"
            if (not force_w or not force_h) and dev_viewport:
                parts = dev_viewport.lower().replace(" ", "").split("x")
                if len(parts) == 2:
                    try:
                        vw = int(parts[0]); vh = int(parts[1])
                        # Ensure portrait orientation for dev tours
                        if vw > vh:
                            vw, vh = vh, vw
                        Window.size = (max(vw, 300), max(vh, 600))
                    except Exception:
                        pass
            if force_w and force_h:
                Window.size = (int(force_w), int(force_h))
            elif Window.width < 300 or Window.height < 600:
                # Provide a reasonable minimum portrait size without enforcing a large desktop window
                Window.size = (max(Window.width, 300), max(Window.height, 600))
        except Exception:
            pass
        # Window.top = 90
        # Window.left = 50

        # Window configuration improvements
        Window.softinput_mode = "below_target"
        Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
        Window.keyboard_mode = "managed"

        # Enhanced theme system for better visuals
        # Theme configuration for consistent appearance (Material 3)
        self.theme_cls.primary_palette = self._load_primary_palette()
        self.theme_cls.accent_palette = self.theme_cls.primary_palette
        self.theme_cls.material_style = "M3"

        # Apply persisted theme preference (Light/Dark), default to Light
        self.theme_cls.theme_style = self._load_theme_style()

        # Initialize responsive sizing system BEFORE loading KV so app.size_class
        # exists for any KV rules that reference it (e.g. intro_screen.kv).
        # Respect FORCE_SIZE_CLASS / DEV_PHONE_VIEWPORT overrides for dev consistency.
        try:
            init_responsive(self)
        except Exception as e:
            logger.warning(f"Responsive init (early) failed: {e}")

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
        from kivy.uix.screenmanager import ScreenManager, NoTransition, SlideTransition

        # Allow disabling transitions to improve responsiveness during automated tours
        no_transitions = os.environ.get("APP_NO_TRANSITION", "0").lower() in ("1", "true", "yes")
        if no_transitions:
            self.manager = ScreenManager(transition=NoTransition())
        else:
            self.manager = ScreenManager()
        self.root_layout.add_widget(self.manager)

        # Initialize ONLY essential screens immediately (IntroScreen, FirstUseScreen, LoginScreen)
        # Load others in background to reduce startup time
        self.intro_screen = IntroScreen(name="intro_screen")
        self.first_use_screen = FirstUseScreen(name="first_use_screen")
        self.login_screen = LoginScreen(name="login_screen")

        # Add essential screens to manager immediately
        self.manager.add_widget(self.intro_screen)
        self.manager.add_widget(self.first_use_screen)
        self.manager.add_widget(self.login_screen)

        # Bind screen change event to add/remove navigation drawers conditionally
        self.manager.bind(current=self.on_screen_change)

        # Start with intro screen immediately to avoid lag
        self.manager.current = "intro_screen"
        
        # Defer initialization of other screens to background thread (reduces startup by ~4s)
        Clock.schedule_once(lambda dt: self._load_remaining_screens(client), 0.1)

        # Add debug overlay if DEBUG_RESPONSIVE=1
        if os.environ.get("DEBUG_RESPONSIVE", "0") == "1":
            try:
                overlay = ResponsiveDebugOverlay()
                self.root_layout.add_widget(overlay)
                logger.info("✅ Responsive debug overlay enabled")
            except Exception as e:
                logger.warning(f"Failed to add debug overlay: {e}")

        return self.root_layout
    
    def _load_remaining_screens(self, client):
        """Load non-critical screens deferred to next frame to improve startup time"""
        if self._loading_screens or self._screens_loaded:
            return
        
        self._loading_screens = True
        
        # Initialize remaining screens (on main thread, but deferred)
        self.wallet_setup_screen = WalletSetupScreen(name="wallet_setup_screen")
        self.create_wallet_screen = CreateWalletScreen(name="create_wallet_screen")
        self.create_extrawallet_screen = CreateExtraWalletScreen(name="create_extrawallet_screen")
        self.importkeys_screen = ImportKeysScreen(name="importkeys_screen")
        self.importextrakeys_screen = ImportExtraKeysScreen(name="import_extra_keys_screen")
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
        self.add_trustline_screen = AddTrustlineScreen(name="add_trustline_screen")
        self.nftmint_screen = NFTMintScreen(name="nftmint_screen")
        self.createimportwallet_screen = CreateImportWalletScreen(name="createimportwallet_screen")
        self.dextrade_screen = DEXTradeScreen(name="dextrade_screen")
        self.foodtrack_screen = FoodTrackScreen(name="foodtrack_screen")
        self.barcode_scan_screen = BarcodeScanScreen(name="barcode_scan_screen")
        self.camera_scan_screen = CameraScanScreen(name="camera_scan_screen")
        self.settings_screen = SettingsScreen(name="settings_screen")
        
        if ENABLE_WEB3_BROWSER:
            self.web3_browser_screen = Web3BrowserScreen(name="web3_browser_screen")
            
        self.webview_screen = WebViewScreen(name="webview_screen")
        
        # Add screens to manager
        self._add_deferred_screens()
    
    def _add_deferred_screens(self):
        """Add deferred screens to manager (must run on main thread)"""
        try:
            self.manager.add_widget(self.wallet_setup_screen)
            self.manager.add_widget(self.create_wallet_screen)
            self.manager.add_widget(self.create_extrawallet_screen)
            self.manager.add_widget(self.importkeys_screen)
            self.manager.add_widget(self.importextrakeys_screen)
            self.manager.add_widget(self.mnemonic_display_screen)
            self.manager.add_widget(self.mnemonic_import_screen)
            self.manager.add_widget(self.account_choice_screen)
            self.manager.add_widget(self.import_choice_screen)
            self.manager.add_widget(self.keypair_import_screen)
            self.manager.add_widget(self.mnemonic_verify_screen)
            self.manager.add_widget(self.account_naming_screen)
            self.manager.add_widget(self.wallet_screen)
            self.manager.add_widget(self.sendxrp_screen)
            self.manager.add_widget(self.add_trustline_screen)
            self.manager.add_widget(self.nftmint_screen)
            self.manager.add_widget(self.createimportwallet_screen)
            self.manager.add_widget(self.dextrade_screen)
            self.manager.add_widget(self.foodtrack_screen)
            self.manager.add_widget(self.barcode_scan_screen)
            self.manager.add_widget(self.camera_scan_screen)
            self.manager.add_widget(self.settings_screen)
            
            if ENABLE_WEB3_BROWSER:
                self.manager.add_widget(self.web3_browser_screen)
                
            self.manager.add_widget(self.webview_screen)
            
            self._screens_loaded = True
            self._loading_screens = False
            logger.info("✅ Deferred screens loaded successfully (background optimization)")
        except Exception as e:
            logger.error(f"Failed to add deferred screens: {e}")
            self._loading_screens = False

    def on_start(self):
        if KeyboardShortcuts is not None:
            try:
                self.shortcuts = KeyboardShortcuts(self)
                self.shortcuts.enable()
                logger.info("✅ Global keyboard shortcuts enabled (Ctrl+Q, Ctrl+S, Ctrl+W, Esc)")
            except Exception as e:
                # Non-fatal: continue without shortcuts if something fails
                logger.warning(f"Could not enable keyboard shortcuts: {e}")
                self.shortcuts = None
        
        # Preload frequently accessed screens for better performance (guarded if import failed)
        try:
            from src.utils.performance import ScreenPreloader
            if ScreenPreloader:
                preloader = ScreenPreloader(self)
                preloader.preload()
                logger.info("✅ Frequently accessed screens preloaded")
            else:
                logger.warning("Screen preloading unavailable (ScreenPreloader is None)")
        except Exception as e:
            logger.warning(f"Screen preloading skipped: {e}")

    # --- Theme helpers ---
    def _load_theme_style(self) -> str:
        try:
            with shelve.open("wallet_data") as db:
                style = db.get(self._theme_pref_key, "Light")
                if style not in ("Light", "Dark"):
                    return "Light"
                return style
        except Exception:
            return "Light"

    def set_theme_style(self, style: str):
        """Set and persist theme style. Accepts 'Light' or 'Dark'."""
        if style not in ("Light", "Dark"):
            return
        try:
            with shelve.open("wallet_data") as db:
                db[self._theme_pref_key] = style
        except Exception:
            pass
        self.theme_cls.theme_style = style

    # --- Primary palette helpers ---
    def _load_primary_palette(self) -> str:
        try:
            with shelve.open("wallet_data") as db:
                palette = db.get(self._palette_pref_key, "Green")
                if palette not in ("Green", "Blue", "Teal"):
                    return "Green"
                return palette
        except Exception:
            return "Green"

    def set_primary_palette(self, palette: str):
        """Set and persist primary/accent palette. One of 'Green', 'Blue', 'Teal'."""
        if palette not in ("Green", "Blue", "Teal"):
            return
        try:
            with shelve.open("wallet_data") as db:
                db[self._palette_pref_key] = palette
        except Exception:
            pass
        self.theme_cls.primary_palette = palette
        self.theme_cls.accent_palette = palette

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

    def navigate_to_barcode_scan(self):
        """Navigate to barcode scan (pilot) screen"""
        self.manager.current = "barcode_scan_screen"

    def navigate_to_camera_scan(self):
        """Navigate to camera barcode scan (pilot) screen"""
        self.manager.current = "camera_scan_screen"

    def navigate_to_settings(self):
        """Navigate to settings screen"""
        self.manager.current = "settings_screen"

    def navigate_to_web3_browser(self):
        """Navigate to Web3 Browser screen (deferred)"""
        if ENABLE_WEB3_BROWSER:
            self.manager.current = "web3_browser_screen"
        else:
            print("Web3 browser feature deferred (flag disabled)")

    def navigate_to_webview(self):
        """Navigate to in-app WebView screen (feature flagged)"""
        self.manager.current = "webview_screen"

    # --- Wallet connection helpers ---
    def connect_wallet(self):
        if not self.wallet_connector.is_connected():
            self.wallet_connector.connect()

    def disconnect_wallet(self):
        if self.wallet_connector.is_connected():
            self.wallet_connector.disconnect()

    def get_wallet_session_info(self):
        return self.wallet_connector.get_session_info()

    def request_xaman_test_sign(self):
        # Dummy payload for future backend integration
        payload = {"tx_type": "SignTest", "network": "XRPL Testnet"}
        return self.wallet_connector.request_sign(payload)

    # --- CalorieDB ↔ XRPL linking helper ---
    def link_calorie_record_to_tx(self, record: dict, tx_hash: str):
        """Register a linkage between a calorie record and an XRPL transaction.

        This stub does NOT submit transactions; it only persists a mapping when
        CALORIE_LINKING_MODE is enabled. Real integration would attach a memo
        (see docs/CALORIE_LEDGER_LINKING.md) prior to submission.
        """
        if os.environ.get("CALORIE_LINKING_MODE") not in ("1", "true", "TRUE"):
            return False
        try:
            import json, hashlib, time
            from pathlib import Path
            links_path = Path("data") / "calorie_links.json"
            links_path.parent.mkdir(exist_ok=True)
            if links_path.exists():
                try:
                    existing = json.loads(links_path.read_text())
                    if not isinstance(existing, list):
                        existing = []
                except Exception:
                    existing = []
            else:
                existing = []
            # Canonical hash (sorted keys, no whitespace)
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
            record_hash = hashlib.sha256(canonical).hexdigest()
            existing.append({
                "tx_hash": tx_hash,
                "record_hash": record_hash,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "type": str(record.get("type", "unknown"))
            })
            links_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
            return True
        except Exception:
            return False

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
        try:
            if self.shortcuts:
                self.shortcuts.disable()
        except Exception:
            pass

# Backward compatibility alias expected by older tests/imports
class CalorieAppTestnetApp(CalorieAppTestnet):
    pass


if __name__ == "__main__":
    # Direct run path for standalone execution
    CalorieAppTestnet().run()
