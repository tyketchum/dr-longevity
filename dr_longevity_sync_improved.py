"""
Dr. Longevity - Enhanced Data Sync
Fetches comprehensive health metrics from Garmin Connect including VO2 max, weight, HRV, training load
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

def sync_daily_metrics(garmin, supabase: Client, days=30):
    """Sync comprehensive daily metrics from Garmin to Supabase"""
    print(f"📥 Syncing last {days} days of daily metrics...")

    end_date = datetime.now()
    synced_count = 0

    for i in range(days):
        date = end_date - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        try:
            # Get comprehensive daily data
            summary = garmin.get_stats(date_str)
            sleep_data = garmin.get_sleep_data(date_str)
            heart_rate_data = garmin.get_heart_rates(date_str)

            # Try to get additional metrics (may not be available for all devices)
            try:
                stress_data = garmin.get_stress_data(date_str)
            except:
                stress_data = None

            try:
                body_battery_data = garmin.get_body_battery(date_str)
            except:
                body_battery_data = None

            try:
                # Weight is in grams, convert to lbs
                weight_data = garmin.get_body_composition(date_str)
                weight_lbs = None
                if weight_data and 'weight' in weight_data:
                    weight_kg = weight_data['weight'] / 1000
                    weight_lbs = weight_kg * 2.20462
            except:
                weight_lbs = None

            # Extract metrics (convert heart rate to integers)
            resting_hr = int(heart_rate_data.get('restingHeartRate')) if heart_rate_data and heart_rate_data.get('restingHeartRate') else None
            max_hr = int(summary.get('maxHeartRate')) if summary and summary.get('maxHeartRate') else None

            # HRV (Heart Rate Variability) - check multiple locations
            hrv = None
            if heart_rate_data:
                hrv = heart_rate_data.get('heartRateVariability') or heart_rate_data.get('hrv')
            if not hrv and summary:
                hrv = summary.get('averageHRV')
            # Convert HRV to integer if present
            hrv = int(hrv) if hrv else None

            # Stress and body battery (convert to integers)
            avg_stress = int(stress_data.get('avgStressLevel')) if stress_data and stress_data.get('avgStressLevel') else None
            body_battery = int(body_battery_data[-1].get('charged')) if body_battery_data and len(body_battery_data) > 0 and body_battery_data[-1].get('charged') else None

            # Activity metrics (ensure integers, handle None)
            steps = int(summary.get('totalSteps') or 0) if summary else 0
            floors_climbed = int(summary.get('floorsAscended') or 0) if summary else 0
            intensity_minutes = int(summary.get('intensityMinutesGoal') or 0) if summary else 0

            # Training load (Garmin's proprietary metric - convert to integer)
            training_load = int(summary.get('trainingLoad')) if summary and summary.get('trainingLoad') else None

            # Respiration and SpO2 (if available - convert to integers)
            respiration_rate = int(summary.get('avgRespirationRate')) if summary and summary.get('avgRespirationRate') else None
            spo2 = int(summary.get('avgSpO2')) if summary and summary.get('avgSpO2') else None

            # Extract sleep metrics
            sleep_score = None
            sleep_hours = None
            deep_sleep = None
            light_sleep = None
            rem_sleep = None
            awake = None

            if sleep_data:
                sleep_summary = sleep_data.get('dailySleepDTO', {})
                sleep_score_raw = sleep_summary.get('sleepScores', {}).get('overall', {}).get('value')
                sleep_score = int(sleep_score_raw) if sleep_score_raw else None
                sleep_time_sec = sleep_summary.get('sleepTimeSeconds')
                if sleep_time_sec:
                    sleep_hours = sleep_time_sec / 3600

                deep_sleep_sec = sleep_summary.get('deepSleepSeconds')
                if deep_sleep_sec:
                    deep_sleep = deep_sleep_sec / 3600

                light_sleep_sec = sleep_summary.get('lightSleepSeconds')
                if light_sleep_sec:
                    light_sleep = light_sleep_sec / 3600

                rem_sleep_sec = sleep_summary.get('remSleepSeconds')
                if rem_sleep_sec:
                    rem_sleep = rem_sleep_sec / 3600

                awake_sec = sleep_summary.get('awakeSleepSeconds')
                if awake_sec:
                    awake = awake_sec / 3600

            # Prepare data for Supabase
            data = {
                'date': date_str,
                'resting_hr': resting_hr,
                'hrv': hrv,
                'stress_score': avg_stress,
                'body_battery': body_battery,
                'weight': weight_lbs,
                'sleep_hours': sleep_hours,
                'sleep_score': sleep_score,
                'sleep_deep_hours': deep_sleep,
                'sleep_light_hours': light_sleep,
                'sleep_rem_hours': rem_sleep,
                'sleep_awake_hours': awake,
                'steps': steps,
                'floors_climbed': floors_climbed,
                'intensity_minutes': intensity_minutes,
                'training_load': training_load,
                'respiration_rate': respiration_rate,
                'spo2': spo2
            }

            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            # Upsert to Supabase
            response = supabase.table('daily_metrics').upsert(data, on_conflict='date').execute()

            synced_count += 1
            metrics_str = f"Steps: {steps:,}, Sleep: {sleep_score if sleep_score else 'N/A'}"
            if weight_lbs:
                metrics_str += f", Weight: {weight_lbs:.1f} lbs"
            if hrv:
                metrics_str += f", HRV: {hrv:.1f}"
            if training_load:
                metrics_str += f", Load: {training_load}"
            print(f"   ✅ {date_str}: {metrics_str}")

        except Exception as e:
            print(f"   ⚠️  {date_str}: {str(e)}")
            continue

    print(f"\n✅ Daily metrics sync complete! {synced_count}/{days} days synced")

def sync_activities(garmin, supabase: Client, days=30):
    """Sync activities from Garmin to Supabase with comprehensive metrics"""
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
            activity_id = activity.get('activityId')

            # Get detailed activity data (like backend does)
            try:
                details = garmin.get_activity(activity_id)
            except Exception as e:
                print(f"   ⚠️  Could not fetch details for activity {activity_id}, using summary: {e}")
                details = activity
            try:
                # Extract activity data
                activity_id = str(activity.get('activityId'))
                date_str = activity.get('startTimeLocal', '').split(' ')[0]
                start_time = activity.get('startTimeLocal')
                activity_type = activity.get('activityType', {}).get('typeKey', 'Unknown')
                duration_minutes = activity.get('duration', 0) / 60
                distance_km = activity.get('distance', 0) / 1000 if activity.get('distance') else None

                # Heart rate data (convert to integers)
                avg_hr = int(activity.get('averageHR')) if activity.get('averageHR') else None
                max_hr = int(activity.get('maxHR')) if activity.get('maxHR') else None

                # HR Zone data - use dedicated API endpoint for better accuracy
                hr_zone_1_minutes = None
                hr_zone_2_minutes = None
                hr_zone_3_minutes = None
                hr_zone_4_minutes = None
                hr_zone_5_minutes = None

                try:
                    hr_zones = garmin.get_activity_hr_in_timezones(activity_id)
                    if hr_zones:
                        for zone in hr_zones:
                            zone_num = zone.get('zoneNumber')
                            secs_in_zone = zone.get('secsInZone', 0)
                            if zone_num == 1:
                                hr_zone_1_minutes = secs_in_zone / 60
                            elif zone_num == 2:
                                hr_zone_2_minutes = secs_in_zone / 60
                            elif zone_num == 3:
                                hr_zone_3_minutes = secs_in_zone / 60
                            elif zone_num == 4:
                                hr_zone_4_minutes = secs_in_zone / 60
                            elif zone_num == 5:
                                hr_zone_5_minutes = secs_in_zone / 60
                except:
                    # Fall back to activity summary if API call fails
                    hr_zone_1_minutes = activity.get('timeInHRZone1', 0) / 60 if activity.get('timeInHRZone1') else None
                    hr_zone_2_minutes = activity.get('timeInHRZone2', 0) / 60 if activity.get('timeInHRZone2') else None
                    hr_zone_3_minutes = activity.get('timeInHRZone3', 0) / 60 if activity.get('timeInHRZone3') else None
                    hr_zone_4_minutes = activity.get('timeInHRZone4', 0) / 60 if activity.get('timeInHRZone4') else None
                    hr_zone_5_minutes = activity.get('timeInHRZone5', 0) / 60 if activity.get('timeInHRZone5') else None

                # Power data - check details first, fall back to summary (convert to integers)
                avg_power = int(details.get('avgPower') or activity.get('avgPower') or 0) if (details.get('avgPower') or activity.get('avgPower')) else None
                max_power = int(details.get('maxPower') or activity.get('maxPower') or 0) if (details.get('maxPower') or activity.get('maxPower')) else None
                normalized_power = int(details.get('normalizedPower') or activity.get('normalizedPower') or 0) if (details.get('normalizedPower') or activity.get('normalizedPower')) else None

                # Cadence data - check details first, fall back to summary (convert to integers)
                avg_cadence = int(details.get('avgBikeCadence') or details.get('avgRunCadence') or activity.get('avgBikeCadence') or activity.get('avgRunCadence') or 0) if (details.get('avgBikeCadence') or details.get('avgRunCadence') or activity.get('avgBikeCadence') or activity.get('avgRunCadence')) else None
                max_cadence = int(details.get('maxBikeCadence') or details.get('maxRunCadence') or activity.get('maxBikeCadence') or activity.get('maxRunCadence') or 0) if (details.get('maxBikeCadence') or details.get('maxRunCadence') or activity.get('maxBikeCadence') or activity.get('maxRunCadence')) else None

                # Pace data (for running)
                avg_pace = activity.get('avgPace')
                max_pace = activity.get('maxPace')

                # Other metrics (convert to integers)
                calories = int(activity.get('calories')) if activity.get('calories') else None
                elevation_gain = int(activity.get('elevationGain')) if activity.get('elevationGain') else None
                elevation_loss = int(activity.get('elevationLoss')) if activity.get('elevationLoss') else None

                # Training effects (convert to integers)
                aerobic_training_effect = int(activity.get('aerobicTrainingEffect')) if activity.get('aerobicTrainingEffect') else None
                anaerobic_training_effect = int(activity.get('anaerobicTrainingEffect')) if activity.get('anaerobicTrainingEffect') else None

                # VO2 MAX ESTIMATE - This is critical!
                vo2max_estimate = activity.get('vO2MaxValue')

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
                    'hr_zone_1_minutes': hr_zone_1_minutes,
                    'hr_zone_2_minutes': hr_zone_2_minutes,
                    'hr_zone_3_minutes': hr_zone_3_minutes,
                    'hr_zone_4_minutes': hr_zone_4_minutes,
                    'hr_zone_5_minutes': hr_zone_5_minutes,
                    'avg_power': avg_power,
                    'max_power': max_power,
                    'normalized_power': normalized_power,
                    'avg_cadence': avg_cadence,
                    'max_cadence': max_cadence,
                    'avg_pace': avg_pace,
                    'max_pace': max_pace,
                    'calories': calories,
                    'elevation_gain': elevation_gain,
                    'elevation_loss': elevation_loss,
                    'aerobic_training_effect': aerobic_training_effect,
                    'anaerobic_training_effect': anaerobic_training_effect,
                    'vo2max_estimate': vo2max_estimate,
                    'workout_name': workout_name
                }

                # Remove None values
                data = {k: v for k, v in data.items() if v is not None}

                # Upsert to Supabase
                response = supabase.table('activities').upsert(data, on_conflict='activity_id').execute()

                synced_count += 1
                metrics_str = f"{activity_type} - {duration_minutes:.0f} min"
                if avg_power:
                    metrics_str += f", Power: {avg_power}W"
                if vo2max_estimate:
                    metrics_str += f", VO2: {vo2max_estimate:.1f}"
                print(f"   ✅ {date_str}: {metrics_str}")

            except Exception as e:
                print(f"   ⚠️  Error syncing activity {activity_id}: {str(e)}")
                continue

        print(f"\n✅ Activities sync complete! {synced_count} activities synced")

    except Exception as e:
        print(f"❌ Error fetching activities: {str(e)}")

def main():
    """Main sync process"""
    print("=" * 50)
    print("🏃 Garmin Enhanced Data Sync Starting...")
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

    # Sync data (default to all history - 20 years should cover any Garmin account)
    days = int(os.getenv('SYNC_DAYS', 7300))  # 20 years default = ALL HISTORY

    print(f"\n📅 Syncing {days} days of data ({days/365:.1f} years) - FULL GARMIN HISTORY")

    # Sync daily metrics (with weight, HRV, training load)
    sync_daily_metrics(garmin, supabase, days)

    # Sync activities (with VO2 max, HR zones, normalized power)
    sync_activities(garmin, supabase, days)

    print("=" * 50)
    print("✅ Enhanced sync complete!")
    print("=" * 50)
    print("\nNew data captured:")
    print("  ✅ Weight (daily)")
    print("  ✅ HRV (daily)")
    print("  ✅ Training Load (daily)")
    print("  ✅ VO2 Max estimates (per activity)")
    print("  ✅ HR Zone times (per activity)")
    print("  ✅ Normalized Power (cycling)")
    print("  ✅ Training Effects (per activity)")

if __name__ == '__main__':
    main()
