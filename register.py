from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.toolbar import MDTopAppBar

from core.auth import register
from core.lang_manager import LangManager


class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang = LangManager("en")
        self.theme_mode = "Light"

        root = MDBoxLayout(orientation="vertical")
        self.toolbar = MDTopAppBar(
            title=self._tr_or("personal_finance_tracker", "Personal Finance Tracker"),
            right_action_items=[
                ["translate", lambda x: self.change_language() ],
                ["theme-light-dark", lambda x: self.toggle_theme() ],
            ]
        )
        root.add_widget(self.toolbar)

        scroll = ScrollView()
        box = MDBoxLayout(
            orientation="vertical", spacing=dp(16), padding=dp(18), size_hint_y=None
        )
        box.bind(minimum_height=box.setter("height"))

        self.title = MDLabel(
            text=self._tr_or("register", "Register"),
            halign="center",
            font_style="H4",
            size_hint_y=None,
            height=dp(34),
        )
        box.add_widget(self.title)

        self.username = MDTextField(
            hint_text=self._tr_or("username", "Username"),
            size_hint_y=None,
            height=dp(50),
            mode="rectangle",
        )
        box.add_widget(self.username)

        self.password = MDTextField(
            hint_text=self._tr_or("password", "Password"),
            password=True,
            size_hint_y=None,
            height=dp(50),
            mode="rectangle",
        )
        box.add_widget(self.password)

        self.btn_register = MDRaisedButton(
            text=self._tr_or("register", "Register"),
            size_hint_y=None,
            height=dp(48),
            on_release=self.do_register
        )
        box.add_widget(self.btn_register)

        self.btn_to_login = MDFlatButton(
            text=self._tr_or("switch_to_login", "Switch to Login"),
            size_hint_y=None,
            height=dp(48),
            on_release=lambda x: setattr(self.manager, "current", "login")
        )
        box.add_widget(self.btn_to_login)

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def _tr_or(self, key, fb):
        t = self.lang.translate(key)
        return t if t != key else fb

    def _show_snackbar(self, text):
        sb = Snackbar()
        sb.text = text
        sb.open()

    def change_language(self, *args):
        new_code = "en" if self.lang.lang_code == "id" else "id"
        self.lang.set_language(new_code)

        self.toolbar.title = self._tr_or("personal_finance_tracker", "Personal Finance Tracker")
        self.title.text = self._tr_or("register", "Register")
        self.username.hint_text = self._tr_or("username", "Username")
        self.password.hint_text = self._tr_or("password", "Password")
        self.btn_register.text = self._tr_or("register", "Register")
        self.btn_to_login.text = self._tr_or("switch_to_login", "Switch to Login")

        self._show_snackbar(f"Language: {self.lang.lang_code.upper()}")

    def toggle_theme(self, *args):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if self.theme_mode == "Light":
            self.theme_mode = "Dark"
            app.theme_cls.theme_style = "Dark"
        else:
            self.theme_mode = "Light"
            app.theme_cls.theme_style = "Light"
        self._show_snackbar(f"Theme: {self.theme_mode}")

    def do_register(self, *args):
        u = self.username.text.strip()
        p = self.password.text.strip()
        if not u or not p:
            self._show_snackbar(self._tr_or("error_fill_fields", "Username and password required"))
            return
        ok, msg_key = register(u, p)
        self._show_snackbar(self._tr_or(msg_key, msg_key))
        if ok:
            self.manager.current = "login"
