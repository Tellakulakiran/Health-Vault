import asyncio
from core.database import engine, Base
import models.user
import models.health

async def reset_database():
    print("Dropping all existing Supabase tables to reset schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("Re-creating all tables with new column definitions...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Database schema synchronization complete!")

if __name__ == "__main__":
    asyncio.run(reset_database())
