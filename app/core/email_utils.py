import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

EMAIL = os.getenv("MAIL_USERNAME")
PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT"))

def send_otp_email(to_email, otp, name="User"):

    subject = "🔐 Password Reset OTP | Plant Care"

    body = f"""
Hi {name} 👋,

We received a request to reset your password for your Plant Care account 🌿

━━━━━━━━━━━━━━━━━━━━━━━
🔐 Your OTP Code: {otp}
━━━━━━━━━━━━━━━━━━━━━━━

⏳ This code is valid for 5 minutes.

If you did not request this, please ignore this email.

Stay secure,  
🌱 Plant Care Team
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()
        print("✅ OTP email sent successfully")

    except Exception as e:
        print("❌ Email error:", e)