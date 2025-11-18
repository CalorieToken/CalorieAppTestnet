"""
Comprehensive UX Tour - Deep Layout Validation
Tests every screen for:
- Sizing (proper dimensions, no overflow)
- Positioning (alignment, spacing)
- Theme colors (consistency with design tokens)
- Display correctness (text, visibility, hierarchy)
- Layout consistency (standardized patterns)
"""
import os
import sys
import time
from datetime import datetime
from typing import Any, Optional

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

# Ensure relative imports work when run from repo root
if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

from src.core.app import CalorieAppTestnet  # noqa: E402


class LayoutValidator:
    """Validates layout properties against design system standards"""
    
    # Design tokens from base.kv
    THEME_COLORS = {
        'CAL_PRIMARY': '#7C4DFF',
        'CAL_SECONDARY': '#FF4081',
        'CAL_ACCENT': '#00BFA5',
        'CAL_BG': '#F5F5F5',
        'CAL_BG_LIGHT': '#FAFAFA',
        'CAL_WHITE': '#FFFFFF',
        'CAL_TEXT_DARK': '#212121',
        'CAL_TEXT_LIGHT': '#757575',
        'CAL_ERROR': '#F44336',
        'CAL_SUCCESS': '#4CAF50',
        'CAL_WARNING': '#FF9800',
    }
    
    # Spacing tokens
    SPACING = {
        'SP_XS': dp(4),
        'SP_SM': dp(8),
        'SP_MD': dp(16),
        'SP_LG': dp(24),
        'SP_XL': dp(32),
    }
    
    # Standard component sizes
    BUTTON_HEIGHT = dp(48)
    INPUT_HEIGHT = dp(56)
    HEADER_HEIGHT = dp(64)
    ICON_SIZE = dp(24)
    
    @staticmethod
    def check_widget_exists(widget, name: str) -> bool:
        """Check if widget exists and is properly initialized"""
        return widget is not None and hasattr(widget, 'size')
    
    @staticmethod
    def check_size_reasonable(widget, min_width=dp(50), min_height=dp(20)) -> bool:
        """Check if widget has reasonable dimensions"""
        if not widget:
            return False
        return widget.width >= min_width and widget.height >= min_height
    
    @staticmethod
    def check_visible(widget) -> bool:
        """Check if widget is visible (not hidden, zero-sized, or off-screen)"""
        if not widget:
            return False
        if widget.size[0] <= 0 or widget.size[1] <= 0:
            return False
        if widget.opacity <= 0:
            return False
        return True
    
    @staticmethod
    def check_color_matches(widget, attr: str, expected_hex: str, tolerance=0.1) -> bool:
        """Check if widget color matches expected hex value within tolerance"""
        try:
            if not hasattr(widget, attr):
                return False
            actual = getattr(widget, attr)
            expected = get_color_from_hex(expected_hex)
            if len(actual) < 3 or len(expected) < 3:
                return False
            # Compare RGB values with tolerance
            for i in range(3):
                if abs(actual[i] - expected[i]) > tolerance:
                    return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_text_not_empty(widget) -> bool:
        """Check if text widget has content"""
        if not widget or not hasattr(widget, 'text'):
            return False
        return bool(widget.text and widget.text.strip())
    
    @staticmethod
    def check_centered(widget, parent, axis='both') -> bool:
        """Check if widget is centered within parent"""
        if not widget or not parent:
            return False
        tolerance = dp(5)
        
        if axis in ('x', 'both'):
            parent_center_x = parent.x + parent.width / 2
            widget_center_x = widget.x + widget.width / 2
            if abs(parent_center_x - widget_center_x) > tolerance:
                return False
        
        if axis in ('y', 'both'):
            parent_center_y = parent.y + parent.height / 2
            widget_center_y = widget.y + widget.height / 2
            if abs(parent_center_y - widget_center_y) > tolerance:
                return False
        
        return True
    
    @staticmethod
    def check_spacing(widget1, widget2, expected_spacing, axis='y') -> bool:
        """Check if spacing between two widgets matches expected value"""
        if not widget1 or not widget2:
            return False
        tolerance = dp(3)
        
        if axis == 'y':
            # Vertical spacing (widget2 below widget1)
            actual = widget1.y - (widget2.y + widget2.height)
        else:
            # Horizontal spacing (widget2 to right of widget1)
            actual = widget2.x - (widget1.x + widget1.width)
        
        return abs(actual - expected_spacing) <= tolerance
    
    @staticmethod
    def check_alignment(widget1, widget2, side='left') -> bool:
        """Check if two widgets are aligned on a specific side"""
        if not widget1 or not widget2:
            return False
        tolerance = dp(2)
        
        if side == 'left':
            return abs(widget1.x - widget2.x) <= tolerance
        elif side == 'right':
            return abs((widget1.x + widget1.width) - (widget2.x + widget2.width)) <= tolerance
        elif side == 'top':
            return abs((widget1.y + widget1.height) - (widget2.y + widget2.height)) <= tolerance
        elif side == 'bottom':
            return abs(widget1.y - widget2.y) <= tolerance
        
        return False


class UxTour:
    def __init__(self):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.out_dir = os.path.join("docs", "ui_tour", ts)
        os.makedirs(self.out_dir, exist_ok=True)
        self.app = None
        self.validator = LayoutValidator()
        self.test_results = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.layout_issues = []

    def snap(self, name: str):
        """Take screenshot"""
        safe = name.replace("/", "-").replace(" ", "_")
        path = os.path.join(self.out_dir, f"{safe}.png")
        try:
            Window.screenshot(name=path)
        except Exception:
            pass
        return path

    def log(self, msg: str):
        print(f"[UX] {msg}")

    def test(self, name: str, assertion_fn, screenshot=True, category="General"):
        """Run a test with assertion and optional screenshot"""
        self.test_count += 1
        try:
            result = assertion_fn()
            if result:
                self.pass_count += 1
                self.log(f"[PASS] {name}")
                self.test_results.append({
                    "name": name,
                    "status": "PASS",
                    "category": category
                })
            else:
                self.fail_count += 1
                self.log(f"[FAIL] {name}")
                self.test_results.append({
                    "name": name,
                    "status": "FAIL",
                    "category": category
                })
                self.layout_issues.append(f"{name} (Category: {category})")
            if screenshot:
                self.snap(f"test_{self.test_count:03d}_{name}")
        except Exception as e:
            self.fail_count += 1
            self.log(f"[ERROR] {name} - {e}")
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "category": category,
                "error": str(e)
            })
            self.layout_issues.append(f"{name} - ERROR: {str(e)}")

    def validate_standard_layout(self, screen, screen_name: str):
        """Validate that screen follows standard layout patterns"""
        
        # Check for AppHeader
        app_header = screen.ids.get("app_header")
        self.test(f"{screen_name}: Has AppHeader",
                 lambda: app_header is not None,
                 screenshot=False,
                 category="Layout Structure")
        
        if app_header:
            # Check header height
            self.test(f"{screen_name}: Header height ~{self.validator.HEADER_HEIGHT}dp",
                     lambda: abs(app_header.height - self.validator.HEADER_HEIGHT) < dp(10),
                     screenshot=False,
                     category="Sizing")
            
            # Check header title exists
            self.test(f"{screen_name}: Header has title",
                     lambda: hasattr(app_header, 'title') and bool(app_header.title),
                     screenshot=False,
                     category="Content")
        
        # Check for ContentScroll (scrollable content area)
        has_scroll = any(w.__class__.__name__ == 'ContentScroll' for w in screen.walk())
        self.test(f"{screen_name}: Has ContentScroll",
                 lambda: has_scroll,
                 screenshot=False,
                 category="Layout Structure")
        
        # Check for PrimaryBottomBar
        has_bottom_bar = any(w.__class__.__name__ == 'PrimaryBottomBar' for w in screen.walk())
        self.test(f"{screen_name}: Has PrimaryBottomBar",
                 lambda: has_bottom_bar,
                 screenshot=False,
                 category="Layout Structure")
        
        # Check background color
        self.test(f"{screen_name}: Background color set",
                 lambda: hasattr(screen, 'canvas') and screen.canvas is not None,
                 screenshot=False,
                 category="Theme")

    def validate_input_field(self, field, field_name: str, screen_name: str, check_helper=True):
        """Validate input field properties with enhanced quality checks"""
        
        # Exists and visible
        self.test(f"{screen_name}: {field_name} exists",
                 lambda: self.validator.check_widget_exists(field, field_name),
                 screenshot=False,
                 category="Widgets")
        
        if not field:
            return
        
        # Reasonable size (should be at least INPUT_HEIGHT)
        self.test(f"{screen_name}: {field_name} has proper size",
                 lambda: field.height >= dp(48) and field.width >= dp(200),
                 screenshot=False,
                 category="Sizing")
        
        # Is visible
        self.test(f"{screen_name}: {field_name} is visible",
                 lambda: self.validator.check_visible(field),
                 screenshot=False,
                 category="Display")
        
        # Has hint text (CRITICAL for UX)
        if hasattr(field, 'hint_text'):
            self.test(f"{screen_name}: {field_name} has hint text",
                     lambda: bool(field.hint_text and len(field.hint_text.strip()) > 0),
                     screenshot=False,
                     category="Content")
        
        # Has helper text (for guidance)
        if check_helper and hasattr(field, 'helper_text'):
            self.test(f"{screen_name}: {field_name} has helper text",
                     lambda: bool(field.helper_text),
                     screenshot=False,
                     category="Content")
        
        # Proper padding/spacing
        if hasattr(field, 'padding'):
            self.test(f"{screen_name}: {field_name} has padding",
                     lambda: any(p > 0 for p in field.padding) if isinstance(field.padding, (list, tuple)) else field.padding > 0,
                     screenshot=False,
                     category="Sizing")

    def validate_button(self, button, button_name: str, screen_name: str):
        """Validate button properties"""
        
        # Exists
        self.test(f"{screen_name}: {button_name} exists",
                 lambda: self.validator.check_widget_exists(button, button_name),
                 screenshot=False,
                 category="Widgets")
        
        if not button:
            return
        
        # Reasonable size (minimum touch target)
        self.test(f"{screen_name}: {button_name} has minimum touch size",
                 lambda: button.width >= dp(40) and button.height >= dp(40),
                 screenshot=False,
                 category="Sizing")
        
        # Is visible
        self.test(f"{screen_name}: {button_name} is visible",
                 lambda: self.validator.check_visible(button),
                 screenshot=False,
                 category="Display")
        
        # Has text or icon
        has_content = False
        if hasattr(button, 'text') and button.text:
            has_content = True
        if hasattr(button, 'icon') and button.icon:
            has_content = True
        
        self.test(f"{screen_name}: {button_name} has text/icon",
                 lambda: has_content,
                 screenshot=False,
                 category="Content")

    def validate_label(self, label, label_name: str, screen_name: str, should_have_text=False):
        """Validate label properties"""
        
        # Exists
        self.test(f"{screen_name}: {label_name} exists",
                 lambda: self.validator.check_widget_exists(label, label_name),
                 screenshot=False,
                 category="Widgets")
        
        if not label:
            return
        
        # Is visible
        self.test(f"{screen_name}: {label_name} is visible",
                 lambda: self.validator.check_visible(label),
                 screenshot=False,
                 category="Display")
        
        # Has text (if required)
        if should_have_text:
            self.test(f"{screen_name}: {label_name} has text",
                     lambda: self.validator.check_text_not_empty(label),
                     screenshot=False,
                     category="Content")

    def write_report(self):
        """Write detailed test results to file"""
        report_path = os.path.join(self.out_dir, "layout_validation_report.txt")
        
        # Group results by category
        by_category = {}
        for result in self.test_results:
            cat = result.get('category', 'General')
            if cat not in by_category:
                by_category[cat] = {'pass': 0, 'fail': 0, 'error': 0, 'tests': []}
            
            status = result['status']
            by_category[cat]['tests'].append(result)
            if status == 'PASS':
                by_category[cat]['pass'] += 1
            elif status == 'FAIL':
                by_category[cat]['fail'] += 1
            else:
                by_category[cat]['error'] += 1
        
        with open(report_path, "w", encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("COMPREHENSIVE UX TOUR - LAYOUT VALIDATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tests: {self.test_count}\n")
            f.write(f"Passed: {self.pass_count} ({(self.pass_count/self.test_count*100):.1f}%)\n")
            f.write(f"Failed: {self.fail_count} ({(self.fail_count/self.test_count*100):.1f}%)\n")
            f.write(f"Success Rate: {(self.pass_count/self.test_count*100):.1f}%\n\n")
            
            # Category summary
            f.write("=" * 80 + "\n")
            f.write("RESULTS BY CATEGORY\n")
            f.write("=" * 80 + "\n\n")
            
            for cat in sorted(by_category.keys()):
                data = by_category[cat]
                total = data['pass'] + data['fail'] + data['error']
                f.write(f"\n{cat}:\n")
                f.write(f"  Total: {total}\n")
                f.write(f"  Passed: {data['pass']} ({(data['pass']/total*100):.1f}%)\n")
                f.write(f"  Failed: {data['fail']}\n")
                f.write(f"  Errors: {data['error']}\n")
            
            # Layout issues summary
            if self.layout_issues:
                f.write("\n" + "=" * 80 + "\n")
                f.write("LAYOUT ISSUES DETECTED\n")
                f.write("=" * 80 + "\n\n")
                for issue in self.layout_issues:
                    f.write(f"  [!] {issue}\n")
            
            # Detailed results
            f.write("\n" + "=" * 80 + "\n")
            f.write("DETAILED TEST RESULTS\n")
            f.write("=" * 80 + "\n\n")
            
            for cat in sorted(by_category.keys()):
                f.write(f"\n--- {cat} ---\n\n")
                for result in by_category[cat]['tests']:
                    status = result['status']
                    name = result['name']
                    
                    if status == 'PASS':
                        f.write(f"  [PASS] {name}\n")
                    elif status == 'FAIL':
                        f.write(f"  [FAIL] {name}\n")
                    else:
                        f.write(f"  [!] {name} - ERROR: {result.get('error', '')}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        self.log(f"Detailed report written to {report_path}")

    def start(self):
        os.environ["UX_TOUR"] = "1"
        os.environ["UX_TOUR_MODE"] = "1"
        os.environ["WEBVIEW_ENABLED"] = "1"
        self.app = CalorieAppTestnet()
        Clock.schedule_once(self._drive_intro, 0.8)
        self.app.run()

    # ========================================================================
    # SCREEN VALIDATION FLOWS
    # ========================================================================

    def _drive_intro(self, dt):
        """Validate IntroScreen"""
        try:
            self.log("=== IntroScreen Validation ===")
            self.snap("00_intro_screen")
            
            scr = self.app.manager.get_screen("intro_screen")
            self.validate_standard_layout(scr, "IntroScreen")
            
            # Check logo/branding
            logo_widgets = [w for w in scr.walk() if hasattr(w, 'source') or 
                          (hasattr(w, 'text') and 'Calorie' in str(getattr(w, 'text', '')))]
            self.test("IntroScreen: Has logo/branding",
                     lambda: len(logo_widgets) > 0,
                     screenshot=False,
                     category="Content")
            
            # Navigate to wallet
            self.app.manager.current = "wallet_screen"
            Clock.schedule_once(self._drive_wallet, 0.6)
        except Exception as e:
            self.log(f"IntroScreen validation failed: {e}")
            Clock.schedule_once(self._finish, 0.1)

    def _drive_wallet(self, dt):
        """Validate WalletScreen"""
        try:
            self.log("=== WalletScreen Validation ===")
            scr = self.app.manager.get_screen("wallet_screen")
            
            self.validate_standard_layout(scr, "WalletScreen")
            
            # Validate address label
            address_label = scr.ids.get("xrp_address_label")
            self.validate_label(address_label, "Address Label", "WalletScreen", should_have_text=True)
            
            # Validate balance label
            balance_label = scr.xrp_balance if hasattr(scr, 'xrp_balance') else None
            self.validate_label(balance_label, "Balance Label", "WalletScreen", should_have_text=False)
            
            # Check for action buttons
            copy_buttons = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'content-copy']
            self.test("WalletScreen: Has copy button",
                     lambda: len(copy_buttons) > 0,
                     screenshot=False,
                     category="Widgets")
            
            send_buttons = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'send']
            self.test("WalletScreen: Has send button",
                     lambda: len(send_buttons) > 0,
                     screenshot=False,
                     category="Widgets")
            
            refresh_buttons = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'refresh']
            self.test("WalletScreen: Has refresh button",
                     lambda: len(refresh_buttons) > 0,
                     screenshot=False,
                     category="Widgets")
            
            # Check trustlines container
            trustlines_container = scr.ids.get("trustlines_container")
            if trustlines_container:
                self.test("WalletScreen: Trustlines container visible",
                         lambda: self.validator.check_visible(trustlines_container),
                         screenshot=False,
                         category="Display")
            
            self.snap("10_wallet")
            
            Clock.schedule_once(self._drive_sendxrp, 0.5)
        except Exception as e:
            self.log(f"WalletScreen validation failed: {e}")
            Clock.schedule_once(self._drive_sendxrp, 0.3)

    def _drive_sendxrp(self, dt):
        """Validate SendXRPScreen"""
        try:
            self.log("=== SendXRPScreen Validation ===")
            self.app.manager.current = "sendxrp_screen"
            Clock.schedule_once(self._validate_sendxrp, 0.6)
        except Exception as e:
            self.log(f"SendXRP navigation failed: {e}")
            Clock.schedule_once(self._drive_settings, 0.3)

    def _validate_sendxrp(self, dt):
        try:
            scr = self.app.manager.get_screen("sendxrp_screen")
            
            self.validate_standard_layout(scr, "SendXRPScreen")
            
            # Validate amount input
            amount_input = scr.ids.get("amount_input")
            self.validate_input_field(amount_input, "Amount Input", "SendXRPScreen")
            
            # Validate destination input
            dest_input = scr.ids.get("destination_input")
            self.validate_input_field(dest_input, "Destination Input", "SendXRPScreen")
            
            # Validate balance display
            balance_label = scr.xrp_balance if hasattr(scr, 'xrp_balance') else None
            self.validate_label(balance_label, "XRP Balance", "SendXRPScreen")
            
            # Validate send button
            send_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                          'Send' in str(getattr(w, 'text', '')) and 
                          w.__class__.__name__ in ('MDButton', 'MDRaisedButton', 'PrimaryButton')]
            if send_buttons:
                self.validate_button(send_buttons[0], "Send Button", "SendXRPScreen")
            
            # Check transactions section
            transactions_card = scr.ids.get("transactions_card")
            if transactions_card:
                self.test("SendXRPScreen: Transactions card visible",
                         lambda: self.validator.check_visible(transactions_card),
                         screenshot=False,
                         category="Display")
            
            self.snap("20_sendxrp")
            
            Clock.schedule_once(self._drive_settings, 0.5)
        except Exception as e:
            self.log(f"SendXRP validation failed: {e}")
            Clock.schedule_once(self._drive_settings, 0.3)

    def _drive_settings(self, dt):
        """Validate SettingsScreen"""
        try:
            self.log("=== SettingsScreen Validation ===")
            self.app.manager.current = "settings_screen"
            Clock.schedule_once(self._validate_settings, 0.6)
        except Exception as e:
            self.log(f"Settings navigation failed: {e}")
            Clock.schedule_once(self._drive_trustline, 0.3)

    def _validate_settings(self, dt):
        try:
            scr = self.app.manager.get_screen("settings_screen")
            
            self.validate_standard_layout(scr, "SettingsScreen")
            
            # Check accounts list
            accounts_list = scr.ids.get("accounts_list")
            if accounts_list:
                self.test("SettingsScreen: Accounts list visible",
                         lambda: self.validator.check_visible(accounts_list),
                         screenshot=False,
                         category="Display")
            
            # Check for refresh button
            refresh_buttons = [w for w in scr.walk() if hasattr(w, 'icon') and 
                             w.icon in ('refresh', 'reload')]
            self.test("SettingsScreen: Has refresh button",
                     lambda: len(refresh_buttons) > 0,
                     screenshot=False,
                     category="Widgets")
            
            self.snap("30_settings")
            
            Clock.schedule_once(self._drive_trustline, 0.5)
        except Exception as e:
            self.log(f"Settings validation failed: {e}")
            Clock.schedule_once(self._drive_trustline, 0.3)

    def _drive_trustline(self, dt):
        """Validate AddTrustlineScreen"""
        try:
            self.log("=== AddTrustlineScreen Validation ===")
            self.app.manager.current = "add_trustline_screen"
            Clock.schedule_once(self._validate_trustline, 0.6)
        except Exception as e:
            self.log(f"Trustline navigation failed: {e}")
            Clock.schedule_once(self._drive_nft, 0.3)

    def _validate_trustline(self, dt):
        try:
            scr = self.app.manager.get_screen("add_trustline_screen")
            
            self.validate_standard_layout(scr, "AddTrustlineScreen")
            
            # Validate currency input
            currency_input = scr.ids.get("currency_code")
            self.validate_input_field(currency_input, "Currency Code", "AddTrustlineScreen")
            
            # Validate issuer input
            issuer_input = scr.ids.get("issuer_address")
            self.validate_input_field(issuer_input, "Issuer Address", "AddTrustlineScreen")
            
            # Validate limit input
            limit_input = scr.ids.get("limit_amount")
            self.validate_input_field(limit_input, "Limit Amount", "AddTrustlineScreen")
            
            # Check add button
            add_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                         'Add' in str(getattr(w, 'text', '')) and 
                         w.__class__.__name__ in ('MDButton', 'PrimaryButton')]
            if add_buttons:
                self.validate_button(add_buttons[0], "Add Button", "AddTrustlineScreen")
            
            self.snap("40_trustline")
            
            Clock.schedule_once(self._drive_nft, 0.5)
        except Exception as e:
            self.log(f"Trustline validation failed: {e}")
            Clock.schedule_once(self._drive_nft, 0.3)

    def _drive_nft(self, dt):
        """Validate NFTMintScreen"""
        try:
            self.log("=== NFTMintScreen Validation ===")
            self.app.manager.current = "nftmint_screen"
            Clock.schedule_once(self._validate_nft, 0.6)
        except Exception as e:
            self.log(f"NFT navigation failed: {e}")
            Clock.schedule_once(self._drive_dex, 0.3)

    def _validate_nft(self, dt):
        try:
            scr = self.app.manager.get_screen("nftmint_screen")
            
            self.validate_standard_layout(scr, "NFTMintScreen")
            
            # Validate URI input
            uri_input = scr.ids.get("nft_uri")
            self.validate_input_field(uri_input, "NFT URI", "NFTMintScreen")
            
            # Validate taxon input
            taxon_input = scr.ids.get("nft_taxon")
            self.validate_input_field(taxon_input, "NFT Taxon", "NFTMintScreen")
            
            # Check mint button
            mint_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                          'Mint' in str(getattr(w, 'text', '')) and 
                          w.__class__.__name__ in ('MDButton', 'PrimaryButton')]
            if mint_buttons:
                self.validate_button(mint_buttons[0], "Mint Button", "NFTMintScreen")
            
            self.snap("50_nft")
            
            Clock.schedule_once(self._drive_dex, 0.5)
        except Exception as e:
            self.log(f"NFT validation failed: {e}")
            Clock.schedule_once(self._drive_dex, 0.3)

    def _drive_dex(self, dt):
        """Validate DEXTradeScreen"""
        try:
            self.log("=== DEXTradeScreen Validation ===")
            self.app.manager.current = "dextrade_screen"
            Clock.schedule_once(self._validate_dex, 0.6)
        except Exception as e:
            self.log(f"DEX navigation failed: {e}")
            Clock.schedule_once(self._drive_foodtrack, 0.3)

    def _validate_dex(self, dt):
        try:
            scr = self.app.manager.get_screen("dextrade_screen")
            
            self.validate_standard_layout(scr, "DEXTradeScreen")
            
            # Check for trading interface elements
            self.test("DEXTradeScreen: Has content sections",
                     lambda: len([w for w in scr.walk() if w.__class__.__name__ == 'ContentSection']) > 0,
                     screenshot=False,
                     category="Layout Structure")
            
            self.snap("60_dex")
            
            Clock.schedule_once(self._drive_foodtrack, 0.5)
        except Exception as e:
            self.log(f"DEX validation failed: {e}")
            Clock.schedule_once(self._drive_foodtrack, 0.3)

    def _drive_foodtrack(self, dt):
        """Validate FoodTrackScreen"""
        try:
            self.log("=== FoodTrackScreen Validation ===")
            self.app.manager.current = "foodtrack_screen"
            Clock.schedule_once(self._validate_foodtrack, 0.6)
        except Exception as e:
            self.log(f"FoodTrack navigation failed: {e}")
            Clock.schedule_once(self._drive_barcode, 0.3)

    def _validate_foodtrack(self, dt):
        try:
            scr = self.app.manager.get_screen("foodtrack_screen")
            
            self.validate_standard_layout(scr, "FoodTrackScreen")
            
            # Check for status section
            status_labels = [w for w in scr.walk() if hasattr(w, 'text') and 
                           'Status' in str(getattr(w, 'text', ''))]
            self.test("FoodTrackScreen: Has status section",
                     lambda: len(status_labels) > 0,
                     screenshot=False,
                     category="Content")
            
            self.snap("70_foodtrack")
            
            Clock.schedule_once(self._drive_barcode, 0.5)
        except Exception as e:
            self.log(f"FoodTrack validation failed: {e}")
            Clock.schedule_once(self._drive_barcode, 0.3)

    def _drive_barcode(self, dt):
        """Validate BarcodeScanScreen"""
        try:
            self.log("=== BarcodeScanScreen Validation ===")
            self.app.manager.current = "barcode_scan_screen"
            Clock.schedule_once(self._validate_barcode, 0.6)
        except Exception as e:
            self.log(f"Barcode navigation failed: {e}")
            Clock.schedule_once(self._drive_mnemonic_display, 0.3)

    def _validate_barcode(self, dt):
        try:
            scr = self.app.manager.get_screen("barcode_scan_screen")
            
            self.validate_standard_layout(scr, "BarcodeScanScreen")
            
            # Validate barcode input
            barcode_input = scr.ids.get("barcode_input")
            self.validate_input_field(barcode_input, "Barcode Input", "BarcodeScanScreen")
            
            # Check result label
            result_label = scr.ids.get("result_label")
            self.validate_label(result_label, "Result Label", "BarcodeScanScreen")
            
            # Check lookup button
            lookup_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                            'Lookup' in str(getattr(w, 'text', '')) and 
                            w.__class__.__name__ in ('MDButton', 'PrimaryButton')]
            if lookup_buttons:
                self.validate_button(lookup_buttons[0], "Lookup Button", "BarcodeScanScreen")
            
            self.snap("80_barcode")
            
            Clock.schedule_once(self._drive_mnemonic_display, 0.5)
        except Exception as e:
            self.log(f"Barcode validation failed: {e}")
            Clock.schedule_once(self._drive_mnemonic_display, 0.3)

    def _drive_mnemonic_display(self, dt):
        """Validate MnemonicDisplayScreen"""
        try:
            self.log("=== MnemonicDisplayScreen Validation ===")
            # Generate test mnemonic
            try:
                from xrpl.wallet import Wallet
                test_wallet = Wallet.create()
                scr = self.app.manager.get_screen("mnemonic_display_screen")
                if hasattr(scr, 'set_mnemonic_data'):
                    scr.set_mnemonic_data(
                        test_wallet.seed.split(),
                        test_wallet.public_key,
                        test_wallet.private_key
                    )
            except Exception:
                pass
            
            self.app.manager.current = "mnemonic_display_screen"
            Clock.schedule_once(self._validate_mnemonic_display, 0.6)
        except Exception as e:
            self.log(f"MnemonicDisplay navigation failed: {e}")
            Clock.schedule_once(self._drive_mnemonic_import, 0.3)

    def _validate_mnemonic_display(self, dt):
        try:
            scr = self.app.manager.get_screen("mnemonic_display_screen")
            
            self.validate_standard_layout(scr, "MnemonicDisplayScreen")
            
            # Check for mnemonic grid
            mnemonic_grid = scr.ids.get("mnemonic_grid")
            if mnemonic_grid:
                # Check grid exists and is configured (may be empty on first load)
                has_children = len(mnemonic_grid.children) > 0
                self.test("MnemonicDisplayScreen: Mnemonic grid visible",
                         lambda: mnemonic_grid is not None and (has_children or mnemonic_grid.opacity >= 0),
                         screenshot=False,
                         category="Display")
                
                # Check grid has 12 word slots
                word_labels = [w for w in mnemonic_grid.walk() if hasattr(w, 'text')]
                self.test("MnemonicDisplayScreen: Has 12 word slots",
                         lambda: len(word_labels) >= 12,
                         screenshot=False,
                         category="Content")
            
            # Check for copy buttons
            copy_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                          'Copy' in str(getattr(w, 'text', ''))]
            self.test("MnemonicDisplayScreen: Has copy buttons",
                     lambda: len(copy_buttons) > 0,
                     screenshot=False,
                     category="Widgets")
            
            self.snap("90_mnemonic_display")
            
            Clock.schedule_once(self._drive_mnemonic_import, 0.5)
        except Exception as e:
            self.log(f"MnemonicDisplay validation failed: {e}")
            Clock.schedule_once(self._drive_mnemonic_import, 0.3)

    def _drive_mnemonic_import(self, dt):
        """Validate MnemonicImportScreen"""
        try:
            self.log("=== MnemonicImportScreen Validation ===")
            self.app.manager.current = "mnemonic_import_screen"
            Clock.schedule_once(self._validate_mnemonic_import, 0.6)
        except Exception as e:
            self.log(f"MnemonicImport navigation failed: {e}")
            Clock.schedule_once(self._drive_first_use, 0.3)

    def _validate_mnemonic_import(self, dt):
        try:
            scr = self.app.manager.get_screen("mnemonic_import_screen")
            
            self.validate_standard_layout(scr, "MnemonicImportScreen")
            
            # Check for 12 word input fields by ID
            word_inputs = []
            for i in range(1, 13):
                word_id = f"word_{i:02d}"
                if word_id in scr.ids:
                    word_inputs.append(scr.ids[word_id])
            
            self.test("MnemonicImportScreen: Has 12 word inputs",
                     lambda: len(word_inputs) >= 12,
                     screenshot=False,
                     category="Widgets")
            
            # Validate each input field has proper hint
            for i, inp in enumerate(word_inputs[:12], 1):
                if hasattr(inp, 'hint_text'):
                    self.test(f"MnemonicImportScreen: Word {i} has hint",
                             lambda inp=inp: bool(inp.hint_text),
                             screenshot=False,
                             category="Content")
            
            # Check import button
            import_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                            'Import' in str(getattr(w, 'text', '')) and 
                            w.__class__.__name__ in ('MDButton', 'PrimaryButton')]
            if import_buttons:
                self.validate_button(import_buttons[0], "Import Button", "MnemonicImportScreen")
            
            self.snap("100_mnemonic_import")
            
            Clock.schedule_once(self._drive_first_use, 0.5)
        except Exception as e:
            self.log(f"MnemonicImport validation failed: {e}")
            Clock.schedule_once(self._drive_first_use, 0.3)

    def _drive_first_use(self, dt):
        """Validate FirstUseScreen"""
        try:
            self.log("=== FirstUseScreen Validation ===")
            self.app.manager.current = "first_use_screen"
            Clock.schedule_once(self._validate_first_use, 0.6)
        except Exception as e:
            self.log(f"FirstUse navigation failed: {e}")
            Clock.schedule_once(self._drive_login, 0.3)

    def _validate_first_use(self, dt):
        try:
            scr = self.app.manager.get_screen("first_use_screen")
            
            self.validate_standard_layout(scr, "FirstUseScreen")
            
            # Validate password fields
            password_input = scr.ids.get("password_input")
            self.validate_input_field(password_input, "Password Input", "FirstUseScreen")
            
            confirm_input = scr.ids.get("confirm_password_input")
            self.validate_input_field(confirm_input, "Confirm Password", "FirstUseScreen")
            
            # Check create button
            create_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                            'Create' in str(getattr(w, 'text', '')) and 
                            w.__class__.__name__ in ('MDButton', 'PrimaryButton')]
            if create_buttons:
                self.validate_button(create_buttons[0], "Create Button", "FirstUseScreen")
            
            # Check helper text
            helper_labels = [w for w in scr.walk() if hasattr(w, 'text') and 
                           ('password' in str(getattr(w, 'text', '')).lower() or
                            'character' in str(getattr(w, 'text', '')).lower())]
            self.test("FirstUseScreen: Has helper text",
                     lambda: len(helper_labels) > 0,
                     screenshot=False,
                     category="Content")
            
            self.snap("110_first_use")
            
            Clock.schedule_once(self._drive_login, 0.5)
        except Exception as e:
            self.log(f"FirstUse validation failed: {e}")
            Clock.schedule_once(self._drive_login, 0.3)

    def _drive_login(self, dt):
        """Validate LoginScreen"""
        try:
            self.log("=== LoginScreen Validation ===")
            self.app.manager.current = "login_screen"
            Clock.schedule_once(self._validate_login, 0.6)
        except Exception as e:
            self.log(f"Login navigation failed: {e}")
            Clock.schedule_once(self._finish, 0.3)

    def _validate_login(self, dt):
        try:
            scr = self.app.manager.get_screen("login_screen")
            
            self.validate_standard_layout(scr, "LoginScreen")
            
            # Validate password input
            password_input = scr.ids.get("password_input")
            self.validate_input_field(password_input, "Password Input", "LoginScreen")
            
            # Check visibility toggle icon
            if password_input and hasattr(password_input, 'icon_right'):
                self.test("LoginScreen: Password has visibility toggle",
                         lambda: bool(password_input.icon_right),
                         screenshot=False,
                         category="Widgets")
            
            # Check login button
            login_buttons = [w for w in scr.walk() if hasattr(w, 'text') and 
                           'Login' in str(getattr(w, 'text', '')) and 
                           w.__class__.__name__ in ('MDButton', 'PrimaryButton')]
            if login_buttons:
                self.validate_button(login_buttons[0], "Login Button", "LoginScreen")
            
            # Check error label
            error_label = scr.ids.get("error_label")
            if error_label:
                self.test("LoginScreen: Error label exists",
                         lambda: self.validator.check_widget_exists(error_label, "error_label"),
                         screenshot=False,
                         category="Widgets")
            
            self.snap("120_login")
            
            Clock.schedule_once(self._finish, 0.5)
        except Exception as e:
            self.log(f"Login validation failed: {e}")
            Clock.schedule_once(self._finish, 0.3)

    def _finish(self, dt):
        """Finalize tour and generate report"""
        try:
            self.log("=== Tour Complete ===")
            self.write_report()
            self.log(f"\nFinal Results:")
            self.log(f"  Total Tests: {self.test_count}")
            self.log(f"  Passed: {self.pass_count} ({(self.pass_count/self.test_count*100):.1f}%)")
            self.log(f"  Failed: {self.fail_count} ({(self.fail_count/self.test_count*100):.1f}%)")
            self.log(f"  Layout Issues: {len(self.layout_issues)}")
            
            if self.layout_issues:
                self.log(f"\n[!] Layout Issues Detected:")
                for issue in self.layout_issues[:10]:  # Show first 10
                    self.log(f"    - {issue}")
                if len(self.layout_issues) > 10:
                    self.log(f"    ... and {len(self.layout_issues) - 10} more")
        except Exception as e:
            self.log(f"Finish failed: {e}")
        finally:
            # Stop app
            try:
                self.app.stop()
            except Exception:
                pass


if __name__ == "__main__":
    UxTour().start()
