import customtkinter as ctk
import time
import threading
import requests
import hashlib
from sms import SendSms
from tkinter import messagebox

import requests
import hashlib
import os
from tkinter import messagebox

PASTEBIN_RAW_URL = "https://pastebin.com/raw/pZLSpNpu"
CACHE_FILE = "license.cache"

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def save_cache(license_hash):
    with open(CACHE_FILE, "w") as f:
        f.write(license_hash)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return f.read().strip()
    return None

def check_license(user_key):
    user_hash = sha256(user_key)

    # 1️⃣ ONLINE KONTROL
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(PASTEBIN_RAW_URL, headers=headers, timeout=7)
        r.raise_for_status()

        valid_hashes = [x.strip() for x in r.text.splitlines() if x.strip()]

        if user_hash in valid_hashes:
            save_cache(user_hash)  # cache yaz
            return True

    except:
        pass  # offline'a düş

    # 2️⃣ OFFLINE CACHE
    cached = load_cache()
    if cached == user_hash:
        return True

    return False

def license_window():
    lic = ctk.CTk()
    lic.title("Lisans Doğrulama")
    lic.geometry("360x220")
    lic.resizable(False, False)

    ctk.CTkLabel(
        lic,
        text="Lisans Anahtarı Gir",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    entry = ctk.CTkEntry(
        lic,
        placeholder_text="XXXX-XXXX-XXXX",
        width=240
    )
    entry.pack(pady=10)

    def submit():
        key = entry.get().strip()
        if not key:
            messagebox.showerror("Hata", "Lisans boş olamaz")
            return

        if check_license(key):
            lic.destroy()
            app.deiconify()
        else:
            messagebox.showerror(
                "Hata",
                "Geçersiz lisans veya internet yok!"
            )

    ctk.CTkButton(
        lic,
        text="DOĞRULA",
        command=submit
    ).pack(pady=20)

    lic.mainloop()


# ================= PANEL =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.withdraw()
app.title("SMS Paneli")
app.geometry("420x520")
app.resizable(False, False)

servisler_sms = [
    x for x in dir(SendSms)
    if callable(getattr(SendSms, x)) and not x.startswith("__")
]

ctk.CTkLabel(
    app,
    text="DIRECTED BY ESESDI!",
    font=("Arial", 22, "bold")
).pack(pady=15)

tel_entry = ctk.CTkEntry(app, placeholder_text="Telefon (10 haneli)")
tel_entry.pack(pady=10)

mail_entry = ctk.CTkEntry(app, placeholder_text="Mail (opsiyonel)")
mail_entry.pack(pady=10)

log_box = ctk.CTkTextbox(app, width=360, height=140)
log_box.pack(pady=10)

def log(msg):
    log_box.insert("end", msg + "\n")
    log_box.see("end")

def TurboSMS():
    tel = tel_entry.get().strip()
    if not tel.isdigit() or len(tel) != 10:
        log("Telefon hatalı")
        return

    log("⚡ Turbo SMS başladı")
    send_sms = SendSms(tel, mail_entry.get().strip())

    def run():
        while True:
            for fn in servisler_sms:
                threading.Thread(
                    target=getattr(send_sms, fn),
                    daemon=True
                ).start()
            time.sleep(0.5)

    threading.Thread(target=run, daemon=True).start()

ctk.CTkButton(app, text="SMS Gönder (Turbo)", command=TurboSMS).pack(pady=8)
ctk.CTkButton(app, text="Çıkış", fg_color="red", command=app.destroy).pack(pady=15)

# ================= BAŞLAT =================
license_window()
app.mainloop()
