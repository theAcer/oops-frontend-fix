"""
Script to fix the businesstype enum in the database
Run this if you want to keep existing data instead of cleaning volumes
"""

from sqlalchemy import text
from app.core.database import engine
import asyncio

async def fix_enum():
    async with engine.begin() as conn:
        # First, check current enum values
        result = await conn.execute(text("""
            SELECT enumlabel FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'businesstype')
        """))
        current_values = [row[0] for row in result]
        print(f"Current enum values: {current_values}")
        
        # Add missing enum values if they don't exist
        required_values = ['restaurant', 'salon', 'retail', 'service', 'other']
        for value in required_values:
            if value not in current_values:
                print(f"Adding enum value: {value}")
                await conn.execute(text(f"ALTER TYPE businesstype ADD VALUE '{value}'"))
        
        print("Enum fix completed!")

if __name__ == "__main__":
    asyncio.run(fix_enum())
