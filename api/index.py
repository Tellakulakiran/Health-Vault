from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.future import select
import uvicorn
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db
# AsyncSessionLocal is now a dummy lambda in database.py but we should avoid importing it if not needed
from core.security import get_password_hash
from models.user import User
import models.health

from api import auth, records, medications, emergency, otp, user_profile

app = FastAPI(title="HealthVault AI")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create templates and static dirs if needed (skip on Vercel's read-only file system)
if not os.environ.get("VERCEL"):
    os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "static/css"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "static/js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(records.router, prefix="/api/records", tags=["records"])
app.include_router(medications.router, prefix="/api/medications", tags=["medications"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["emergency"])
app.include_router(otp.router, prefix="/api/otp", tags=["otp"])
app.include_router(user_profile.router, prefix="/api/profile", tags=["profile"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    from fastapi import HTTPException
    
    status_code = 500
    detail = "Internal Server Error"
    message = str(exc)
    
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
        
    # Log the full error to the server console
    print(f"ERROR: {detail} - {message}")
    if status_code == 500:
        print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "message": message,
            "trace": traceback.format_exc() if (status_code == 500 and not os.environ.get("VERCEL")) else None
        },
    )


# Startup Event Disabled for Serverless Deployment
# @app.on_event("startup")
# async def startup_event():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     
#     async with AsyncSessionLocal() as session:
#         # Check if demo user exists
#         result = await session.execute(select(User).where(User.username == "patient_demo"))
#         user = result.scalars().first()
#         if not user:
#             demo_user = User(
#                 username="patient_demo",
#                 hashed_password=get_password_hash("password123"),
#                 role="patient"
#             )
#             session.add(demo_user)
#             await session.commit()
@app.get("/api/health_db")
async def health_db():
    from core.database import get_supabase_client
    try:
        client = get_supabase_client()
        # Simple ping to a table
        response = client.table("users").select("count", count="exact").limit(1).execute()
        return {"status": "ok", "message": "Supabase Connection Successful", "data": response.data}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return FileResponse(os.path.join(BASE_DIR, "templates/app.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
