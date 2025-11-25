"""
Migration Script: SQLite to Supabase
Copies existing data from local SQLite database to Supabase cloud database
"""

import os
import sqlite3
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
DB_PATH = Path(__file__).parent / 'longevity_dashboard.db'

def get_supabase_client() -> Client:
    """Get Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def migrate_table(sqlite_conn, supabase: Client, table_name: str):
    """Migrate a single table from SQLite to Supabase"""
    try:
        # Read data from SQLite
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)

        if df.empty:
            print(f"   ⚠️  {table_name}: No data to migrate")
            return 0

        # Convert DataFrame to list of dicts
        records = df.to_dict('records')

        # Clean up records (remove None values, convert timestamps)
        cleaned_records = []
        for record in records:
            cleaned = {k: v for k, v in record.items() if pd.notna(v)}
            cleaned_records.append(cleaned)

        # Batch insert to Supabase (in chunks of 100)
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(cleaned_records), batch_size):
            batch = cleaned_records[i:i + batch_size]
            try:
                response = supabase.table(table_name).upsert(batch).execute()
                total_inserted += len(batch)
                print(f"   ✅ {table_name}: Inserted batch {i // batch_size + 1} ({len(batch)} records)")
            except Exception as e:
                print(f"   ⚠️  {table_name}: Error inserting batch {i // batch_size + 1}: {str(e)}")
                continue

        print(f"   ✅ {table_name}: Successfully migrated {total_inserted}/{len(records)} records")
        return total_inserted

    except Exception as e:
        print(f"   ❌ {table_name}: Error - {str(e)}")
        return 0

def main():
    """Main migration process"""
    print("=" * 60)
    print("🔄 SQLite to Supabase Migration")
    print("=" * 60)

    # Check if SQLite database exists
    if not DB_PATH.exists():
        print(f"❌ SQLite database not found at: {DB_PATH}")
        print("Nothing to migrate!")
        return

    # Validate Supabase credentials
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials!")
        print("Please set SUPABASE_URL and SUPABASE_KEY in .env file")
        return

    # Connect to databases
    print("\n📥 Connecting to databases...")
    sqlite_conn = sqlite3.connect(DB_PATH)
    supabase = get_supabase_client()
    print("✅ Connected successfully")

    # Get list of tables to migrate
    tables_to_migrate = [
        'activities',
        'daily_metrics',
        'daily_summaries',
        'weekly_summary',
        'monthly_labs',
        'food_log',
        'water_log'
    ]

    print(f"\n📤 Migrating {len(tables_to_migrate)} tables...")
    print("-" * 60)

    total_records = 0
    for table in tables_to_migrate:
        print(f"\n📋 Migrating: {table}")
        records = migrate_table(sqlite_conn, supabase, table)
        total_records += records

    # Close connections
    sqlite_conn.close()

    print("\n" + "=" * 60)
    print(f"✅ Migration complete! {total_records} total records migrated")
    print("=" * 60)

    print("\n📝 Next steps:")
    print("1. Go to your Supabase project")
    print("2. Click 'Table Editor' to verify data was migrated")
    print("3. Update your dashboard to use the Supabase version")
    print("4. Test that everything works")
    print("5. You can delete the local SQLite database")

if __name__ == '__main__':
    main()
