from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
import os

from core.auth import login, register
from core.lang_manager import LangManager


class AuthScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Bahasa default EN
        self.lang = LangManager("en")
        self.mode = "login"
        self.dialog = None  # Simpan reference MDDialog

        # ===== BACKGROUND =====
        self.md_bg_color = get_color_from_hex("#F1F5F9")
        bg_path = os.path.join("assets", "bg_gradient.png")
        if os.path.exists(bg_path):
            self.gradient_layer = Image(
                source=bg_path, allow_stretch=True, keep_ratio=False, opacity=0.9
            )
            self.add_widget(self.gradient_layer)

        # ===== CARD UTAMA =====
        self.card = MDCard(
            orientation="vertical",
            padding=28,
            spacing=22,
            size_hint=(0.92, None),
            height=460,
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            radius=[26, 26, 26, 26],
            elevation=10,
            md_bg_color=get_color_from_hex("#FFFFFF"),
        )

        # Judul
        self.title = MDLabel(
            text=self.lang.translate("login"),
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#0F172A"),
            size_hint_y=None,
            height=36,
        )
        self.card.add_widget(self.title)

        # Subtitle
        self.subtitle = MDLabel(
            text=self.lang.translate("subtitle_login"),
            halign="center",
            theme_text_color="Hint",
            size_hint_y=None,
            height=18,
        )
        self.card.add_widget(self.subtitle)

        # Input username
        self.username = MDTextField(
            hint_text=self.lang.translate("username"),
            icon_right="account",
            mode="rectangle",
            size_hint=(1, None),
            height=56,
            required=True,
        )
        self.card.add_widget(self.username)

        # Input password
        self.password = MDTextField(
            hint_text=self.lang.translate("password"),
            icon_right="eye-off",
            password=True,
            mode="rectangle",
            size_hint=(1, None),
            height=56,
            required=True,
        )
        self.card.add_widget(self.password)

        # Tombol aksi utama
        self.btn_action = MDRaisedButton(
            text=self.lang.translate("login"),
            md_bg_color=get_color_from_hex("#2563EB"),
            text_color=get_color_from_hex("#FFFFFF"),
            size_hint=(1, None),
            height=50,
            elevation=8,
            on_release=self.do_action,
        )
        self.card.add_widget(self.btn_action)

        # Tombol switch login/register
        self.btn_switch = MDFlatButton(
            text=self.lang.translate("switch_to_register"),
            text_color=get_color_from_hex("#2563EB"),
            on_release=self.switch_mode,
        )
        self.card.add_widget(self.btn_switch)

        # Tombol ganti bahasa
        self.btn_switch_lang = MDFlatButton(
            text="Switch to Bahasa Indonesia",
            text_color=get_color_from_hex("#334155"),
            on_release=self.switch_language,
        )
        self.card.add_widget(self.btn_switch_lang)

        # Footer
        self.footer = MDLabel(
            text="© 2025 Finance Tracker",
            halign="center",
            theme_text_color="Hint",
            size_hint_y=None,
            height=16,
        )
        self.card.add_widget(self.footer)

        # Layout root
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(self.card)
        self.add_widget(root)

    # ===== FUNGSI LOGIN / REGISTER =====
    def do_action(self, instance):
        user = self.username.text.strip()
        pwd = self.password.text.strip()
        if not user or not pwd:
            self.show_dialog(self.lang.translate("error_fill_fields"))
            return

        if self.mode == "login":
            success, msg_key = login(user, pwd)
        else:
            success, msg_key = register(user, pwd)

        self.show_dialog(self.lang.translate(msg_key))

        if success and self.mode == "login" and self.manager:
            self.manager.current = "home"

    # ===== GANTI MODE LOGIN / REGISTER =====
    def switch_mode(self, instance):
        Animation(opacity=0, duration=0.15).start(self.card)

        def _after(*args):
            if self.mode == "login":
                self.mode = "register"
                self.title.text = self.lang.translate("register")
                self.btn_action.text = self.lang.translate("register")
                self.btn_switch.text = self.lang.translate("switch_to_login")
                self.subtitle.text = self.lang.translate("subtitle_register")
            else:
                self.mode = "login"
                self.title.text = self.lang.translate("login")
                self.btn_action.text = self.lang.translate("login")
                self.btn_switch.text = self.lang.translate("switch_to_register")
                self.subtitle.text = self.lang.translate("subtitle_login")

            Animation(opacity=1, duration=0.15).start(self.card)

        Animation(duration=0.16).bind(on_complete=_after).start(self.card)

    # ===== GANTI BAHASA =====
    def switch_language(self, instance):
        new_lang = "id" if self.lang.lang_code == "en" else "en"
        self.lang.set_language(new_lang)

        # Update semua teks
        self.title.text = self.lang.translate(self.mode)
        self.username.hint_text = self.lang.translate("username")
        self.password.hint_text = self.lang.translate("password")
        self.btn_action.text = self.lang.translate(self.mode)
        self.btn_switch.text = self.lang.translate(
            "switch_to_register" if self.mode == "login" else "switch_to_login"
        )
        self.subtitle.text = self.lang.translate(
            "subtitle_login" if self.mode == "login" else "subtitle_register"
        )

        # Update tombol bahasa (tanpa emoji)
        self.btn_switch_lang.text = (
            "Switch to English" if new_lang == "id" else "Switch to Bahasa Indonesia"
        )

    # ===== POPUP DIALOG =====
    def show_dialog(self, text):
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Info",
            text=text,
            size_hint=(0.85, None),
        )
        self.dialog.open()
