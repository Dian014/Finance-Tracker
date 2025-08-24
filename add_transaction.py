from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from core.excel_exporter import save_to_excel
import datetime

class AddTransactionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.amount_input = TextInput(hint_text="Amount", multiline=False, input_filter='float')
        self.note_input = TextInput(hint_text="Note", multiline=False)
        self.date_input = TextInput(hint_text="Date (YYYY-MM-DD)", multiline=False)
        self.category_spinner = Spinner(
            text='Select Category',
            values=('Food', 'Transport', 'Entertainment', 'Bills', 'Others'),
            size_hint=(1, None),
            height=44
        )

        layout.add_widget(Label(text="Add New Transaction", font_size=18))
        layout.add_widget(self.amount_input)
        layout.add_widget(self.note_input)
        layout.add_widget(self.date_input)
        layout.add_widget(self.category_spinner)

        save_btn = Button(text="Save")
        save_btn.bind(on_press=self.save_transaction)
        layout.add_widget(save_btn)

        back_btn = Button(text="Back to Home")
        back_btn.bind(on_press=self.go_home)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def save_transaction(self, instance):
        amount = self.amount_input.text.strip()
        note = self.note_input.text.strip()
        date_str = self.date_input.text.strip()
        category = self.category_spinner.text if self.category_spinner.text != 'Select Category' else 'Others'

        # Validasi amount wajib diisi dan valid
        if not amount or not amount.replace('.', '', 1).isdigit():
            popup = Popup(title='Error', content=Label(text='Amount is required and must be a number'), size_hint=(0.8, 0.4))
            popup.open()
            return

        # Validasi tanggal wajib diisi dan format benar
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except Exception:
            popup = Popup(title='Error', content=Label(text='Date must be in YYYY-MM-DD format'), size_hint=(0.8, 0.4))
            popup.open()
            return

        data = [{
            "Amount": float(amount),
            "Note": note,
            "Date": date_obj.strftime('%Y-%m-%d'),
            "Category": category
        }]
        save_to_excel(data)

        popup = Popup(title='Saved', content=Label(text='Transaction saved!'), size_hint=(0.8, 0.4))
        popup.open()

        # Reset input
        self.amount_input.text = ''
        self.note_input.text = ''
        self.date_input.text = ''
        self.category_spinner.text = 'Select Category'

    def go_home(self, instance):
        self.manager.current = 'home'
