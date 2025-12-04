import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
dotenv_path = BASE_DIR / ".env"
print("DOTENV PATH:", dotenv_path, "exists?", dotenv_path.exists())

# load .env
load_dotenv(dotenv_path)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

TO_EMAIL = "izzynisa.26@gmail.com"  # kirim ke dirimu sendiri dulu

print("SMTP_HOST:", SMTP_HOST)
print("SMTP_PORT:", SMTP_PORT)
print("SMTP_USERNAME:", SMTP_USERNAME)

msg = EmailMessage()
msg["Subject"] = "Tes SMTP dari PGI Canteen"
msg["From"] = SMTP_USERNAME
msg["To"] = TO_EMAIL
msg.set_content("Kalau email ini masuk, konfigurasi SMTP sudah benar.")

try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
    print("✅ Email test terkirim, cek inbox/spam Gmail.")
except Exception as e:
    print("❌ Gagal kirim email:", repr(e))
    