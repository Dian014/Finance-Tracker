# server.py
from flask import Flask, request, jsonify
import midtransclient
import json
import os

app = Flask(__name__)

# Load or inisialisasi data user dari file
DATA_FILE = "users.json"

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

users_db = load_users()

# Konfigurasi Midtrans (pakai sandbox)
snap = midtransclient.Snap(
    is_production=False,
    server_key="Mid-server-erhBrXGnRqTEpwX54Gz5ahxj",
    client_key="G060601779Mid-client-W14yjPUtOKeFGO0t"
)

@app.route("/upgrade", methods=["POST"])
def upgrade():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username wajib diberikan"}), 400

    if username not in users_db:
        return jsonify({"error": "User tidak ditemukan"}), 404

    # Buat transaksi pembayaran Midtrans
    transaction_details = {
        "order_id": f"premium-{username}",
        "gross_amount": 50000  # Contoh harga upgrade Rp 50.000
    }
    customer_details = {
        "first_name": username
    }
    params = {
        "transaction_details": transaction_details,
        "customer_details": customer_details,
        "enabled_payments": ["credit_card","gopay","bank_transfer"],
        "expiry": {
            "start_time": "2025-07-04T10:00:00+07:00",
            "unit": "minute",
            "duration": 60
        }
    }

    try:
        payment_url = snap.create_transaction(params)["redirect_url"]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"snap_url": payment_url})

@app.route("/midtrans/callback", methods=["POST"])
def callback():
    notification = request.json

    order_id = notification.get("order_id")
    transaction_status = notification.get("transaction_status")
    fraud_status = notification.get("fraud_status")

    if order_id and transaction_status == "capture" and fraud_status == "accept":
        # extract username dari order_id (format premium-username)
        username = order_id.replace("premium-", "")
        if username in users_db:
            users_db[username]["is_premium"] = True
            save_users(users_db)
            return jsonify({"message": "User upgraded to premium"}), 200
        else:
            return jsonify({"error": "User tidak ditemukan"}), 404

    return jsonify({"message": "Transaksi belum selesai atau tidak valid"}), 200

if __name__ == "__main__":
    app.run(debug=True)
