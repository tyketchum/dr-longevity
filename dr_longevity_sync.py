"""
Dr. Longevity - Data Sync
Fetches health metrics from Garmin Connect and stores in Supabase cloud database
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from garminconnect import Garmin
from garth.exc import GarthHTTPError
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Try to get credentials from Streamlit secrets first (for cloud deployment)
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        GARMIN_EMAIL = st.secrets.get("garmin", {}).get("email") or os.getenv('GARMIN_EMAIL')
        GARMIN_PASSWORD = st.secrets.get("garmin", {}).get("password") or os.getenv('GARMIN_PASSWORD')
        SUPABASE_URL = st.secrets.get("supabase", {}).get("url") or os.getenv('SUPABASE_URL')
        SUPABASE_KEY = st.secrets.get("supabase", {}).get("key") or os.getenv('SUPABASE_KEY')
    else:
        GARMIN_EMAIL = os.getenv('GARMIN_EMAIL')
        GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY')
except:
    GARMIN_EMAIL = os.getenv('GARMIN_EMAIL')
    GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def get_supabase_client() -> Client:
    """Get Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

    return create_client(SUPABASE_URL, SUPABASE_KEY)

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

def sync_daily_data(garmin, supabase: Client, days=30):
    """Sync daily summary data from Garmin to Supabase"""
    print(f"📥 Syncing last {days} days of data...")

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

            # Prepare data for Supabase
            data = {
                'date': date_str,
                'steps': steps,
                'distance_meters': distance,
                'calories': calories,
                'active_minutes': active_mins,
                'resting_heart_rate': rhr,
                'max_heart_rate': max_hr,
                'avg_stress': avg_stress,
                'body_battery_charged': body_battery,
                'sleep_score': sleep_score,
                'deep_sleep_seconds': deep_sleep,
                'light_sleep_seconds': light_sleep,
                'rem_sleep_seconds': rem_sleep,
                'awake_seconds': awake,
                'last_synced': datetime.now().isoformat()
            }

            # Upsert to Supabase (insert or update if exists)
            response = supabase.table('daily_summaries').upsert(data).execute()

            synced_count += 1
            print(f"   ✅ {date_str}: {steps:,} steps, {sleep_score if sleep_score else 'N/A'} sleep score")

        except Exception as e:
            print(f"   ⚠️  {date_str}: {str(e)}")
            continue

    print(f"\n✅ Sync complete! {synced_count}/{days} days synced")

def sync_activities(garmin, supabase: Client, days=30):
    """Sync activities from Garmin to Supabase"""
    print(f"📥 Syncing activities from last {days} days...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    synced_count = 0

    try:
        # Get activities from Garmin
        activities = garmin.get_activities_by_date(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        for activity in activities:
            try:
                # Extract activity data
                activity_id = str(activity.get('activityId'))
                date_str = activity.get('startTimeLocal', '').split(' ')[0]
                start_time = activity.get('startTimeLocal')
                activity_type = activity.get('activityType', {}).get('typeKey', 'Unknown')
                duration_minutes = activity.get('duration', 0) / 60
                distance_km = activity.get('distance', 0) / 1000 if activity.get('distance') else None

                # Heart rate data
                avg_hr = activity.get('averageHR')
                max_hr = activity.get('maxHR')

                # Power data
                avg_power = activity.get('avgPower')
                max_power = activity.get('maxPower')

                # Cadence data
                avg_cadence = activity.get('avgRunCadence') or activity.get('avgBikeCadence')
                max_cadence = activity.get('maxRunCadence') or activity.get('maxBikeCadence')

                # Other metrics
                calories = activity.get('calories')
                elevation_gain = activity.get('elevationGain')
                elevation_loss = activity.get('elevationLoss')
                workout_name = activity.get('activityName')

                # Prepare data for Supabase
                data = {
                    'activity_id': activity_id,
                    'date': date_str,
                    'start_time': start_time,
                    'source': 'garmin',
                    'activity_type': activity_type,
                    'duration_minutes': duration_minutes,
                    'distance_km': distance_km,
                    'avg_hr': avg_hr,
                    'max_hr': max_hr,
                    'avg_power': avg_power,
                    'max_power': max_power,
                    'avg_cadence': avg_cadence,
                    'max_cadence': max_cadence,
                    'calories': calories,
                    'elevation_gain': elevation_gain,
                    'elevation_loss': elevation_loss,
                    'workout_name': workout_name
                }

                # Remove None values
                data = {k: v for k, v in data.items() if v is not None}

                # Upsert to Supabase
                response = supabase.table('activities').upsert(data, on_conflict='activity_id').execute()

                synced_count += 1
                print(f"   ✅ {date_str}: {activity_type} - {duration_minutes:.0f} min")

            except Exception as e:
                print(f"   ⚠️  Error syncing activity {activity_id}: {str(e)}")
                continue

        print(f"\n✅ Activities sync complete! {synced_count} activities synced")

    except Exception as e:
        print(f"❌ Error fetching activities: {str(e)}")

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

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials!")
        print("Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        sys.exit(1)

    # Get Supabase client
    supabase = get_supabase_client()
    print("✅ Connected to Supabase")

    # Connect to Garmin
    garmin = connect_to_garmin()

    # Sync data (default to last 30 days)
    days = int(os.getenv('SYNC_DAYS', 30))

    # Sync daily summaries
    sync_daily_data(garmin, supabase, days)

    # Sync activities
    sync_activities(garmin, supabase, days)

    print("=" * 50)
    print("✅ All done!")
    print("=" * 50)

if __name__ == '__main__':
    main()
