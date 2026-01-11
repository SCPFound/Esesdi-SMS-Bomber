import customtkinter as ctk
import time
import threading
import requests
import hashlib
from sms import SendSms
from tkinter import messagebox

# ================= LİSANS =================
PASTEBIN_RAW_URL = "https://pastebin.com/raw/pZLSpNpu"

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def check_license_online(user_key):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(PASTEBIN_RAW_URL, headers=headers, timeout=10)
        r.raise_for_status()

        valid_hashes = [x.strip() for x in r.text.splitlines() if x.strip()]
        return sha256(user_key) in valid_hashes

    except:
        messagebox.showerror("Hata", "Lisans sunucusuna bağlanılamadı!")
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
        placeholder_text="Lisans...",
        width=240
    )
    entry.pack(pady=10)

    def submit():
        key = entry.get().strip()
        if not key:
            messagebox.showerror("Hata", "Lisans boş olamaz")
            return

        if check_license_online(key):
            lic.destroy()
            app.deiconify()
        else:
            messagebox.showerror("Hata", "Geçersiz Lisans")

    ctk.CTkButton(
        lic,
        text="Doğrula",
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
    text="MARKED BY ESESDI!",
    font=("Arial", 22, "bold")
).pack(pady=15)

tel_entry = ctk.CTkEntry(app, placeholder_text="Telefon (+90 EKLEME)")
tel_entry.pack(pady=10)

mail_entry = ctk.CTkEntry(app, placeholder_text="Mail (opsiyonel)")
mail_entry.pack(pady=10)

log_box = ctk.CTkTextbox(app, width=360, height=140)
log_box.pack(pady=10)

def hover_in(btn):
    btn.configure(width=220, height=38)

def hover_out(btn):
    btn.configure(width=200, height=32)

def click_anim(btn):
    btn.configure(width=180)
    btn.after(80, lambda: btn.configure(width=200))


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

sms_btn = ctk.CTkButton(
    app,
    text="🚀 SMS Gönder (Turbo)",
    width=200,
    height=32,
    command=lambda: (click_anim(sms_btn), TurboSMS())
)

sms_btn.pack(pady=8)

sms_btn.bind("<Enter>", lambda e: hover_in(sms_btn))
sms_btn.bind("<Leave>", lambda e: hover_out(sms_btn))

exit_btn = ctk.CTkButton(
    app,
    text="Çıkış",
    fg_color="red",
    width=200,
    height=32,
    command=app.destroy
)
exit_btn.pack(pady=15)

exit_btn.bind("<Enter>", lambda e: hover_in(exit_btn))
exit_btn.bind("<Leave>", lambda e: hover_out(exit_btn))


# ================= BAŞLAT =================
license_window()
app.mainloop()
