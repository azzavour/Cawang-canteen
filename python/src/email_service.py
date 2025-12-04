import os
import smtplib
from email.message import EmailMessage
from typing import Optional
from urllib.parse import quote

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USERNAME or "no-reply@pgi-canteen.local")


def send_order_ticket_email(
    to_email: Optional[str],
    order_code: str,
    employee_name: str,
    employee_id: str,
    tenant_name: str,
    menu_label: str,
    queue_number: int,
    order_datetime_text: str,
    whatsapp_url: str,
) -> None:
    """
    Kirim email tiket pre-order ke karyawan.
    Kalau to_email kosong, fungsi akan langsung return tanpa error.
    """
    if not to_email:
        return

    subject = f"[PGI Canteen] Tiket Pre-Order #{queue_number}"

    plain_text = f"""
Tiket pre-order kantin Anda sudah tercatat di sistem.

ORDER   : {order_code}
Tanggal : {order_datetime_text}

Nama    : {employee_name} ({employee_id})
Kantin  : {tenant_name}
Menu    : {menu_label}
Nomor   : {queue_number}

Sebagai konfirmasi, mohon tunjukkan tiket ini saat mengambil makanan di kantin.
Jika perlu, Anda juga dapat membuka WhatsApp dengan link berikut:
{whatsapp_url}
""".strip()

    html_body = f"""
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color:#000;">
    <div style="max-width:600px;margin:0 auto;">
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px;">
        <div><strong>ORDER : </strong><span style="font-family:monospace;">{order_code}</span></div>
        <div>{order_datetime_text}</div>
      </div>

      <div style="border:2px solid #000;padding:16px;">
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
          <tr>
            <td width="50%" style="text-align:center;border-right:2px solid #000;padding:8px;">
              <div style="font-weight:bold;font-size:14px;margin-bottom:12px;">
                SCAN KONFIRMASI ORDER
              </div>
              <div style="margin-bottom:12px;">
                <img
                  src="https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={quote(whatsapp_url, safe='')}"
                  alt="QR WhatsApp"
                  width="180"
                  height="180"
                  style="display:block;margin:0 auto;border:1px solid #000;padding:6px;background:#fff;"
                />
              </div>
              <div style="margin-bottom:12px;">
                <a href="{whatsapp_url}">Klik di sini untuk buka WhatsApp</a>
              </div>
            </td>
            <td width="50%" style="text-align:center;padding:8px;">
              <div style="font-weight:bold;font-size:16px;text-transform:uppercase;">
                {employee_name}
              </div>
              <div style="font-size:13px;margin-bottom:12px;">{employee_id}</div>
              <div style="font-weight:bold;font-size:48px;margin-bottom:12px;">
                {queue_number}
              </div>
              <div style="font-weight:bold;font-size:14px;text-transform:uppercase;margin-bottom:4px;">
                {menu_label}
              </div>
              <div style="font-size:12px;">{tenant_name}</div>
            </td>
          </tr>
        </table>
      </div>

      <p style="margin-top:12px;font-size:12px;font-weight:bold;text-align:center;">
        Foto Bukti order ini untuk dilampirkan saat melakukan konfirmasi
      </p>
    </div>
  </body>
</html>
""".strip()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM or SMTP_USERNAME
    msg["To"] = to_email
    msg.set_content(plain_text)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
