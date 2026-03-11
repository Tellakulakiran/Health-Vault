import asyncio
from core.database import AsyncSessionLocal
from api.user_profile import get_profile
from models.user import User

async def test_profile():
    print('Testing Profile Fetch...')
    async with AsyncSessionLocal() as session:
        # Create a mock user
        user = User(id=1, username="test", name="Test", email="test@test.com", phone="123", age=30, gender="Male", blood_group="O+", hashed_password="pw")
        try:
            result = await get_profile(session, user)
            print(result)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test_profile())
