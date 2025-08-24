import pandas as pd
import os
from datetime import datetime
from core.auth import get_current_user

def get_user_transaction_file():
    user = get_current_user()
    if not user:
        raise Exception("Tidak ada user yang login.")
    username = user["username"]
    os.makedirs("transactions", exist_ok=True)
    return f"transactions/user_{username}.xlsx"

def save_to_excel(data, file_path=None):
    if not file_path:
        file_path = get_user_transaction_file()

    for d in data:
        if "Date" not in d or not d["Date"]:
            d["Date"] = datetime.now().strftime('%Y-%m-%d')

    df = pd.DataFrame(data)

    if os.path.exists(file_path):
        try:
            existing = pd.read_excel(file_path)
        except Exception as e:
            print(f"[ERROR] Gagal membaca file lama: {e}")
            existing = pd.DataFrame()
        df = pd.concat([existing, df], ignore_index=True)

    try:
        df.to_excel(file_path, index=False)
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan data: {e}")

def read_transactions(file_path=None):
    if not file_path:
        try:
            file_path = get_user_transaction_file()
        except Exception as e:
            print(f"[ERROR] {e}")
            return pd.DataFrame(columns=["Amount", "Note", "Category", "Date"])

    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            if 'Date' not in df.columns:
                df['Date'] = pd.NaT
            else:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            return df
        except Exception as e:
            print(f"[ERROR] Gagal membaca transaksi: {e}")
            return pd.DataFrame(columns=["Amount", "Note", "Category", "Date"])
    else:
        return pd.DataFrame(columns=["Amount", "Note", "Category", "Date"])

def delete_transaction_by_index(index, file_path=None):
    if not file_path:
        file_path = get_user_transaction_file()

    if not os.path.exists(file_path):
        return False

    try:
        df = pd.read_excel(file_path)
        if index < 0 or index >= len(df):
            return False
        df = df.drop(index).reset_index(drop=True)
        df.to_excel(file_path, index=False)
        return True
    except Exception as e:
        print(f"[ERROR] Gagal menghapus transaksi: {e}")
        return False
