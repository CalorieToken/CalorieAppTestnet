# Kivy libraries for the GUI.
from kivy.uix.screenmanager import Screen

# Intro Screen
class IntroScreen(Screen):
    def next(self):
        self.manager.current = "first_use_screen"