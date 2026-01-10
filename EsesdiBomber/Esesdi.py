import customtkinter as ctk
import time
import threading
import requests
import hashlib
import os
import sys
from sms import SendSms
from tkinter import messagebox

# ======== GÜNCELLEME AYAR ========
LOCAL_VERSION = "1.0.2"

VERSION_URL = "https://raw.githubusercontent.com/SCPFound/Esesdi-SMS-Bomber/refs/heads/main/EsesdiBomber/version.txt"
UPDATE_URL  = "https://raw.githubusercontent.com/SCPFound/Esesdi-SMS-Bomber/refs/heads/main/EsesdiBomber/Esesdi.py"

def check_update():
    try:
        r = requests.get(VERSION_URL, timeout=5)
        r.raise_for_status()
        online = r.text.strip()

        if online != LOCAL_VERSION:
            if messagebox.askyesno(
                "Güncelleme Var",
                f"Yeni sürüm bulundu ({online})\nGüncellemek ister misin?"
            ):
                download_update()
    except:
        pass

def download_update():
    try:
        r = requests.get(UPDATE_URL, timeout=10)
        r.raise_for_status()

        new_file = sys.argv[0] + ".new"
        with open(new_file, "wb") as f:
            f.write(r.content)

        os.replace(new_file, sys.argv[0])
        messagebox.showinfo("Güncellendi", "Program güncellendi, yeniden başlatılıyor")
        os.execv(sys.executable, ["python"] + sys.argv)

    except Exception as e:
        messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}")


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
        placeholder_text="XXXX-XXXX-XXXX",
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

check_update()

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
check_update()
license_window()
app.mainloop()
