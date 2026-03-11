import asyncio
from core.database import AsyncSessionLocal
from api.auth import RegisterRequest, register_user

async def test_register():
    print('Testing Registration...')
    request = RegisterRequest(
        name='Test User',
        email='test@example.com',
        phone='1234567890',
        password='password123',
        age=30,
        gender='Male',
        blood_group='O+'
    )
    async with AsyncSessionLocal() as session:
        try:
            result = await register_user(request, session)
            print(result)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test_register())
