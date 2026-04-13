import os
import requests
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("MAIL_PASSWORD")  # your SendGrid API key
FROM_EMAIL = os.getenv("MAIL_FROM")  # verified sender email


def send_otp_email(to_email, otp, name="User"):

    print("👉 send_otp_email() called")
    print("👉 FROM_EMAIL:", FROM_EMAIL)

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

    url = "https://api.sendgrid.com/v3/mail/send"

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {"email": FROM_EMAIL},
        "content": [
            {
                "type": "text/plain",
                "value": body
            }
        ]
    }

    try:
        print("👉 Sending email via SendGrid API...")

        response = requests.post(url, headers=headers, json=data)

        print("👉 Status Code:", response.status_code)
        print("👉 Response:", response.text)

        if response.status_code == 202:
            print("✅ OTP email sent successfully")
        else:
            print("❌ Failed to send email")

    except Exception as e:
        print("❌ Email error:", str(e))