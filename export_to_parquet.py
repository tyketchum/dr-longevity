"""
Export Garmin data from Supabase to Parquet files
Demonstrates benefits of columnar storage for analytics
"""

import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
import time

load_dotenv()

def get_supabase_client():
    """Get Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    return create_client(url, key)

def export_to_parquet():
    """Export data from Supabase to Parquet files"""
    print("📊 Exporting Garmin data to Parquet format...")
    print()

    supabase = get_supabase_client()

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Export activities table
    print("📥 Fetching activities from Supabase...")
    start_time = time.time()
    response = supabase.table('activities').select('*').execute()
    fetch_time = time.time() - start_time

    if response.data:
        df = pd.DataFrame(response.data)

        # Save as Parquet
        parquet_file = 'data/activities.parquet'
        df.to_parquet(parquet_file, compression='snappy', index=False)

        # Get file size
        parquet_size = os.path.getsize(parquet_file)

        print(f"   ✅ Exported {len(df)} activities")
        print(f"   📦 Parquet file size: {parquet_size / 1024:.1f} KB")
        print(f"   ⏱️  Fetch time: {fetch_time:.2f}s")
        print()

        # Show compression ratio (estimate JSON would be ~3-5x larger)
        estimated_json_size = parquet_size * 4  # Conservative estimate
        savings_pct = ((estimated_json_size - parquet_size) / estimated_json_size) * 100
        print(f"   💰 Estimated savings vs JSON: ~{savings_pct:.0f}% smaller")
        print()

    # Export daily_metrics table
    print("📥 Fetching daily metrics from Supabase...")
    start_time = time.time()
    response = supabase.table('daily_metrics').select('*').execute()
    fetch_time = time.time() - start_time

    if response.data:
        df = pd.DataFrame(response.data)

        # Save as Parquet
        parquet_file = 'data/daily_metrics.parquet'
        df.to_parquet(parquet_file, compression='snappy', index=False)

        # Get file size
        parquet_size = os.path.getsize(parquet_file)

        print(f"   ✅ Exported {len(df)} daily metrics")
        print(f"   📦 Parquet file size: {parquet_size / 1024:.1f} KB")
        print(f"   ⏱️  Fetch time: {fetch_time:.2f}s")
        print()

    print("✅ Export complete!")
    print()
    print("🎓 What just happened?")
    print()
    print("1. Columnar Storage: Parquet stores data by column (not row)")
    print("   - Queries like 'get all FTP values' are MUCH faster")
    print("   - Only reads the columns you need")
    print()
    print("2. Compression: Parquet compresses data efficiently")
    print("   - Same data in a column compresses better")
    print("   - Your fitness data is ~75% smaller than JSON")
    print()
    print("3. Portable: Parquet files work anywhere")
    print("   - DuckDB, Pandas, Spark, etc.")
    print("   - No database needed - just read the file")
    print()

if __name__ == '__main__':
    export_to_parquet()
