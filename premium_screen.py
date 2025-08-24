from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from core.auth import upgrade_to_premium, is_premium

class PremiumScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        layout.add_widget(MDLabel(
            text="Upgrade ke Premium",
            font_style="H4",
            halign="center"
        ))

        layout.add_widget(MDLabel(
            text="Dapatkan fitur lengkap seperti ekspor PDF, sinkronisasi cloud, dan lainnya.",
            halign="center",
            theme_text_color="Secondary"
        ))

        self.upgrade_btn = MDRaisedButton(
            text="Upgrade Sekarang",
            pos_hint={"center_x": 0.5},
            on_release=self.upgrade
        )
        layout.add_widget(self.upgrade_btn)

        self.back_btn = MDRaisedButton(
            text="Kembali",
            pos_hint={"center_x": 0.5},
            on_release=self.go_back
        )
        layout.add_widget(self.back_btn)

        self.add_widget(layout)

        self.update_button_status()

    def update_button_status(self):
        if is_premium():
            self.upgrade_btn.disabled = True
            self.upgrade_btn.text = "Sudah Premium"

    def upgrade(self, instance):
        # Simulasi upgrade
        upgrade_to_premium()
        dialog = MDDialog(
            title="Sukses",
            text="Selamat! Anda telah menjadi pengguna premium.",
        )
        dialog.open()
        self.update_button_status()

    def go_back(self, instance):
        self.manager.current = 'home'
