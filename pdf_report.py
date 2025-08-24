import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from datetime import datetime, timedelta
from core.excel_exporter import read_transactions   # ✅ diperbaiki
from core.auth import get_current_user

class PDFReport:
    def __init__(self):
        pass

    def generate_report(self, output_path="monthly_report.pdf"):
        user = get_current_user()
        if not user:
            raise Exception("Tidak ada user login.")

        data = read_transactions()
        if data.empty:
            raise ValueError("Tidak ada transaksi sama sekali.")

        data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
        data['Category'] = data['Category'].fillna('Lainnya')
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce').fillna(pd.Timestamp.now())

        now = datetime.now()

        monthly_data = data[(data['Date'].dt.year == now.year) & (data['Date'].dt.month == now.month)]
        weekly_data = data[data['Date'] >= now - timedelta(days=7)]

        if monthly_data.empty:
            raise ValueError("Tidak ada transaksi bulan ini")

        grouped = monthly_data.groupby('Category')['Amount'].sum()
        daily_sum = monthly_data.groupby(monthly_data['Date'].dt.date)['Amount'].sum()

        # Pie Chart
        fig1, ax1 = plt.subplots()
        ax1.pie(grouped, labels=grouped.index, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Pengeluaran Bulanan per Kategori")
        pie_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        fig1.savefig(pie_path)
        plt.close(fig1)

        # Bar Chart
        fig2, ax2 = plt.subplots()
        ax2.bar(daily_sum.index, daily_sum.values, color='skyblue')
        ax2.set_title("Pengeluaran Harian")
        ax2.set_xlabel("Tanggal")
        ax2.set_ylabel("Jumlah (Rp)")
        ax2.tick_params(axis='x', rotation=45)
        bar_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        fig2.savefig(bar_path)
        plt.close(fig2)

        # PDF generation
        pdf = FPDF()
        pdf.add_page()

        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=30)

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Laporan Keuangan Bulanan", ln=True, align='C')
        pdf.ln(10)

        total_month = monthly_data['Amount'].sum()
        total_week = weekly_data['Amount'].sum()

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"User: {user['username']}", ln=True)
        pdf.cell(0, 10, f"Periode: {now.strftime('%B %Y')}", ln=True)
        pdf.cell(0, 10, f"Total Bulanan: Rp {total_month:,.2f}", ln=True)
        pdf.cell(0, 10, f"Total Mingguan: Rp {total_week:,.2f}", ln=True)
        pdf.ln(10)

        pdf.image(pie_path, x=30, w=150)
        pdf.ln(10)
        pdf.image(bar_path, x=30, w=150)
        pdf.ln(10)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Rincian Pengeluaran:", ln=True)
        pdf.set_font("Arial", size=12)
        for cat, amount in grouped.items():
            pdf.cell(0, 8, f"{cat}: Rp {amount:,.2f}", ln=True)

        pdf.ln(20)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "Ditandatangani secara digital oleh FinanceTracker", ln=True, align='R')
        pdf.cell(0, 10, now.strftime("%Y-%m-%d %H:%M:%S"), ln=True, align='R')

        pdf.output(output_path)
        os.remove(pie_path)
        os.remove(bar_path)
