import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "HealthVault AI"
    # Use /tmp for SQLite on Vercel to avoid Read-Only file system errors
    _default_db = "sqlite+aiosqlite:////tmp/healthvault.db" if os.environ.get("VERCEL") else "sqlite+aiosqlite:///./healthvault.db"
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", _default_db)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://aqjcsrmkxjtihbryxeyk.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "") # Need to acquire from the Dashboard
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ec9b48b7fca1f8b3c9b741872b8ceef00d23a10e6a88e2c07921503dbdedd30f") # Demo key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Gmail SMTP for OTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")  # Your Gmail address
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")  # Gmail App Password

settings = Settings()
