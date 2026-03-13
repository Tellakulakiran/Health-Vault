import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from core.database import Base
import models.user
import models.health

engine = create_async_engine('postgresql+asyncpg://postgres:your_db_password_here@aws-0-ap-south-1.pooler.supabase.com:6543/postgres', echo=False, future=True)

async def reset_cloud_database():
    print('Connecting to Vercel Supabase Instance...')
    async with engine.begin() as conn:
        print('Dropping old schema tables...')
        await conn.run_sync(Base.metadata.drop_all)
    
    async with engine.begin() as conn:
        print('Creating newly expanded SQLAlchemy models in Supabase...')
        await conn.run_sync(Base.metadata.create_all)
        
    print('Vercel Cloud Database successfully synchronized!')

asyncio.run(reset_cloud_database())
