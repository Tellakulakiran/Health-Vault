import asyncio
from core.database import SupabaseSession
from models.user import User

async def test_rest():
    print('Testing REST Emulation Insert...')
    async with SupabaseSession() as session:
        # Create user
        demo_user = User(
            username="rest_demo",
            phone="rest_demo",
            hashed_password="pw",
            role="patient"
        )
        session.add(demo_user)
        try:
            await session.commit()
            print("Successfully Inserted User ID:", demo_user.id)
            
            # Test Query Builder
            from sqlalchemy.future import select
            query = select(User).where(User.username == 'rest_demo')
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                print('Found User via REST query!', user.id, user.username)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test_rest())
