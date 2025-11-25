"""
Garmin Connect Data Sync
Fetches health metrics from Garmin and stores in SQLite database
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from garminconnect import Garmin
from garth.exc import GarthHTTPError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to get credentials from Streamlit secrets first (for cloud deployment)
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        GARMIN_EMAIL = st.secrets.get("garmin", {}).get("email") or os.getenv('GARMIN_EMAIL')
        GARMIN_PASSWORD = st.secrets.get("garmin", {}).get("password") or os.getenv('GARMIN_PASSWORD')
    else:
        GARMIN_EMAIL = os.getenv('GARMIN_EMAIL')
        GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')
except:
    GARMIN_EMAIL = os.getenv('GARMIN_EMAIL')
    GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')

DB_PATH = os.getenv('DB_PATH', str(Path(__file__).parent / 'longevity_dashboard.db'))

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_summaries (
        date TEXT PRIMARY KEY,
        steps INTEGER,
        distance_meters REAL,
        calories INTEGER,
        active_minutes INTEGER,
        resting_heart_rate INTEGER,
        max_heart_rate INTEGER,
        avg_stress INTEGER,
        body_battery_charged INTEGER,
        sleep_score INTEGER,
        deep_sleep_seconds INTEGER,
        light_sleep_seconds INTEGER,
        rem_sleep_seconds INTEGER,
        awake_seconds INTEGER,
        last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def connect_to_garmin():
    """Connect to Garmin Connect"""
    print("🔐 Connecting to Garmin Connect...")

    try:
        garmin = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        garmin.login()
        print("✅ Connected to Garmin Connect")
        return garmin
    except GarthHTTPError as e:
        print(f"❌ Failed to connect to Garmin: {e}")
        sys.exit(1)

def sync_daily_data(garmin, days=30):
    """Sync daily summary data from Garmin"""
    print(f"📥 Syncing last {days} days of data...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    end_date = datetime.now()
    synced_count = 0

    for i in range(days):
        date = end_date - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        try:
            # Get daily summary
            summary = garmin.get_stats(date_str)

            # Get sleep data
            sleep_data = garmin.get_sleep_data(date_str)

            # Extract metrics
            steps = summary.get('totalSteps', 0)
            distance = summary.get('totalDistanceMeters', 0)
            calories = summary.get('activeKilocalories', 0)
            active_mins = summary.get('highlyActiveSeconds', 0) // 60
            rhr = summary.get('restingHeartRate')
            max_hr = summary.get('maxHeartRate')
            avg_stress = summary.get('averageStressLevel')
            body_battery = summary.get('bodyBatteryChargedValue')

            # Extract sleep metrics
            sleep_score = sleep_data.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value')
            deep_sleep = sleep_data.get('dailySleepDTO', {}).get('deepSleepSeconds', 0)
            light_sleep = sleep_data.get('dailySleepDTO', {}).get('lightSleepSeconds', 0)
            rem_sleep = sleep_data.get('dailySleepDTO', {}).get('remSleepSeconds', 0)
            awake = sleep_data.get('dailySleepDTO', {}).get('awakeSeconds', 0)

            # Insert or update
            cursor.execute("""
            INSERT OR REPLACE INTO daily_summaries
            (date, steps, distance_meters, calories, active_minutes,
             resting_heart_rate, max_heart_rate, avg_stress, body_battery_charged,
             sleep_score, deep_sleep_seconds, light_sleep_seconds,
             rem_sleep_seconds, awake_seconds, last_synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                date_str, steps, distance, calories, active_mins,
                rhr, max_hr, avg_stress, body_battery,
                sleep_score, deep_sleep, light_sleep, rem_sleep, awake
            ))

            synced_count += 1
            print(f"   ✅ {date_str}: {steps:,} steps, {sleep_score} sleep score")

        except Exception as e:
            print(f"   ⚠️  {date_str}: {str(e)}")
            continue

    conn.commit()
    conn.close()

    print(f"\n✅ Sync complete! {synced_count}/{days} days synced")

def main():
    """Main sync process"""
    print("=" * 50)
    print("🏃 Garmin Data Sync Starting...")
    print("=" * 50)

    # Validate credentials
    if not GARMIN_EMAIL or not GARMIN_PASSWORD:
        print("❌ Missing Garmin credentials!")
        print("Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")
        sys.exit(1)

    # Initialize database
    init_database()

    # Connect to Garmin
    garmin = connect_to_garmin()

    # Sync data (default to last 30 days)
    days = int(os.getenv('SYNC_DAYS', 30))
    sync_daily_data(garmin, days)

    print("=" * 50)
    print("✅ All done!")
    print("=" * 50)

if __name__ == '__main__':
    main()
