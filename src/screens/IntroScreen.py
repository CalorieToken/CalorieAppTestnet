# Kivy libraries for the GUI.
import logging
import shelve
import threading

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from src.utils.storage_paths import WALLET_DATA_PATH


# Intro Screen
class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._wallet_check_done = False
        self._has_password = False
        
    def on_pre_enter(self):
        """Pre-check wallet in background before screen displays"""
        # Start wallet check in background thread (non-blocking)
        threading.Thread(target=self._check_wallet_background, daemon=True).start()
        
    def on_enter(self):
        """Prepare screen for display with VERY DRAMATIC animated welcome"""
        self.opacity = 1
        
        # Get all animated elements
        logo_box = self.ids.get('logo_box')
        title_box = self.ids.get('title_box')
        subtitle1_box = self.ids.get('subtitle1_box')
        subtitle2_box = self.ids.get('subtitle2_box')
        version_box = self.ids.get('version_box')
        button = self.ids.get('start_button')
        
        # Logo: HUGE DROP from above with massive bounce
        if logo_box:
            logo_box.opacity = 0
            original_y = logo_box.y
            logo_box.y = original_y + 800  # Start way above screen
            anim = Animation(opacity=1, y=original_y, duration=2.0, t='out_bounce')
            anim.start(logo_box)
        
        # Title: SLIDE in from FAR LEFT with overshoot
        if title_box:
            title_box.opacity = 0
            original_x = title_box.x
            title_box.x = -800  # Start far off screen left
            anim = Animation(opacity=1, x=original_x, duration=1.5, t='out_back')
            Clock.schedule_once(lambda dt: anim.start(title_box), 0.8)
            
        # Subtitle 1: ZOOM in from RIGHT
        if subtitle1_box:
            subtitle1_box.opacity = 0
            original_x = subtitle1_box.x
            subtitle1_box.x = 800  # Start far off screen right
            anim = Animation(opacity=1, x=original_x, duration=1.3, t='out_elastic')
            Clock.schedule_once(lambda dt: anim.start(subtitle1_box), 1.5)
            
        # Subtitle 2: ZOOM in from LEFT
        if subtitle2_box:
            subtitle2_box.opacity = 0
            original_x = subtitle2_box.x
            subtitle2_box.x = -800
            anim = Animation(opacity=1, x=original_x, duration=1.3, t='out_elastic')
            Clock.schedule_once(lambda dt: anim.start(subtitle2_box), 2.0)
            
        # Version: POP UP from bottom
        if version_box:
            version_box.opacity = 0
            original_y = version_box.y
            version_box.y = -400
            anim = Animation(opacity=1, y=original_y, duration=1.0, t='out_back')
            Clock.schedule_once(lambda dt: anim.start(version_box), 2.5)
            
        # Button: MASSIVE BOUNCE from bottom
        if button:
            button.opacity = 0
            original_y = button.y
            button.y = -600  # Start way below screen
            anim = Animation(opacity=1, y=original_y, duration=1.8, t='out_bounce')
            Clock.schedule_once(lambda dt: anim.start(button), 3.0)
            Clock.schedule_once(lambda dt: anim.start(button), 1.5)
        
    def _check_wallet_background(self):
        """Check for existing wallet in background thread"""
        try:
            with shelve.open(WALLET_DATA_PATH) as wallet_data:
                self._has_password = "password" in wallet_data
        except Exception as e:
            logging.debug(f"No wallet_data found: {e}")
            self._has_password = False
        finally:
            self._wallet_check_done = True
    
    def next(self):
        """Handle next button click - route based on pre-checked wallet status"""
        # Wait for background check if not done (should be instant)
        if not self._wallet_check_done:
            Clock.schedule_once(lambda dt: self.next(), 0.1)
            return
            
        if self._has_password:
            # Existing wallet found - go to login screen
            self.manager.current = "login_screen"
        else:
            # No password found - go to first use screen
            self.manager.current = "first_use_screen"
