from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
import io
import matplotlib.pyplot as plt
from kivy.core.image import Image as CoreImage
from core.excel_exporter import read_transactions
import pandas as pd

class ChartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.back_button = Button(text="Back", size_hint=(1, 0.1))
        self.back_button.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_button)
        self.draw_chart()
        self.add_widget(self.layout)

    def go_back(self, instance):
        self.manager.current = 'home'

    def draw_chart(self):
        data = read_transactions()
        if 'Category' in data.columns and not data.empty:
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')
            grouped = data.groupby('Category')['Amount'].sum()

            fig, ax = plt.subplots()
            ax.pie(grouped, labels=grouped.index, autopct='%1.1f%%')
            ax.set_title("Pengeluaran berdasarkan kategori")

            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            img = CoreImage(buf, ext='png')
            chart_image = Image(texture=img.texture)
            self.layout.add_widget(chart_image)
            plt.close(fig)
        else:
            self.layout.add_widget(Label(text="No data or 'Category' not found"))
