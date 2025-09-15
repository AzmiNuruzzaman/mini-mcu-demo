# check_tables.py
from sqlalchemy import create_engine, text
from config.settings import POSTGRES_URL

def check_tables():
    engine = create_engine(POSTGRES_URL)
    
    with engine.connect() as conn:
        # Check if checkups table exists
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'checkups'
            ORDER BY ordinal_position
        """))
        
        print("📋 Columns in 'checkups' table:")
        for row in result:
            print(f"  {row[0]} ({row[1]})")
        
        # Check if users table exists
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        print("\n📋 Columns in 'users' table:")
        for row in result:
            print(f"  {row[0]} ({row[1]})")

if __name__ == "__main__":
    check_tables()