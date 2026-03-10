"""
OTP API — Generate, send via Gmail SMTP, and verify OTPs.
OTPs are stored in-memory with a 5-minute expiry.
"""
import random
import time
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.config import settings

router = APIRouter()

# In-memory OTP store: { email: { code, expires_at } }
_otp_store: dict = {}
_lock = threading.Lock()

OTP_EXPIRY_SECONDS = 300  # 5 minutes


class OtpSendRequest(BaseModel):
    email: str


class OtpVerifyRequest(BaseModel):
    email: str
    code: str


def _generate_otp() -> str:
    return str(random.randint(100000, 999999))


def _send_email(to_email: str, otp_code: str):
    """Send OTP email via Gmail SMTP."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[OTP] SMTP not configured. OTP for {to_email}: {otp_code}")
        return  # Graceful fallback: print to console

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔐 HealthVault Verification Code: {otp_code}"
    msg["From"] = f"HealthVault <{settings.SMTP_USER}>"
    msg["To"] = to_email

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 0;">
      <div style="background: linear-gradient(135deg, #0a121e, #0e1929); border-radius: 20px; padding: 40px; color: #fff; text-align: center;">
        <div style="font-size: 28px; font-weight: 800; color: #00f2fe; margin-bottom: 8px;">✦ HealthVault</div>
        <div style="color: #94a3b8; font-size: 14px; margin-bottom: 28px;">Your secure personal health companion</div>
        <div style="font-size: 14px; color: #94a3b8; margin-bottom: 12px;">Your verification code is:</div>
        <div style="font-size: 42px; font-weight: 800; letter-spacing: 12px; color: #00f2fe; background: rgba(0,242,254,0.08); border-radius: 16px; padding: 16px 0; margin-bottom: 20px;">
          {otp_code}
        </div>
        <div style="font-size: 13px; color: #64748b; line-height: 1.6;">
          This code expires in <strong style="color:#00f2fe;">5 minutes</strong>.<br/>
          If you didn't request this, please ignore this email.
        </div>
      </div>
      <div style="text-align: center; color: #475569; font-size: 11px; margin-top: 16px;">
        &copy; 2026 HealthVault AI &bull; Secure Health Platform
      </div>
    </div>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        print(f"[OTP] Email sent to {to_email}")
    except Exception as e:
        print(f"[OTP] Email send failed: {e}")
        # Don't raise — we still stored the OTP, user can see it in console fallback
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/send")
async def send_otp(req: OtpSendRequest):
    """Generate OTP, store it, and email it."""
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    code = _generate_otp()
    with _lock:
        _otp_store[email] = {"code": code, "expires_at": time.time() + OTP_EXPIRY_SECONDS}

    # Send email (runs synchronously but is fast enough for SMTP)
    _send_email(email, code)

    return {"success": True, "message": "OTP sent to your email"}


@router.post("/verify")
async def verify_otp(req: OtpVerifyRequest):
    """Verify the OTP code."""
    email = req.email.strip().lower()
    code = req.code.strip()

    with _lock:
        entry = _otp_store.get(email)

    if not entry:
        raise HTTPException(status_code=400, detail="No OTP found. Please request a new one.")

    if time.time() > entry["expires_at"]:
        with _lock:
            _otp_store.pop(email, None)
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    if entry["code"] != code:
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")

    # OTP is valid — remove it
    with _lock:
        _otp_store.pop(email, None)

    return {"success": True, "message": "OTP verified"}
