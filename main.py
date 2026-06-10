import os
import sys
import sqlite3
import random
import pyperclip
import customtkinter as ctk
from PIL import Image
from cryptography.fernet import Fernet
import string

# ---------------------------- APP ICON INSTRUCTIONS ------------------------ #
# To fully implement the custom App Icon:
# 1. Save your high-res icon as `assets/app_icon.png`
# 2. For macOS: Convert to .icns (e.g. `sips -s format icns assets/app_icon.png --out assets/icon.icns`)
# 3. For Windows: Convert to .ico (e.g. using an online converter or Pillow)
# 4. When building with PyInstaller, use the `--icon` flag:
#    macOS:   pyinstaller --windowed --name MyPass --icon assets/icon.icns --add-data "assets:assets" ... main.py
#    Windows: pyinstaller --windowed --name MyPass --icon assets/icon.ico --add-data "assets;assets" ... main.py

# ---------------------------- CONFIG ------------------------------- #
import platform

os_name = platform.system()
if os_name == "Darwin":
    APP_FONT = "SF Pro"
elif os_name == "Windows":
    APP_FONT = "Segoe UI"
else:
    APP_FONT = "Arial"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_COLOR = "#1A1A1A"
CARD_COLOR = "#252525"
INPUT_COLOR = "#2A2A2A"
BORDER_COLOR = "#333333"
FOCUS_BORDER = "#4F8CFF"
ACCENT_COLOR = "#3B82F6"
MUTED_TEXT = "#8E8E93"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------------------- DATA & ENCRYPTION ----------------------------- #
def get_data_dir():
    home = os.path.expanduser("~")
    data_dir = os.path.join(home, ".password_manager_data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

DATA_DIR = get_data_dir()
DB_FILE = os.path.join(DATA_DIR, "vault.db")
KEY_FILE = os.path.join(DATA_DIR, "vault.key")

def get_encryption_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    with open(KEY_FILE, "rb") as f:
        return f.read()

fernet = Fernet(get_encryption_key())

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_total_credentials():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM credentials")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ---------------------------- APP CLASS ------------------------------- #
class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG_COLOR)
        
        self.title("MyPass")
        self.geometry("720x760")
        self.minsize(720, 760)
        self.maxsize(720, 760)
        
        # Load Window Icon if exists
        try:
            if os_name == "Windows":
                self.iconbitmap(resource_path("assets/icon.ico"))
            else:
                # Tkinter standard iconphoto for Linux/macOS
                icon_img = Image.open(resource_path("assets/logo.png"))
                import tkinter as tk
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(icon_img)
                self.wm_iconphoto(True, photo)
        except Exception:
            pass
            
        self.password_var = ctk.StringVar()
        self.password_var.trace_add("write", self.update_strength_bar)
        
        self.setup_icons()
        self.setup_ui()
        self.bind_shortcuts()
        self.check_empty_state()
        
    def setup_icons(self):
        def load_icon(name):
            try:
                return ctk.CTkImage(Image.open(resource_path(f"assets/{name}.png")), size=(18, 18))
            except Exception:
                return None
                
        self.icons = {
            "eye": load_icon("eye"),
            "eye_off": load_icon("eye-off"),
            "copy": load_icon("copy"),
            "search": load_icon("search"),
        }
        
        try:
            self.logo_img = ctk.CTkImage(Image.open(resource_path("assets/app_icon.png")), size=(48, 48))
        except Exception:
            try:
                self.logo_img = ctk.CTkImage(Image.open(resource_path("assets/logo.png")), size=(48, 48))
            except Exception:
                self.logo_img = None

    def setup_ui(self):
        # Centered Card (occupying almost the whole window)
        self.card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.card.pack(expand=True, fill="both", padx=24, pady=24)
        
        # Header (Logo + Title)
        self.header_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.header_frame.pack(pady=(30, 20))
        
        if self.logo_img:
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_img, text="")
            self.logo_label.pack(side="left", padx=(0, 15))
            
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.pack(side="left")
        
        self.title_lbl = ctk.CTkLabel(self.title_frame, text="MyPass", font=(APP_FONT, 22, "bold"), text_color="white")
        self.title_lbl.pack(anchor="w")
        self.subtitle_lbl = ctk.CTkLabel(self.title_frame, text="Secure Password Vault", font=(APP_FONT, 12), text_color=MUTED_TEXT)
        self.subtitle_lbl.pack(anchor="w")

        # Focus handler helper
        def on_focus_in(event, entry):
            entry.configure(border_color=FOCUS_BORDER)
        def on_focus_out(event, entry):
            entry.configure(border_color=BORDER_COLOR)
            
        # Website Section
        self.web_lbl = ctk.CTkLabel(self.card, text="Website", font=(APP_FONT, 12), text_color=MUTED_TEXT)
        self.web_lbl.pack(anchor="w", padx=40, pady=(10, 2))
        
        self.website_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.website_frame.pack(fill="x", padx=40)
        
        self.website_entry = ctk.CTkEntry(self.website_frame, placeholder_text="amazon.com", height=40, fg_color=INPUT_COLOR, border_color=BORDER_COLOR, corner_radius=8, border_width=1)
        self.website_entry.pack(side="left", expand=True, fill="x")
        self.website_entry.bind("<FocusIn>", lambda e: on_focus_in(e, self.website_entry))
        self.website_entry.bind("<FocusOut>", lambda e: on_focus_out(e, self.website_entry))
        
        self.search_btn = ctk.CTkButton(self.website_frame, text="", image=self.icons.get("search"), width=40, height=40, fg_color=INPUT_COLOR, hover_color=BORDER_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=8, cursor="hand2", command=self.find_password)
        self.search_btn.pack(side="right", padx=(8, 0))
        
        # Email Section
        self.email_lbl = ctk.CTkLabel(self.card, text="Email or Username", font=(APP_FONT, 12), text_color=MUTED_TEXT)
        self.email_lbl.pack(anchor="w", padx=40, pady=(15, 2))
        
        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="john@example.com", height=40, fg_color=INPUT_COLOR, border_color=BORDER_COLOR, corner_radius=8, border_width=1)
        self.email_entry.pack(fill="x", padx=40)
        self.email_entry.bind("<FocusIn>", lambda e: on_focus_in(e, self.email_entry))
        self.email_entry.bind("<FocusOut>", lambda e: on_focus_out(e, self.email_entry))
        
        # Password Section
        self.pwd_lbl = ctk.CTkLabel(self.card, text="Password", font=(APP_FONT, 12), text_color=MUTED_TEXT)
        self.pwd_lbl.pack(anchor="w", padx=40, pady=(15, 2))
        
        self.pwd_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.pwd_frame.pack(fill="x", padx=40)
        
        self.password_entry = ctk.CTkEntry(self.pwd_frame, placeholder_text="Generate or enter password", height=40, fg_color=INPUT_COLOR, border_color=BORDER_COLOR, corner_radius=8, show="*", border_width=1, textvariable=self.password_var)
        self.password_entry.pack(side="left", expand=True, fill="x")
        self.password_entry.bind("<FocusIn>", lambda e: on_focus_in(e, self.password_entry))
        self.password_entry.bind("<FocusOut>", lambda e: on_focus_out(e, self.password_entry))
        
        self.show_pwd = False
        self.eye_btn = ctk.CTkButton(self.pwd_frame, text="", image=self.icons.get("eye"), width=40, height=40, fg_color=INPUT_COLOR, hover_color=BORDER_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=8, cursor="hand2", command=self.toggle_password)
        self.eye_btn.pack(side="left", padx=(8, 0))
        
        self.copy_btn = ctk.CTkButton(self.pwd_frame, text="", image=self.icons.get("copy"), width=40, height=40, fg_color=INPUT_COLOR, hover_color=BORDER_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=8, cursor="hand2", command=self.copy_password)
        self.copy_btn.pack(side="left", padx=(8, 0))
        
        # Strength Bar & Text
        self.strength_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.strength_frame.pack(fill="x", padx=40, pady=(10, 0))
        
        self.strength_bar = ctk.CTkProgressBar(self.strength_frame, height=4, progress_color=BORDER_COLOR, fg_color=BORDER_COLOR, corner_radius=2)
        self.strength_bar.pack(fill="x")
        self.strength_bar.set(0)
        
        self.strength_lbl = ctk.CTkLabel(self.strength_frame, text="", font=(APP_FONT, 11), text_color=MUTED_TEXT, height=14)
        self.strength_lbl.pack(anchor="w", pady=(4, 0))
        
        # Buttons
        self.btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=40, pady=(20, 20))
        
        self.gen_btn = ctk.CTkButton(self.btn_frame, text="Generate", height=40, fg_color=INPUT_COLOR, hover_color=BORDER_COLOR, text_color="white", border_width=1, border_color=BORDER_COLOR, corner_radius=8, cursor="hand2", font=(APP_FONT, 13, "bold"), command=self.generate_password)
        self.gen_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))
        
        self.save_btn = ctk.CTkButton(self.btn_frame, text="Save", height=40, fg_color=ACCENT_COLOR, hover_color="#2563EB", text_color="white", corner_radius=8, cursor="hand2", font=(APP_FONT, 13, "bold"), command=self.save_password)
        self.save_btn.pack(side="right", expand=True, fill="x", padx=(6, 0))
        
        # Helper Text
        self.helper_lbl = ctk.CTkLabel(self.card, text="Passwords are securely stored locally.", font=(APP_FONT, 11), text_color=MUTED_TEXT)
        self.helper_lbl.pack(side="bottom", pady=(0, 25))

        # Footer Metadata & Empty State
        self.footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.footer.pack(fill="x", side="bottom", padx=20, pady=10)
        
        self.version_lbl = ctk.CTkLabel(self.footer, text="MyPass v1.0", font=(APP_FONT, 11), text_color=MUTED_TEXT)
        self.version_lbl.pack(side="left")
        
        self.empty_state_lbl = ctk.CTkLabel(self.footer, text="", font=(APP_FONT, 12), text_color=MUTED_TEXT)
        self.empty_state_lbl.pack(side="right")
        
        # Toast Container (Hidden initially)
        self.toast_frame = ctk.CTkFrame(self, fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=16)
        self.toast_lbl = ctk.CTkLabel(self.toast_frame, text="", font=(APP_FONT, 13, "bold"), text_color="white")
        self.toast_lbl.pack(padx=20, pady=8)

    def check_empty_state(self):
        count = get_total_credentials()
        if count == 0:
            self.empty_state_lbl.configure(text="No passwords saved yet. Start by adding your first credential.")
        else:
            self.empty_state_lbl.configure(text=f"{count} credentials securely stored.")

    def bind_shortcuts(self):
        self.bind("<Command-s>", lambda event: self.save_password())
        self.bind("<Command-f>", lambda event: self.find_password())
        self.bind("<Command-g>", lambda event: self.generate_password())
        self.bind("<Return>", lambda event: self.save_password())
        # Support Windows Ctrl shortcuts too
        self.bind("<Control-s>", lambda event: self.save_password())
        self.bind("<Control-f>", lambda event: self.find_password())
        self.bind("<Control-g>", lambda event: self.generate_password())

    def flash_error(self, entry):
        # Flash the border red for a split second to indicate error
        original = entry.cget("border_color")
        entry.configure(border_color="#EF4444")
        self.after(400, lambda: entry.configure(border_color=original))

    def show_toast(self, text, is_error=False):
        color = "#EF4444" if is_error else "#10B981"
        self.toast_lbl.configure(text=text, text_color=color)
        # Position toast at the bottom center of the window
        self.toast_frame.place(relx=0.5, rely=0.92, anchor="center")
        self.after(3000, lambda: self.toast_frame.place_forget())

    def toggle_password(self):
        self.show_pwd = not self.show_pwd
        self.password_entry.configure(show="" if self.show_pwd else "*")
        if self.icons.get("eye") and self.icons.get("eye_off"):
            self.eye_btn.configure(image=self.icons["eye_off"] if self.show_pwd else self.icons["eye"])

    def copy_password(self):
        pwd = self.password_entry.get()
        if pwd:
            pyperclip.copy(pwd)
            self.show_toast("✓ Password Copied")
        else:
            self.flash_error(self.password_entry)

    def update_strength_bar(self, *args):
        pwd = self.password_entry.get()
        if not pwd:
            self.strength_bar.set(0)
            self.strength_bar.configure(progress_color=BORDER_COLOR)
            self.strength_lbl.configure(text="")
            return
            
        score = 0
        if len(pwd) >= 8: score += 1
        if len(pwd) >= 12: score += 1
        if any(c.isupper() for c in pwd): score += 1
        if any(c.islower() for c in pwd): score += 1
        if any(c.isdigit() for c in pwd): score += 1
        if any(c in string.punctuation for c in pwd): score += 1
        
        strength = min(score / 6.0, 1.0)
        self.strength_bar.set(strength)
        
        if strength < 0.4:
            self.strength_bar.configure(progress_color="#EF4444")
            self.strength_lbl.configure(text="Weak Password", text_color="#EF4444")
        elif strength < 0.8:
            self.strength_bar.configure(progress_color="#F59E0B")
            self.strength_lbl.configure(text="Medium Password", text_color="#F59E0B")
        else:
            self.strength_bar.configure(progress_color="#10B981")
            self.strength_lbl.configure(text="Strong Password", text_color="#10B981")

    def generate_password(self):
        letters = string.ascii_letters
        numbers = string.digits
        symbols = "!#$%&()*+"
        
        pwd_list = (
            [random.choice(letters) for _ in range(8)] +
            [random.choice(numbers) for _ in range(3)] +
            [random.choice(symbols) for _ in range(3)]
        )
        random.shuffle(pwd_list)
        pwd = "".join(pwd_list)
        
        self.password_entry.delete(0, 'end')
        self.password_entry.insert(0, pwd)
        self.copy_password()

    def save_password(self):
        website = self.website_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not website: self.flash_error(self.website_entry)
        if not email: self.flash_error(self.email_entry)
        if not password: self.flash_error(self.password_entry)
            
        if not website or not email or not password:
            self.show_toast("⚠ Please fill all fields", is_error=True)
            return
            
        encrypted_pwd = fernet.encrypt(password.encode()).decode()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM credentials WHERE website=?", (website,))
        result = cursor.fetchone()
        
        if result:
            cursor.execute("UPDATE credentials SET email=?, password=? WHERE website=?", (email, encrypted_pwd, website))
            self.show_toast("✓ Updated Securely")
        else:
            cursor.execute("INSERT INTO credentials (website, email, password) VALUES (?, ?, ?)", (website, email, encrypted_pwd))
            self.show_toast("✓ Saved Securely")
            
        conn.commit()
        conn.close()
        
        self.website_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        
        # Reset strength bar smoothly
        self.password_var.set("")
        self.check_empty_state()

    def find_password(self):
        website = self.website_entry.get().strip()
        if not website:
            self.flash_error(self.website_entry)
            self.show_toast("⚠ Enter website to search", is_error=True)
            return
            
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT email, password FROM credentials WHERE website=?", (website,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            email, encrypted_pwd = result
            password = fernet.decrypt(encrypted_pwd.encode()).decode()
            
            # Simulate smooth autofill
            self.email_entry.delete(0, 'end')
            self.email_entry.insert(0, email)
            self.password_entry.delete(0, 'end')
            self.password_entry.insert(0, password)
            self.show_toast("✓ Entry Found")
        else:
            self.show_toast("⚠ No Saved Credentials", is_error=True)
            self.email_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')

if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()