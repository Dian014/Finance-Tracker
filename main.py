# 1. main.py
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.home import HomeScreen


class FinanceApp(MDApp):
    def build(self):
        self.title = "Personal Finance Tracker"

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(HomeScreen(name="home"))

        sm.current = "login"
        return sm


if __name__ == "__main__":
    FinanceApp().run()

# 2. core/lang_manager.py
import json
import os

class LangManager:
    def __init__(self, lang_code='id'):
        self.lang_code = lang_code
        self.translations = {}
        self.load_language()

    def load_language(self):
        lang_file = os.path.join('assets', f'{self.lang_code}.json')
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)

    def set_language(self, lang_code):
        self.lang_code = lang_code
        self.load_language()

    def translate(self, key):
        return self.translations.get(key, key)

# 3. core/auth.py
import json
import os

USERS_FILE = 'users.json'
current_user = None

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def register(username, password):
    users = load_users()
    if username in users:
        return False, "register_fail"
    users[username] = {"password": password, "is_premium": False}
    save_users(users)
    return True, "register_success"

def login(username, password):
    global current_user
    users = load_users()
    if username in users and users[username]["password"] == password:
        current_user = {"username": username, "is_premium": users[username]["is_premium"]}
        return True, "login_success"
    return False, "login_fail"

def logout():
    global current_user
    current_user = None

def is_premium():
    return current_user and current_user.get("is_premium", False)

def upgrade_to_premium():
    users = load_users()
    if current_user and current_user["username"] in users:
        users[current_user["username"]]["is_premium"] = True
        current_user["is_premium"] = True
        save_users(users)
        return True, "Upgrade berhasil"
    return False, "Gagal upgrade"

# 4. assets/en.json (simpan di folder assets/)
{
  "personal_finance_tracker": "Personal Finance Tracker",
  "login": "Login",
  "register": "Register",
  "username": "Username",
  "password": "Password",
  "login_success": "Login successful",
  "login_fail": "Incorrect username or password",
  "register_success": "Registration successful",
  "register_fail": "Username already exists",
  "upgrade_premium": "Upgrade to Premium",
  "premium_only": "This feature is only for premium users.",
  "add_transaction": "Add Transaction",
  "view_chart": "View Chart",
  "export_pdf": "Export PDF",
  "switch_to_register": "Switch to Register",
  "switch_to_login": "Switch to Login",
  "logout": "Logout",
  "error_fill_fields": "Username and password required",
  "success_pdf": "PDF report successfully created!"
}