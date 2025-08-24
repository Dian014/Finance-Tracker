import json
import os

class LangManager:
    """
    Simple in-memory language manager.
    Use keys consistently across the app (lowercase, underscore).
    """
    LANGS = {
        "id": {
            "personal_finance_tracker": "Pengelola Keuangan Pribadi",
            "app_name": "Pengelola Keuangan Pribadi",
            "pemasukan": "Pemasukan",
            "pengeluaran": "Pengeluaran",
            "date": "Tanggal",
            "type": "Tipe",
            "category": "Kategori",
            "note": "Catatan",
            "amount": "Jumlah",
            "currency": "Mata Uang",
            "clear": "Bersihkan",
            "save": "Simpan",
            "transaction_history": "Riwayat Transaksi",
            "view_chart": "Lihat Grafik",
            "export_pdf": "Ekspor PDF",
            "upgrade_premium": "Upgrade Premium",
            "logout": "Keluar",
            "ok": "Oke",
            "weekly": "Mingguan",
            "monthly": "Bulanan",
            "cancel": "Batal",
            "status_free": "Status: Gratis",
            "status_premium": "Status: Premium",
            "fill_all_fields": "Isi semua field!",
            "error": "Kesalahan",
            "success": "Sukses",
            "transaction_saved": "Transaksi berhasil disimpan",
            "premium_only": "Hanya untuk Premium",
            "premium_feature_only": "Fitur ini hanya untuk pengguna Premium",
            "pdf_generated": "PDF berhasil dibuat",
            "choose_subscription_plan": "Pilih paket langganan",
            "total_per_category": "Total per Kategori",
            "jumlah": "Jumlah",
            "enter_number": "Masukkan angka",
            "confirm_delete": "Konfirmasi Hapus",
            "confirm_delete_text": "Hapus transaksi ini?",
            "delete": "Hapus",
            "no_transactions": "Belum ada transaksi",
            "transaction_deleted": "Transaksi dihapus",
            "cannot_delete": "Tidak dapat menghapus transaksi",
            "total_expense": "Total Pengeluaran",
            "balance": "Saldo",
            "transactions": "Transaksi",
        },
        "en": {
            "personal_finance_tracker": "Personal Finance Tracker",
            "app_name": "Personal Finance Tracker",
            "pemasukan": "Income",
            "pengeluaran": "Expense",
            "date": "Date",
            "type": "Type",
            "category": "Category",
            "note": "Note",
            "amount": "Amount",
            "currency": "Currency",
            "clear": "Clear",
            "save": "Save",
            "transaction_history": "Transaction History",
            "view_chart": "View Chart",
            "export_pdf": "Export PDF",
            "upgrade_premium": "Upgrade Premium",
            "logout": "Logout",
            "ok": "OK",
            "weekly": "Weekly",
            "monthly": "Monthly",
            "cancel": "Cancel",
            "status_free": "Status: Free",
            "status_premium": "Status: Premium",
            "fill_all_fields": "Fill all fields!",
            "error": "Error",
            "success": "Success",
            "transaction_saved": "Transaction saved successfully",
            "premium_only": "Premium Only",
            "premium_feature_only": "This feature is only for Premium users",
            "pdf_generated": "PDF generated successfully",
            "choose_subscription_plan": "Choose a subscription plan",
            "total_per_category": "Total per Category",
            "jumlah": "Amount",
            "enter_number": "Enter a number",
            "confirm_delete": "Confirm Delete",
            "confirm_delete_text": "Delete this transaction?",
            "delete": "Delete",
            "no_transactions": "No transactions yet",
            "transaction_deleted": "Transaction deleted",
            "cannot_delete": "Cannot delete transaction",
            "total_expense": "Total Expense",
            "balance": "Balance",
            "transactions": "Transactions",
        },
    }

    def __init__(self, lang_code="id"):
        self.lang_code = lang_code if lang_code in self.LANGS else "id"

    def translate(self, key: str) -> str:
        """Return translated string for key; fallback to key if missing."""
        if not key:
            return key
        return self.LANGS.get(self.lang_code, {}).get(key, key)

    def set_language(self, lang_code: str):
        if lang_code in self.LANGS:
            self.lang_code = lang_code
        else:
            raise ValueError(f"Language '{lang_code}' not supported")
