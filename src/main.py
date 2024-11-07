import time
from enum import Enum

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.core.window import Window

BUTTON_BASE = [50/255, 50/255, 50/255, 0.8]
INI = dict()
ini_error = False
ini_error_msg = None

class Toks(Enum):
    YES_ACTV = "yes_button_colour"
    NO_ACTV = "no_button_colour"
    CUSTOM_ACTV = "custom_button_colour"
    YES_TXT = "yes_button_text"
    NO_TXT = "no_button_text"
    CUSTOM_TXT = "custom_button_text"
    YES_MAP = "yes_button_map"
    NO_MAP = "no_button_map"
    CUSTOM_MAP = "custom_button_map"
    HEADER_TXT = "header_text"
    FADE_TM = "button_fade_time"
    DEBUG = "debug_mode"

class Indicator(Widget):
    color = ListProperty([1,1,1,1])

    def __init__(self, actv_clr, *args, **kwargs):
        self.active = False
        self.color = BUTTON_BASE
        self.active_colour = actv_clr
        super().__init__(*args, **kwargs)

    def actv(self):
        self.active = True
        self.color = self.active_colour
        self.active_time = time.time()

    def deac(self):
        self.active = False
        self.color = BUTTON_BASE

    def update(self):
        if self.active:
            elapsed = time.time() - self.active_time
            if elapsed > INI[Toks.FADE_TM]:
                self.deac()
            else:
                mult = elapsed / INI[Toks.FADE_TM]
                new = [self.active_colour[i] + ((BUTTON_BASE[i] - self.active_colour[i]) * ((5 ** mult) / 4 - 0.25)) for i in range(4)]
                self.color = new


class YesBtn(Indicator):
    def __init__(self, *args, **kwargs):
        self.text = INI[Toks.YES_TXT]
        super().__init__(INI[Toks.YES_ACTV], *args, **kwargs)

class NoBtn(Indicator):
    def __init__(self, *args, **kwargs):
        self.text = INI[Toks.NO_TXT]
        super().__init__(INI[Toks.NO_ACTV], *args, **kwargs)

class CustomBtn(Indicator):
    def __init__(self, *args, **kwargs):
        self.text = INI[Toks.CUSTOM_TXT]
        super().__init__(INI[Toks.CUSTOM_ACTV], *args, **kwargs)

class Initializer():

    def readIni(self):
        global ini_error
        global ini_error_msg
        self.load_defaults()

        with open('comm.ini', 'r') as ini:
            lines = ini.readlines()

        for i, line in enumerate(lines):
            if line.strip() == '':
                continue
            if line.strip().startswith('#'):
                continue
            try:
                tok_text, val = line.split(':', maxsplit=1)

                tok_text = tok_text.strip()
                val = val.strip()

                if tok_text not in Toks:
                    self.load_defaults()
                    ini_error = True
                    ini_error_msg = f"Error in .ini file at line {i+1}: {line}"
                    return

                tok = Toks(tok_text)

                if tok in [Toks.CUSTOM_ACTV, Toks.YES_ACTV, Toks.NO_ACTV]:
                    val = val.lstrip("[").rstrip("]")
                    val = [float(num.strip()) for num in val.split(",")]
                    alpha = val[3]
                    val = [val[i] / 255 for i in range(3)]
                    val.append(alpha)
                elif tok in [Toks.CUSTOM_TXT, Toks.YES_TXT, Toks.NO_TXT, Toks.HEADER_TXT]:
                    val = val.strip('"')
                elif tok in [Toks.CUSTOM_MAP, Toks.YES_MAP, Toks.NO_MAP]:
                    val = int(val)
                elif tok in [Toks.FADE_TM]:
                    val = float(val)
                elif tok in [Toks.DEBUG]:
                    val = val.lower() == "true"

            except Exception as e:
                self.load_defaults()
                ini_error = True
                ini_error_msg = f"Error in .ini file at line {i+1}: {line}"
                return

            INI[tok] = val

    def load_defaults(self):
        INI[Toks.CUSTOM_ACTV] = [97/255, 237/255, 255/255, 0.8]
        INI[Toks.YES_ACTV] = [145/255, 255/255, 121/255, 0.8]
        INI[Toks.NO_ACTV] = [255/255, 121/255, 121/255, 0.8]
        INI[Toks.CUSTOM_TXT] = "Custom"
        INI[Toks.YES_TXT] = "Yes"
        INI[Toks.NO_TXT] = "No"
        INI[Toks.HEADER_TXT] = "Comm App"
        INI[Toks.YES_MAP] = 1073742097
        INI[Toks.NO_MAP] = 281
        INI[Toks.CUSTOM_MAP] = 280
        INI[Toks.FADE_TM] = 1.5
        INI[Toks.DEBUG] = False

class CmdWnd(GridLayout):
    initializer = Initializer()
    initializer.readIni()

    kp = ObjectProperty(None)
    yes = ObjectProperty(None)
    no = ObjectProperty(None)
    custom = ObjectProperty(None)

    if ini_error:
        header_text = StringProperty(ini_error_msg)
        font_size = 20
    else:
        header_text = StringProperty(INI[Toks.HEADER_TXT])
        font_size = 50

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        try:
            char = chr(key)
        except ValueError:
            char = "Unknown"

        if INI[Toks.DEBUG]:
            self.header_text = f"pressed '{char}' ({key})"
        if key in [INI[Toks.YES_MAP], 49]:
            self.yes.actv()
        elif key in [INI[Toks.NO_MAP], 50]:
            self.no.actv()
        elif key in [INI[Toks.CUSTOM_MAP], 51]:
            self.custom.actv()

    def update(self, dt):
        self.yes.update()
        self.no.update()
        self.custom.update()

class CommandScreen(Screen):
    cmd_wnd = ObjectProperty(None)

    def update(self, dt):
        self.cmd_wnd.update(dt)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        self.cmd_wnd.on_key_down(window, key, scancode, codepoint, modifiers)

class Key(Widget):
    text = StringProperty('')

class KeyWnd(GridLayout):
    def __init__(self, **kwargs):
        super(KeyWnd, self).__init__(**kwargs)

        self.text = 'test text testsdf fkjsdl dl sdlk test test text nba'
        self.key_objs = dict()
        self.key_maps = dict()

        for _ in range(4):
            self.add_widget(Widget(size_hint_x=None,size_hint_y=None,width=0))

        self.title = Label(font_size=50, halign='center', text='Keyboard')
        self.title.center_x = self.center_x + 100
        self.add_widget(self.title)

        for _ in range(5):
            self.add_widget(Widget(size_hint_x=None,size_hint_y=None,width=0))

        self.add_widget(Label(font_size=50, text=self.text, halign='left'))
        """
        self.add_widget(Label(
                            font_size=20,
                            halign='left',
                            text_size=(self.width * 10, self.height),
                            text=self.text))
        """

        for _ in range(9):
            self.add_widget(Widget(size_hint_x=None,size_hint_y=None,width=0))

        keys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '\u232B',
                'z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '\u2423', 'CLEAR']

        for i, disp_char in enumerate(keys):
            if disp_char == '\u232B':
                char = '\b'
            elif disp_char == '\u2423':
                char = ' '
            elif disp_char == 'CLEAR':
                char = 'CLR'
            else:
                char = disp_char

            pos = f"{i - 10 * (int(i / 10))},{int(i / 10)}"
            self.key_objs[pos] = Key(text=disp_char)
            self.key_maps[pos] = char
            self.add_widget(self.key_objs[pos])

    def update(self, dt):
        pass

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        pass

class KeyboardScreen(Screen):
    key_wnd = ObjectProperty(None)

    def update(self, dt):
        self.key_wnd.update(dt)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        self.key_wnd.on_key_down(window, key, scancode, codepoint, modifiers)

class MyScreenManager(ScreenManager):
    cmd_scr = None
    key_scr = None

    def update(self, dt):
        if self.current == 'CommandScreen' and self.cmd_scr is not None:
            self.cmd_scr.update(dt)
        elif self.current == 'KeyboardScreen' and self.key_scr is not None:
            self.key_scr.update(dt)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        print(f"Pressed {key}")
        if key == 32:
            if self.current == 'CommandScreen':
                self.current = 'KeyboardScreen'
            else:
                self.current = 'CommandScreen'
        else:
            if self.current == 'CommandScreen' and self.cmd_scr is not None:
                self.cmd_scr.on_key_down(window, key, scancode, codepoint, modifiers)
            elif self.current == 'KeyboardScreen' and self.key_scr is not None:
                self.key_scr.on_key_down(window, key, scancode, codepoint, modifiers)

class CommApp(App):
    def build(self):
        sm = MyScreenManager()
        cmd_scr = CommandScreen(name='CommandScreen')
        key_scr = KeyboardScreen(name='KeyboardScreen')
        sm.add_widget(cmd_scr)
        sm.add_widget(key_scr)
        sm.cmd_scr = cmd_scr
        sm.key_scr = key_scr
        Window.bind(on_key_down=sm.on_key_down)
        Clock.schedule_interval(sm.update, 1.0/30)
        return sm

if __name__ == "__main__":
    CommApp().run()
