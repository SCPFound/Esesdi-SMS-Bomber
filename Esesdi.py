import customtkinter as ctk
import os as system
import time
import threading
import time
import hashlib

from colorama import Fore
from sms import SendSms
from tkinter import messagebox

# ---- LİSANS ----
LICENSE_HASH = hashlib.sha256(
    "ESESDI-ASD2-ASDN-23VA".encode() and "ESESDI-2DA2-BOWC-MB74".encode() and "test".encode()
).hexdigest()

def check_license(key):
    return hashlib.sha256(key.encode()).hexdigest() == LICENSE_HASH


def license_window():
    lic = ctk.CTk()
    lic.title("Lisans Doğrulama")
    lic.geometry("360x220")
    lic.resizable(False, False)

    label = ctk.CTkLabel(
        lic,
        text="Lisans Anahtarı Gir",
        font=("Arial", 18, "bold")
    )
    label.pack(pady=20)

    entry = ctk.CTkEntry(
        lic,
        placeholder_text="XXXX-XXXX-XXXX",
        width=240
    )
    entry.pack(pady=10)

    def submit():
        if check_license(entry.get().strip()):
            lic.destroy()
            app.deiconify()  # ana pencereyi aç
        else:
            messagebox.showerror("Hata", "Geçersiz Lisans Anahtarı")

    btn = ctk.CTkButton(
        lic,
        text="GİRİŞ",
        command=submit
    )
    btn.pack(pady=20)

    lic.mainloop()


def sleep(x):
    time.sleep(x)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("SMS Paneli")
app.geometry("420x520")
app.resizable(False, False)

servisler_sms = []
for attribute in dir(SendSms):
    attribute_value = getattr(SendSms, attribute)
    if callable(attribute_value):
        if attribute.startswith('__') == False:
            servisler_sms.append(attribute)

# ---------- BAŞLIK ----------
title = ctk.CTkLabel(
    app,
    text="DIRECTED BY ESESDI!",
    font=("Arial", 22, "bold")
)
title.pack(pady=15)

# ---------- INPUTLAR ----------
tel_entry = ctk.CTkEntry(app, placeholder_text="Telefon (5xxxxxxxxx)")
tel_entry.pack(pady=10)

mail_entry = ctk.CTkEntry(app, placeholder_text="Mail (opsiyonel)")
mail_entry.pack(pady=10)

adet_entry = ctk.CTkEntry(app, placeholder_text="SMS Adedi (boş = sonsuz)")
adet_entry.pack(pady=10)

aralik_entry = ctk.CTkEntry(app, placeholder_text="Gönderim Aralığı (sn)")
aralik_entry.pack(pady=10)

# ---------- LOG ----------
log_box = ctk.CTkTextbox(app, width=360, height=140)
log_box.pack(pady=10)

def log(msg):
    log_box.insert("end", msg + "\n")
    log_box.see("end")

# ---------- MOCK SMS ----------
def fake_sms_send():
    log("📨 SMS gönderildi (TEST)")

# ---------- NORMAL MOD ----------
def normal_sms():
    tel = tel_entry.get()
    if len(tel) != 10 or not tel.isdigit():
        messagebox.showerror("Hata", "Telefon numarası hatalı")
        return

    try:
        aralik = int(aralik_entry.get())
    except:
        messagebox.showerror("Hata", "Aralık sayısal olmalı")
        return

    adet = adet_entry.get()
    adet = int(adet) if adet.isdigit() else None

    def run():
        sayac = 0
        while adet is None or sayac < adet:
            fake_sms_send()
            sayac += 1
            time.sleep(aralik)

    threading.Thread(target=run, daemon=True).start()

# ---------- TURBO MOD ----------
def TurboSMS():
    tel_no = tel_entry.get().strip()
    mail = mail_entry.get().strip()

    if not tel_no.isdigit() or len(tel_no) != 10:
        log("Telefon numarası hatalı!")
        return

    log("⚡ Turbo SMS başlatıldı")
    log("🥀 Esesdi SMS!")

    send_sms = SendSms(tel_no, mail)
    dur = threading.Event()
    def run():
        while not dur.is_set():
            threads = []
            for fonk in servisler_sms:
                t = threading.Thread(
                    target=getattr(send_sms, fonk),
                    daemon=True
                )
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            time.sleep(0.5)  # GUI'yi boğmamak için

    threading.Thread(target=run, daemon=True).start()


# ---------- BUTONLAR ----------
btn_normal = ctk.CTkButton(app, text="SMS Gönder (Normal)", command=normal_sms)
btn_normal.pack(pady=8)

btn_turbo = ctk.CTkButton(app, text="SMS Gönder (Turbo)", command=TurboSMS)
btn_turbo.pack(pady=8)

btn_exit = ctk.CTkButton(app, text="Çıkış", fg_color="red", command=app.destroy)
btn_exit.pack(pady=15)

license_window()
app.mainloop()
