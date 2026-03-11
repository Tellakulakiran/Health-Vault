import os
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Any, List, Optional
from core.config import settings
import uuid
from sqlalchemy.orm import declarative_base

# Required for all data models like models/user.py to inherit from
Base = declarative_base()

# Dummy alias so old code doesn't crash on import
AsyncSessionLocal = lambda: SupabaseSession()

# We lazy-load the client so Vercel's Build container doesn't crash on import if keys are hidden
_supabase_client = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url = settings.SUPABASE_URL or "https://aqjcsrmkxjtihbryxeyk.supabase.co"
        # Provide a dummy string during build time to avoid "supabase_key is required" exception
        key = settings.SUPABASE_KEY or "dummy_build_key" 
        _supabase_client = create_client(url, key)
    return _supabase_client

class MockResult:
    def __init__(self, data):
        self._data = data
        
    def scalars(self):
        return self
        
    def first(self):
        if not self._data:
            return None
        return self._data[0]
        
    def all(self):
        return self._data

class SupabaseSession:
    """A drop-in SQLAlchemy async session replacement that routes queries to Supabase REST API via IPv4"""
    def __init__(self):
        self.pending_adds = []
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def add(self, instance):
        self.pending_adds.append(instance)

    async def commit(self):
        for item in self.pending_adds:
            table_name = item.__tablename__
            
            # Convert SQLAlchemy object to dictionary, excluding internal state
            data = {c.name: getattr(item, c.name) for c in item.__table__.columns if getattr(item, c.name) is not None}
            
            # Post to Supabase REST endpoint
            client = get_supabase_client()
            response = client.table(table_name).insert(data).execute()
            
            # Emulate SQLAlchemy ID assignment
            if response.data and 'id' in response.data[0]:
                setattr(item, 'id', response.data[0]['id'])

        self.pending_adds = []
        
    async def refresh(self, instance):
        pass

    async def execute(self, statement):
        """
        Parses basic SQLAlchemy `select(Model).where(Model.field == value)` statements
        and converts them into Supabase `.select().eq()` REST requests.
        """
        table_name = statement.froms[0].name
        model_class = statement.column_descriptions[0]["type"]
        
        client = get_supabase_client()
        query = client.table(table_name).select("*")
        
        # Extremely simplified WHERE clause parser for our specific Auth/Profile queries
        if statement.whereclause is not None:
            # Check for OR conditions (used in login/register)
            if hasattr(statement.whereclause, 'operator') and statement.whereclause.operator.__name__ == 'or_':
                clauses = statement.whereclause.clauses
                or_string = ",".join([f"{c.left.name}.eq.{c.right.value}" for c in clauses])
                query = query.or_(or_string)
            else:
                # Simple single condition
                left_key = statement.whereclause.left.name
                right_val = statement.whereclause.right.value
                query = query.eq(left_key, right_val)
                
        response = query.execute()
        
        # Re-hydrate dictionary data back into SQLAlchemy Model instances
        hydrated = []
        for row in response.data:
            instance = model_class(**row)
            hydrated.append(instance)
            
        return MockResult(hydrated)

async def get_db():
    async with SupabaseSession() as session:
        yield session
