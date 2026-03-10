from fastapi import APIRouter, Depends
from models.user import User
from api.deps import get_current_active_user
import asyncio
import random

router = APIRouter()

@router.post("/trigger")
async def trigger_emergency(
    current_user: User = Depends(get_current_active_user)
):
    # Simulate a delay and return mock live location coordinates
    # In a real app this would trigger SMS/emails to emergency contacts
    await asyncio.sleep(1)
    
    lat = 37.7749 + random.uniform(-0.01, 0.01)
    lng = -122.4194 + random.uniform(-0.01, 0.01)
    
    return {
        "status": "success",
        "message": f"Emergency Alert Triggered for user {current_user.username}",
        "data": {
            "tracking_active": True,
            "simulated_location": {
                "latitude": round(lat, 6),
                "longitude": round(lng, 6)
            },
            "contacts_notified": ["Emergency Contact 1 (555-0100)"]
        }
    }
