import sys
import os
import json

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# File penyimpanan user
USERS_FILE = resource_path(os.path.join("core", "users.json"))
current_user = None


# ================= USER FILE HANDLER =================
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Reset file jika corrupt
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


# ================= AUTH FUNCTION =================
def register(username: str, password: str):
    users = load_users()
    if username in users:
        return False, "user_exists"   # gunakan key agar bisa diterjemahkan di LangManager

    users[username] = {
        "password": password,
        "is_premium": False
    }
    save_users(users)
    return True, "register_success"


def login(username: str, password: str):
    global current_user
    users = load_users()
    user = users.get(username)

    if user and user["password"] == password:
        current_user = {
            "username": username,
            "is_premium": user.get("is_premium", False)
        }
        print(f"[LOGIN] Pengguna '{username}' berhasil login.")
        return True, "login_success"

    return False, "login_failed"


def logout():
    global current_user
    if current_user:
        print(f"[LOGOUT] Pengguna '{current_user['username']}' logout.")
    else:
        print("[LOGOUT] Tidak ada user login.")
    current_user = None


def is_premium():
    return current_user.get("is_premium", False) if current_user else False


def get_current_user():
    return current_user


def upgrade_to_premium():
    global current_user
    if current_user:
        users = load_users()
        username = current_user["username"]
        users[username]["is_premium"] = True
        save_users(users)
        current_user["is_premium"] = True
        print(f"[PREMIUM] Pengguna '{username}' di-upgrade ke premium.")
        return True, "upgrade_success"
    return False, "no_user_logged_in"
