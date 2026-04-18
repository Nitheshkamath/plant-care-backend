import os
import requests
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("MAIL_PASSWORD")
FROM_EMAIL = os.getenv("MAIL_FROM")


def send_otp_email(to_email, otp, name="User"):

    print("👉 send_otp_email() called")

    subject = "PlantMate Password Reset Code"

    body = f"""
Hi {name},

We received a request to reset your password.

Your verification code is: {otp}

This code will expire in 5 minutes.

If you did not request this, you can safely ignore this email.

Thank you,
PlantMate Team
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
        "from": {
            "email": FROM_EMAIL,
            "name": "PlantMate"   # ✅ VERY IMPORTANT
        },
        "reply_to": {
            "email": FROM_EMAIL
        },
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

        if response.status_code == 202:
            print("✅ OTP email sent successfully")
        else:
            print("❌ Failed:", response.text)

    except Exception as e:
        print("❌ Email error:", str(e))