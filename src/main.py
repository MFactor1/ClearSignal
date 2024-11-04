import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.clock import Clock

BUTTON_BASE = [93/255, 93/255, 93/255, 0.8]
YES_ACTV = [145/255, 255/255, 121/255, 0.8]
NO_ACTV = [255/255, 121/255, 121/255, 0.8]
LINGER_TM = 3

class YesBtn(Widget):
    active = False
    color = ListProperty(BUTTON_BASE)

    def actv(self):
        self.active = True
        self.color = YES_ACTV
        self.active_time = time.time()

    def deac(self):
        self.active = False
        self.color = BUTTON_BASE

    def update(self):
        if self.active:
            if time.time() - self.active_time > LINGER_TM:
                self.deac()


class NoBtn(Widget):
    active = False
    color = ListProperty(BUTTON_BASE)

    def actv(self):
        self.active = True
        self.color = NO_ACTV
        self.active_time = time.time()

    def deac(self):
        self.active = False
        self.color = BUTTON_BASE

    def update(self):
        if self.active:
            if time.time() - self.active_time > LINGER_TM:
                self.deac()

class CommWnd(Widget):
    kp = ObjectProperty(None)
    yes = ObjectProperty(None)
    no = ObjectProperty(None)
    yes_key = 1073742097
    no_key = 281

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        try:
            char = chr(key)
        except ValueError:
            char = "Unknown"
        self.kp.text = f"pressed '{char}' ({key})"
        if key == self.yes_key:
            self.yes.actv()
        elif key == self.no_key:
            self.no.actv()

    def update(self, dt):
        self.yes.update()
        self.no.update()

class CommApp(App):
    def build(self):
        wnd = CommWnd()
        Window.bind(on_key_down=wnd.on_key_down)
        Clock.schedule_interval(wnd.update, 1.0/10)
        return wnd

if __name__ == "__main__":
    CommApp().run()
