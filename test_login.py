import asyncio
from core.database import AsyncSessionLocal
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Response
from api.auth import login_for_access_token

class MockResponse(Response):
    def set_cookie(self, *args, **kwargs):
        pass

async def test_login():
    print('Testing Login...')
    # Mocking a form request
    form = OAuth2PasswordRequestForm(username='test@example.com', password='password123', scope="", client_id=None, client_secret=None, grant_type="password")
    
    async with AsyncSessionLocal() as session:
        try:
            result = await login_for_access_token(MockResponse(), form, session)
            print(result)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test_login())
