from functools import partial
from datetime import datetime
import io
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu

from core.auth import is_premium, logout
from core.excel_exporter import save_to_excel, read_transactions, delete_transaction_by_index
from core.pdf_report import PDFReport
from core.midtrans_payment import pay_with_midtrans
from core.lang_manager import LangManager


FALLBACK = {
    "en": {
        "personal_finance_tracker": "Personal Finance Tracker",
        "status_premium": "Premium account",
        "status_free": "Free account",
        "date": "date",
        "type": "type",
        "category": "category",
        "note": "note",
        "amount": "amount",
        "enter_number": "Enter a valid number",
        "pemasukan": "income",            # keep original keys, provide EN text
        "pengeluaran": "expense",
        "currency": "currency",
        "clear": "clear",
        "save": "save",
        "transaction_history": "Transaction History",
        "view_chart": "Category Chart",
        "export_pdf": "Export PDF",
        "upgrade_premium": "Upgrade to Premium",
        "logout": "Logout",
        "total_expense": "Total Expense",
        "balance": "Balance",
        "transactions": "Transactions",
        "error": "Error",
        "fill_all_fields": "Please fill in all fields correctly.",
        "success": "Success",
        "transaction_saved": "Transaction saved.",
        "no_transactions": "No transactions yet.",
        "confirm_delete": "Delete Transaction",
        "confirm_delete_text": "Are you sure you want to delete this transaction?",
        "cancel": "Cancel",
        "delete": "Delete",
        "jumlah": "Amount",
        "total_per_category": "Totals by Category",
        "premium_only": "Premium Required",
        "premium_feature_only": "This feature is available for Premium users only.",
        "pdf_generated": "PDF generated.",
        "ok": "OK",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "choose_subscription_plan": "Choose a subscription plan",
    },
    "id": {
        "personal_finance_tracker": "Pencatat Keuangan Pribadi",
        "status_premium": "Akun premium",
        "status_free": "Akun gratis",
        "date": "tanggal",
        "type": "tipe",
        "category": "kategori",
        "note": "catatan",
        "amount": "nominal",
        "enter_number": "Masukkan angka yang benar",
        "pemasukan": "pemasukan",
        "pengeluaran": "pengeluaran",
        "currency": "mata uang",
        "clear": "hapus",
        "save": "simpan",
        "transaction_history": "Riwayat Transaksi",
        "view_chart": "Grafik Kategori",
        "export_pdf": "Ekspor PDF",
        "upgrade_premium": "Upgrade Premium",
        "logout": "Keluar",
        "total_expense": "Total Pengeluaran",
        "balance": "Saldo",
        "transactions": "Transaksi",
        "error": "Kesalahan",
        "fill_all_fields": "Harap isi semua kolom dengan benar.",
        "success": "Berhasil",
        "transaction_saved": "Transaksi tersimpan.",
        "no_transactions": "Belum ada transaksi.",
        "confirm_delete": "Hapus Transaksi",
        "confirm_delete_text": "Yakin ingin menghapus transaksi ini?",
        "cancel": "Batal",
        "delete": "Hapus",
        "jumlah": "Jumlah",
        "total_per_category": "Total per Kategori",
        "premium_only": "Khusus Premium",
        "premium_feature_only": "Fitur ini hanya tersedia untuk pengguna Premium.",
        "pdf_generated": "PDF berhasil dibuat.",
        "ok": "OK",
        "weekly": "Mingguan",
        "monthly": "Bulanan",
        "choose_subscription_plan": "Pilih paket berlangganan",
    }
}


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ----- Language & Theme -----
        # Default English so UI tidak campur
        self.lang = LangManager('en')
        # cache kode bahasa agar fallback bisa tahu
        self.current_lang_code = getattr(self.lang, 'lang_code', 'en')
        self.is_dark_theme = False
        self.dialog = None

        # ----- Currency list -----
        self.currency = 'IDR'
        self.currencies = {
            'IDR': 'Indonesian Rupiah', 'USD': 'US Dollar', 'AUD': 'Australian Dollar',
            'BRL': 'Brazilian Real', 'EUR': 'Euro', 'AED': 'UAE Dirham',
            'GBP': 'British Pound', 'JPY': 'Japanese Yen', 'CAD': 'Canadian Dollar',
            'CHF': 'Swiss Franc', 'NZD': 'New Zealand Dollar', 'SGD': 'Singapore Dollar',
            'HKD': 'Hong Kong Dollar', 'SEK': 'Swedish Krona', 'NOK': 'Norwegian Krone',
            'DKK': 'Danish Krone', 'INR': 'Indian Rupee', 'CNY': 'Chinese Yuan',
        }

        # ----- Main Layout -----
        self.scroll = ScrollView()
        self.main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=16,
            padding=16,
            size_hint=(0.98, None),
            pos_hint={"center_x": 0.5},
        )
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        # Background "gradient" (multi-layer for smoother look)
        with self.main_layout.canvas.before:
            # base
            self.body_col_a = Color(0.95, 0.98, 1.00, 1)
            self.body_rect_a = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            # mid layer
            self.body_col_b = Color(0.90, 0.96, 1.00, 1)
            self.body_rect_b = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
            # soft vignette band at bottom
            self.body_col_c = Color(0.84, 0.93, 1.00, 0.6)
            self.body_rect_c = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_body_bg, pos=self._update_body_bg)

        # ----- Header with layered gradient -----
        self.header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=82,
            padding=[16, 10, 16, 10],
            spacing=12,
        )
        with self.header.canvas.before:
            # deep to light
            self.header_col_a = Color(0.05, 0.30, 0.70, 1)
            self.header_rect_a = Rectangle(size=self.header.size, pos=self.header.pos)
            self.header_col_b = Color(0.15, 0.55, 0.90, 1)
            self.header_rect_b = Rectangle(size=self.header.size, pos=self.header.pos)
            self.header_col_c = Color(0.55, 0.80, 0.98, 1)
            self.header_rect_c = Rectangle(size=self.header.size, pos=self.header.pos)
        self.header.bind(size=self._update_header_bg, pos=self._update_header_bg)

        # Title
        self.title_label = MDLabel(
            text=self.t("personal_finance_tracker"),
            font_style="H5",
            halign="left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_x=1,
        )
        # left spacer + title
        self.header.add_widget(MDLabel(size_hint=(None, 1), width=4))
        self.header.add_widget(self.title_label)

        # right controls: language & theme
        right_box = MDBoxLayout(size_hint=(None, 1), width=120, spacing=4)
        self.btn_lang = MDIconButton(icon="earth", on_release=self.switch_language)
        self.btn_toggle_theme = MDIconButton(icon="theme-light-dark", on_release=self.toggle_theme)
        right_box.add_widget(self.btn_lang)
        right_box.add_widget(self.btn_toggle_theme)
        self.header.add_widget(right_box)

        self.main_layout.add_widget(self.header)

        # ----- Top Info (premium) -----
        top_info = MDBoxLayout(orientation='horizontal', spacing=12, size_hint_y=None, height=36)
        self.premium_label = MDLabel(
            text=self.t("status_premium") if is_premium() else self.t("status_free"),
            halign="left",
            theme_text_color="Custom",
            text_color=(0.22, 0.26, 0.32, 1),
        )
        top_info.add_widget(self.premium_label)
        self.main_layout.add_widget(top_info)

        # ----- Stat summary row -----
        self.stats_grid = MDGridLayout(
            cols=self._calc_cols(Window.width),
            spacing=12,
            adaptive_height=True,
        )
        Window.bind(size=lambda *_: self._update_grid_cols())
        self._add_stat_cards()
        self.main_layout.add_widget(self.stats_grid)

        # ----- Form Input Card -----
        self.form_card = MDCard(
            orientation='vertical',
            padding=16,
            spacing=12,
            elevation=8,
            radius=[14],
            size_hint=(1, None),
        )
        self.form_card.bind(minimum_height=self.form_card.setter('height'))

        self.fields = ['date', 'type', 'category', 'note', 'amount']
        self.inputs = {}
        for field in self.fields:
            hint = self.t(field)
            inp = MDTextField(
                hint_text=hint.capitalize(),
                multiline=False,
                size_hint_y=None,
                height=50,
                mode="rectangle",
            )
            if field == 'date':
                inp.text = datetime.now().strftime("%Y-%m-%d")
            if field == 'amount':
                inp.input_filter = 'float'
                inp.helper_text = self.t("enter_number")
                inp.helper_text_mode = "on_focus"
            if field == 'type':
                inp.readonly = True
                inp.text = self.t("pengeluaran").capitalize()
            self.inputs[field] = inp
            self.form_card.add_widget(inp)

        # Type dropdown
        self._build_type_menu()

        # Currency dropdown (codes only to avoid mixed language)
        self.currency_field = MDTextField(
            readonly=True,
            text=self.currency,
            hint_text=self.t("currency").capitalize(),
            size_hint_y=None,
            height=50,
            mode="rectangle",
        )
        self.currency_menu = MDDropdownMenu(
            caller=self.currency_field,
            items=[{"viewclass": "OneLineListItem", "text": key, "on_release": partial(self.set_currency, key)}
                   for key in self.currencies],
            max_height=280,
        )
        self.currency_field.bind(on_touch_down=self.check_open_currency_menu)
        self.form_card.add_widget(self.currency_field)

        self.main_layout.add_widget(self.form_card)

        # ----- Save / Clear Buttons -----
        btn_row = MDBoxLayout(spacing=12, size_hint_y=None, height=54)
        self.btn_clear = MDFlatButton(
            text=self.t("clear").capitalize(),
            on_release=self.clear_inputs,
            text_color=(1, 0.45, 0.38, 1),
        )
        self.btn_save = MDRaisedButton(
            text=self.t("save").capitalize(),
            on_release=self.save_transaction,
            md_bg_color=(0.06, 0.5, 0.9, 1),
            text_color=(1, 1, 1, 1),
            elevation=8,
        )
        btn_row.add_widget(self.btn_clear)
        btn_row.add_widget(self.btn_save)
        self.main_layout.add_widget(btn_row)

        # ----- Transaction List Card -----
        self.history_label = MDLabel(
            text=self.t("transaction_history"),
            halign="left",
            theme_text_color="Hint",
            size_hint_y=None,
            height=28,
        )
        self.list_card = MDCard(padding=12, elevation=8, radius=[14], size_hint=(1, None), height=340)
        self.scroll_list = ScrollView(scroll_type=['bars', 'content'], bar_width=10)
        self.transaction_list = MDList()
        self.scroll_list.add_widget(self.transaction_list)
        self.list_card.add_widget(self.scroll_list)
        self.main_layout.add_widget(self.history_label)
        self.main_layout.add_widget(self.list_card)

        # ----- Chart -----
        self.chart_label = MDLabel(
            text=self.t("view_chart"),
            halign="left",
            theme_text_color="Hint",
            size_hint_y=None,
            height=28
        )
        self.chart_image = Image(size_hint_y=None, height=340)
        self.main_layout.add_widget(self.chart_label)
        self.main_layout.add_widget(self.chart_image)

        # ----- Bottom Buttons -----
        bottom_btns = MDBoxLayout(spacing=12, size_hint_y=None, height=56)
        self.btn_export_pdf = MDRaisedButton(
            text=self.t("export_pdf").capitalize(),
            on_release=self.export_pdf,
            md_bg_color=(0.12, 0.6, 0.2, 1),
            elevation=8,
        )
        self.btn_upgrade = MDRaisedButton(
            text=self.t("upgrade_premium").capitalize(),
            on_release=self.upgrade_premium,
            md_bg_color=(1, 0.5, 0),
            elevation=8,
        )
        bottom_btns.add_widget(self.btn_export_pdf)
        bottom_btns.add_widget(self.btn_upgrade)
        self.main_layout.add_widget(bottom_btns)

        # ----- Footer -----
        footer = MDBoxLayout(spacing=12, size_hint_y=None, height=48)
        self.btn_logout = MDFlatButton(text=self.t("logout").capitalize(), on_release=self.do_logout)
        footer.add_widget(self.btn_logout)
        self.main_layout.add_widget(footer)

        # Add scroll to screen
        self.scroll.add_widget(self.main_layout)
        self.add_widget(self.scroll)

        # cache stat widgets for quick update
        self._stat_card_widgets = []

        # schedule initial refresh after layout
        Clock.schedule_once(lambda dt: self.refresh_ui(), 0.05)

        # subtle header breathing animation
        Clock.schedule_once(lambda dt: self._animate_header_bg(), 0.2)

    # ==========
    # Translation helper with fallback 
    # ==========
    def t(self, key: str) -> str:
        txt = None
        try:
            txt = self.lang.translate(key)
        except Exception:
            txt = None
        # update cache of current lang code if ada
        self.current_lang_code = getattr(self.lang, 'lang_code', self.current_lang_code)
        if not txt or txt == key or not isinstance(txt, str):
            txt = FALLBACK.get(self.current_lang_code, FALLBACK["en"]).get(key, key)
        return txt

    # =========================
    # Responsive & gradient helpers
    # =========================
    def _calc_cols(self, width):
        if width < 520:
            return 1
        if width < 900:
            return 2
        return 3

    def _update_grid_cols(self):
        self.stats_grid.cols = self._calc_cols(Window.width)

    def _apply_theme_colors(self):
        if self.is_dark_theme:
            # header tones
            self.header_col_a.rgba = (0.02, 0.10, 0.25, 1)
            self.header_col_b.rgba = (0.05, 0.25, 0.50, 1)
            self.header_col_c.rgba = (0.15, 0.45, 0.75, 1)
            # body tones
            self.body_col_a.rgba = (0.03, 0.06, 0.10, 1)
            self.body_col_b.rgba = (0.05, 0.08, 0.12, 1)
            self.body_col_c.rgba = (0.07, 0.10, 0.15, 0.7)
            title_color = (1, 1, 1, 1)
            hint_color = (0.92, 0.93, 0.96, 1)
        else:
            self.header_col_a.rgba = (0.05, 0.30, 0.70, 1)
            self.header_col_b.rgba = (0.15, 0.55, 0.90, 1)
            self.header_col_c.rgba = (0.55, 0.80, 0.98, 1)
            self.body_col_a.rgba = (0.95, 0.98, 1.00, 1)
            self.body_col_b.rgba = (0.90, 0.96, 1.00, 1)
            self.body_col_c.rgba = (0.84, 0.93, 1.00, 0.6)
            title_color = (1, 1, 1, 1)
            hint_color = (0.22, 0.26, 0.32, 1)

        try:
            self.title_label.text_color = title_color
            self.premium_label.text_color = hint_color
        except Exception:
            pass

        app = MDApp.get_running_app()
        if app:
            app.theme_cls.theme_style = "Dark" if self.is_dark_theme else "Light"

    def _update_header_bg(self, *args):
        w, h = self.header.size
        x, y = self.header.pos
        # create layered feel: 60% + 30% + 10%
        self.header_rect_a.size = (w * 0.6, h)
        self.header_rect_a.pos = (x, y)
        self.header_rect_b.size = (w * 0.3, h)
        self.header_rect_b.pos = (x + w * 0.6, y)
        self.header_rect_c.size = (w * 0.1, h)
        self.header_rect_c.pos = (x + w * 0.9, y)

    def _animate_header_bg(self):
        # slow subtle move of band C for a "shimmer" effect
        if not self.header or not self.header_rect_c:
            return
        w, h = self.header.size
        x, y = self.header.pos
        anim = Animation(pos=(x + w * 0.85, y), d=2.6, t="in_out_sine") + Animation(pos=(x + w * 0.9, y), d=2.6, t="in_out_sine")
        anim.repeat = True
        anim.start(self.header_rect_c)

    def _update_body_bg(self, *args):
        w, h = self.main_layout.size
        x, y = self.main_layout.pos
        # top, middle, bottom bands
        self.body_rect_a.size = (w, h * 0.50)
        self.body_rect_a.pos = (x, y + h * 0.50)
        self.body_rect_b.size = (w, h * 0.36)
        self.body_rect_b.pos = (x, y + h * 0.14)
        self.body_rect_c.size = (w, h * 0.14)
        self.body_rect_c.pos = (x, y)

    # -------------------------
    # Stat cards
    # -------------------------
    def _add_stat_cards(self):
        titles = [
            self.t("total_expense"),
            self.t("balance"),
            self.t("transactions"),
        ]
        values = ["0", "0", "0"]
        self._stat_card_widgets = []
        self.stats_grid.clear_widgets()

        for ttxt, v in zip(titles, values):
            card = MDCard(
                orientation='vertical',
                padding=14,
                radius=[14],
                elevation=8,
                size_hint=(None, None),
                width=max(260, Window.width * 0.30),
                height=118
            )
            lbl_title = MDLabel(
                text=ttxt.capitalize(),
                theme_text_color="Hint",
                halign="left",
                size_hint_y=None,
                height=22,
                shorten=True
            )
            lbl_value = MDLabel(
                text=v,
                font_style="H6",
                halign="left",
                size_hint_y=None,
                height=64,
                shorten=True
            )
            card.add_widget(lbl_title)
            card.add_widget(lbl_value)
            self.stats_grid.add_widget(card)
            self._stat_card_widgets.append((lbl_title, lbl_value))
            Animation(opacity=1, d=0.28, t="out_quad").start(card)

    def _refresh_stat_cards(self):
        data = read_transactions()
        total_expense = 0.0
        total_income = 0.0
        count_tx = 0
        if isinstance(data, pd.DataFrame) and not data.empty:
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
            total_income = data.loc[data['Amount'] >= 0, 'Amount'].sum()
            total_expense = -data.loc[data['Amount'] < 0, 'Amount'].sum()
            count_tx = len(data)
        balance = total_income - total_expense

        def fmt(n):
            try:
                return f"{self.currency} {n:,.2f}"
            except Exception:
                return f"{self.currency} {n}"

        if self._stat_card_widgets and len(self._stat_card_widgets) >= 3:
            self._stat_card_widgets[0][1].text = fmt(total_expense)
            self._stat_card_widgets[1][1].text = fmt(balance)
            self._stat_card_widgets[2][1].text = str(count_tx)
        else:
            self._add_stat_cards()

    # -------------------------
    # Type menu build
    # -------------------------
    def _build_type_menu(self):
        inc = self.t("pemasukan").capitalize()
        exp = self.t("pengeluaran").capitalize()
        items = [
            {"viewclass": "OneLineListItem", "text": inc, "on_release": partial(self.set_type, inc)},
            {"viewclass": "OneLineListItem", "text": exp, "on_release": partial(self.set_type, exp)},
        ]
        try:
            self.type_menu.dismiss()
        except Exception:
            pass
        self.type_menu = MDDropdownMenu(caller=self.inputs['type'], items=items, max_height=150)
        self.inputs['type'].bind(on_touch_down=self.check_open_type_menu)

    def check_open_type_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.type_menu.open()

    def check_open_currency_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.currency_menu.open()

    def set_type(self, value, *args):
        self.inputs['type'].text = value
        try:
            self.type_menu.dismiss()
        except Exception:
            pass

    def set_currency(self, val, *args):
        self.currency = val
        self.currency_field.text = val
        try:
            self.currency_menu.dismiss()
        except Exception:
            pass
        # refresh UI
        self._refresh_stat_cards()
        self.load_transactions()
        self.update_chart()

    # -------------------------
    # Refresh UI
    # -------------------------
    def refresh_ui(self, *_):
        # update top labels & translated text
        self.premium_label.text = self.t("status_premium") if is_premium() else self.t("status_free")
        try:
            self.title_label.text = self.t("personal_finance_tracker")
        except Exception:
            self.title_label.text = "Personal Finance Tracker"

        # rebuild type menu to refresh translations
        self._build_type_menu()

        # inputs hints
        for field in self.fields:
            if field in self.inputs:
                self.inputs[field].hint_text = self.t(field).capitalize()
        self.currency_field.hint_text = self.t("currency").capitalize()
        self.btn_clear.text = self.t("clear").capitalize()
        self.btn_save.text = self.t("save").capitalize()
        self.history_label.text = self.t("transaction_history")
        self.chart_label.text = self.t("view_chart")
        self.btn_export_pdf.text = self.t("export_pdf").capitalize()
        self.btn_upgrade.text = self.t("upgrade_premium").capitalize()
        self.btn_logout.text = self.t("logout").capitalize()

        # apply theme colors
        self._apply_theme_colors()
        self._update_header_bg()
        self._update_body_bg()

        # refresh data-driven widgets
        self.load_transactions()
        self.update_chart()
        self._refresh_stat_cards()

    # -------------------------
    # CRUD operations
    # -------------------------
    def clear_inputs(self, *args):
        self.inputs['date'].text = datetime.now().strftime("%Y-%m-%d")
        self.inputs['type'].text = self.t("pengeluaran").capitalize()
        self.inputs['category'].text = ""
        self.inputs['note'].text = ""
        self.inputs['amount'].text = ""

    def save_transaction(self, instance):
        try:
            date_val = self.inputs['date'].text.strip()
            tipe = self.inputs['type'].text.strip().lower()
            category = self.inputs['category'].text.strip()
            note = self.inputs['note'].text.strip()
            amount_text = self.inputs['amount'].text.strip()

            if not date_val or not category or not amount_text or not tipe:
                self.show_dialog(self.t("error"), self.t("fill_all_fields"))
                return

            datetime.strptime(date_val, "%Y-%m-%d")
            amount = float(amount_text)
            # if type is not 'pemasukan' (income), treat as expense (negative)
            if tipe != self.t("pemasukan").lower():
                amount = -abs(amount)

            # save (core function will append to the per-user Excel)
            save_to_excel([{"Date": date_val, "Category": category, "Note": note, "Amount": amount}])
            self.show_dialog(self.t("success"), self.t("transaction_saved"))
            self.clear_inputs()
            # refresh
            self.load_transactions()
            self.update_chart()
            self._refresh_stat_cards()
        except Exception as e:
            self.show_dialog(self.t("error"), str(e))

    def delete_transaction(self, df_index=None, signature=None):
        """
        Use core.excel_exporter.delete_transaction_by_index() for index-based deletes.
        If index not usable (e.g. indexes shifted), attempt to find the row by signature:
        signature = (Date, Category, Note, Amount)
        """
        try:
            data = read_transactions()
            if not isinstance(data, pd.DataFrame) or data.empty:
                self.show_dialog(self.t("error"), self.t("no_transactions"))
                return

            # direct index deletion if valid
            if df_index is not None and df_index in data.index:
                ok = delete_transaction_by_index(int(df_index))
                if not ok:
                    self.show_dialog(self.t("error"), self.t("cannot_delete") if "cannot_delete" in FALLBACK["en"] else "Cannot delete.")
                    return
            else:
                # fallback: search for first matching signature and delete
                if signature is None:
                    self.show_dialog(self.t("error"), self.t("cannot_delete") if "cannot_delete" in FALLBACK["en"] else "Cannot delete.")
                    return
                date_s, cat_s, note_s, amt_s = signature
                data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
                found_index = None
                for i, row in data.iterrows():
                    row_amt = float(row.get('Amount', 0) or 0)
                    # string compare date/category/note
                    row_date = str(row.get('Date', ''))
                    row_cat = str(row.get('Category', ''))
                    row_note = str(row.get('Note', ''))
                    try:
                        amt_match = abs(row_amt - float(amt_s)) < 1e-6
                    except Exception:
                        amt_match = (str(row_amt) == str(amt_s))
                    if row_date == str(date_s) and row_cat == str(cat_s) and row_note == str(note_s) and amt_match:
                        found_index = i
                        break
                if found_index is None:
                    self.show_dialog(self.t("error"), self.t("cannot_delete") if "cannot_delete" in FALLBACK["en"] else "Cannot delete.")
                    return
                ok = delete_transaction_by_index(int(found_index))
                if not ok:
                    self.show_dialog(self.t("error"), self.t("cannot_delete") if "cannot_delete" in FALLBACK["en"] else "Cannot delete.")
                    return

            # success
            self.show_dialog(self.t("success"), self.t("transaction_deleted") if "transaction_deleted" in FALLBACK["en"] else "Transaction deleted.")
            self.load_transactions()
            self.update_chart()
            self._refresh_stat_cards()
        except Exception as e:
            self.show_dialog(self.t("error"), str(e))

    def load_transactions(self):
        """
        Populate the list. For delete safety we pass a signature tuple to _on_delete_pressed:
        (Date, Category, Note, Amount) so the delete function can still find the row even if
        indices or append behavior changed.
        """
        self.transaction_list.clear_widgets()
        data = read_transactions()
        if not isinstance(data, pd.DataFrame) or data.empty:
            self.transaction_list.add_widget(OneLineAvatarIconListItem(text=self.t("no_transactions")))
            return

        # ensure numeric and safe formatting
        data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)

        for idx, row in data.iterrows():
            date_str = row.get('Date', "?")
            nominal = abs(float(row.get('Amount', 0) or 0))
            tipe_text = self.t("pemasukan") if row.get('Amount', 0) >= 0 else self.t("pengeluaran")
            cat = row.get('Category', "")
            note = row.get('Note', "")
            item_text = f"{date_str} | {tipe_text.capitalize()} | {cat} | {self.currency} {nominal:,.2f} | {note}"

            item = OneLineAvatarIconListItem(text=item_text)

            # build signature to help deletion if indices differ later
            signature = (str(date_str), str(cat), str(note), float(row.get('Amount', 0) or 0))

            # delete icon with binding index + signature
            delete_icon = IconRightWidget(icon="trash-can-outline",
                                          on_release=partial(self._on_delete_pressed, idx, signature))
            item.add_widget(delete_icon)
            self.transaction_list.add_widget(item)

    def _on_delete_pressed(self, df_index, signature, instance):
        # confirm dialog before delete
        if self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass

        self.dialog = MDDialog(
            title=self.t("confirm_delete"),
            text=self.t("confirm_delete_text"),
            buttons=[
                MDFlatButton(text=self.t("cancel"), on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text=self.t("delete"), on_release=lambda x: (self.dialog.dismiss(), self.delete_transaction(df_index, signature)))
            ]
        )
        self.dialog.open()

    # -------------------------
    # Chart
    # -------------------------
    def update_chart(self):
        data = read_transactions()
        if not isinstance(data, pd.DataFrame) or data.empty:
            self.chart_image.texture = None
            return
        try:
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
            grouped = data.groupby('Category')['Amount'].agg([
                ('income', lambda s: s[s >= 0].sum()),
                ('expense', lambda s: -s[s < 0].sum())
            ])
            if grouped.empty:
                self.chart_image.texture = None
                return

            categories = grouped.index.tolist()
            income_vals = grouped['income'].fillna(0).values
            expense_vals = grouped['expense'].fillna(0).values

            fig, ax = plt.subplots(figsize=(7.6, 4.2))

            if self.is_dark_theme:
                fig.patch.set_facecolor("#0b1720")
                ax.set_facecolor("#0b1720")
                text_color = "#ecf0f1"
                grid_color = "#355169"
            else:
                fig.patch.set_facecolor("#f3f8ff")
                ax.set_facecolor("#f3f8ff")
                text_color = "#2c3e50"
                grid_color = "#c9d9ee"

            x = np.arange(len(categories))
            width = 0.36

            inc_color = "#4cd964"
            exp_color = "#ff6b6b"

            ax.bar(x - width/2, income_vals, width, label=self.t("pemasukan").capitalize(), color=inc_color)
            ax.bar(x + width/2, expense_vals, width, label=self.t("pengeluaran").capitalize(), color=exp_color)

            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=35, ha='right', fontsize=9, color=text_color)
            ax.set_ylabel(f"{self.t('jumlah')} ({self.currency})", color=text_color)
            ax.set_title(self.t("total_per_category"), color=text_color)
            ax.tick_params(axis='y', colors=text_color)
            ax.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.6, color=grid_color)
            for spine in ax.spines.values():
                spine.set_color(text_color)
                spine.set_alpha(0.35)
            leg = ax.legend()
            for txt in leg.get_texts():
                txt.set_color(text_color)
            leg.get_frame().set_facecolor(fig.get_facecolor())
            plt.tight_layout()

            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=170, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)

            im = CoreImage(buf, ext='png')
            Clock.schedule_once(lambda dt: self.chart_image.setter('texture')(self.chart_image, im.texture), 0)
        except Exception:
            self.chart_image.texture = None

    # -------------------------
    # PDF / Premium / Logout / Dialog
    # -------------------------
    def export_pdf(self, instance):
        if not is_premium():
            self.show_dialog(self.t("premium_only"), self.t("premium_feature_only"))
            return
        try:
            PDFReport().generate_report()
            self.show_dialog(self.t("success"), self.t("pdf_generated"))
        except Exception as e:
            self.show_dialog(self.t("error"), str(e))

    def upgrade_premium(self, instance):
        if self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass
        self.dialog = MDDialog(
            title=self.t("upgrade_premium"),
            text=self.t("choose_subscription_plan"),
            buttons=[
                MDFlatButton(text=self.t("weekly"), on_release=lambda x: self._pay("weekly")),
                MDFlatButton(text=self.t("monthly"), on_release=lambda x: self._pay("monthly")),
                MDFlatButton(text=self.t("cancel"), on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def _pay(self, plan):
        if self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass
        pay_with_midtrans(plan)

    def do_logout(self, instance):
        logout()
        MDApp.get_running_app().stop()

    def show_dialog(self, title, text):
        if self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text=self.t("ok"), on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    # -------------------------
    # Language & Theme toggles
    # -------------------------
    def switch_language(self, instance=None):
        # read current (fallback to cached)
        current = getattr(self.lang, 'lang_code', self.current_lang_code)
        new_lang = 'en' if current == 'id' else 'id'
        try:
            self.lang.set_language(new_lang)
        except Exception:
            # if core fails, at least update cache so fallback works
            self.current_lang_code = new_lang
        # refresh UI (rebuild menus & texts)
        self.refresh_ui()

    def toggle_theme(self, instance=None):
        self.is_dark_theme = not self.is_dark_theme
        self.refresh_ui()


class FinanceApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return HomeScreen()


if __name__ == "__main__":
    FinanceApp().run()
