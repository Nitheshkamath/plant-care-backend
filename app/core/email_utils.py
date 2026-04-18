import os
import requests
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("MAIL_PASSWORD")
FROM_EMAIL = os.getenv("MAIL_FROM")
APP_NAME = "PlantMate"


def send_otp_email(to_email: str, otp: str, name: str = "User") -> bool:
    """
    Sends OTP email using SendGrid API
    Returns True if sent successfully, else False
    """

    print("📧 send_otp_email() triggered")

    subject = f"{APP_NAME} - Password Reset Code"

    # ✅ Plain text fallback
    text_content = f"""
Hi {name},

Your password reset code is: {otp}

This code is valid for 5 minutes.

If you did not request this, please ignore this email.

Thanks,
{APP_NAME} Team
"""

    # ✅ HTML content (better inbox rate + professional)
    html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
    <div style="max-width: 500px; margin: auto; background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #eee;">
      
      <h2 style="color: #2e7d32;">{APP_NAME}</h2>

      <p>Hi {name},</p>

      <p>We received a request to reset your password.</p>

      <div style="text-align: center; margin: 20px 0;">
        <span style="font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #2e7d32;">
          {otp}
        </span>
      </div>

      <p>This code will expire in <b>5 minutes</b>.</p>

      <p>If you didn’t request this, you can safely ignore this email.</p>

      <hr style="margin: 20px 0;" />

      <p style="font-size: 12px; color: #888;">
        This is an automated message. Please do not reply.
      </p>

      <p style="font-size: 12px; color: #888;">
        © {APP_NAME}
      </p>
    </div>
  </body>
</html>
"""

    url = "https://api.sendgrid.com/v3/mail/send"

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {
            "email": FROM_EMAIL,
            "name": APP_NAME
        },
        "reply_to": {
            "email": FROM_EMAIL
        },
        "content": [
            {"type": "text/plain", "value": text_content},
            {"type": "text/html", "value": html_content}
        ]
    }

    try:
        print(f"📤 Sending OTP to {to_email}")

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        print("📊 Status Code:", response.status_code)

        if response.status_code == 202:
            print("✅ Email sent successfully")
            return True
        else:
            print("❌ SendGrid Error:", response.text)
            return False

    except requests.exceptions.RequestException as e:
        print("❌ Network Error:", str(e))
        return False