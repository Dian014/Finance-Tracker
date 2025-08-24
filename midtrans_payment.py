from midtransclient import Snap
import time
import webbrowser

IS_PRODUCTION = True
SERVER_KEY = "Mid-server-erhBrXGnRqTEpwX54Gz5ahxj"

snap = Snap(
    is_production=IS_PRODUCTION,
    server_key=SERVER_KEY
)

def pay_with_midtrans(plan):
    order_id = f"{plan}-{int(time.time())}"
    price = 7000 if plan == "weekly" else 15000

    params = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": price
        },
        "item_details": [{
            "id": plan,
            "price": price,
            "quantity": 1,
            "name": f"Premium Plan ({plan})"
        }]
    }

    transaction = snap.create_transaction(params)
    url = transaction["redirect_url"]
    print(f"[MIDTRANS] URL pembayaran: {url}")

    # Buka otomatis di browser
    webbrowser.open(url)
