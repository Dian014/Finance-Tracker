# midtrans_config.py
import base64

SERVER_KEY = 'Mid-server-erhBrXGnRqTEpwX54Gz5ahxj'
CLIENT_KEY = 'G060601779Mid-client-W14yjPUtOKeFGO0t'

BASE_URL = 'https://api.sandbox.midtrans.com/v2'  # Production: ganti 'sandbox' jadi 'midtrans'
AUTH_HEADER = {
    "Authorization": "Basic " + base64.b64encode(f"{SERVER_KEY}:".encode()).decode()
}
