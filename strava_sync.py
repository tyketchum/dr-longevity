"""
Strava Integration for Dr. Longevity
Fetches activity data directly from Strava API to fill gaps in Garmin sync
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import requests
import time

load_dotenv()

# Try to get credentials from Streamlit secrets first (for cloud deployment)
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        STRAVA_CLIENT_ID = st.secrets.get("strava", {}).get("client_id") or os.getenv('STRAVA_CLIENT_ID')
        STRAVA_CLIENT_SECRET = st.secrets.get("strava", {}).get("client_secret") or os.getenv('STRAVA_CLIENT_SECRET')
        STRAVA_REFRESH_TOKEN = st.secrets.get("strava", {}).get("refresh_token") or os.getenv('STRAVA_REFRESH_TOKEN')
        SUPABASE_URL = st.secrets.get("supabase", {}).get("url") or os.getenv('SUPABASE_URL')
        SUPABASE_KEY = st.secrets.get("supabase", {}).get("key") or os.getenv('SUPABASE_KEY')
    else:
        STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
        STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
        STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY')
except:
    STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
    STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
    STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Supabase configuration
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_strava_access_token():
    """Get a fresh access token using refresh token"""
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': STRAVA_REFRESH_TOKEN
        }
    )

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get Strava access token: {response.text}")


def fetch_strava_activities(days=7):
    """Fetch activities from Strava API"""
    access_token = get_strava_access_token()

    # Calculate date range
    after_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())

    # Fetch activities
    url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'after': after_timestamp,
        'per_page': 100
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch Strava activities: {response.text}")


def get_strava_activity_details(activity_id, access_token):
    """Get detailed activity data including power streams"""

    # Get activity details
    url = f'https://www.strava.com/api/v3/activities/{activity_id}'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"  ⚠️  Failed to get activity details: {response.text}")
        return None

    activity = response.json()

    # Get power stream if available
    streams_url = f'https://www.strava.com/api/v3/activities/{activity_id}/streams'
    streams_params = {
        'keys': 'watts,heartrate,cadence,time',
        'key_by_type': 'true'
    }

    streams_response = requests.get(streams_url, headers=headers, params=streams_params)

    if streams_response.status_code == 200:
        streams = streams_response.json()
        activity['streams'] = streams

    return activity


def parse_strava_activity(activity, streams=None):
    """Parse Strava activity into our database format"""

    # Basic activity info
    date = datetime.strptime(activity['start_date_local'], '%Y-%m-%dT%H:%M:%SZ')

    activity_data = {
        'date': date.isoformat(),
        'workout_name': activity['name'],
        'activity_type': activity['type'].lower(),
        'duration_minutes': int(activity['moving_time'] / 60) if activity.get('moving_time') else 0,
        'distance_km': round(activity['distance'] / 1000, 2) if activity.get('distance') else None,
        'elevation_gain': int(activity['total_elevation_gain']) if activity.get('total_elevation_gain') else None,
        'calories': int(activity['kilojoules']) if activity.get('kilojoules') else None,
        'source': 'strava',
    }

    # Power data
    if activity.get('average_watts'):
        activity_data['avg_power'] = int(activity['average_watts'])

    if activity.get('weighted_average_watts'):
        activity_data['normalized_power'] = int(activity['weighted_average_watts'])

    if activity.get('max_watts'):
        activity_data['max_power'] = int(activity['max_watts'])

    # Heart rate data
    if activity.get('average_heartrate'):
        activity_data['avg_hr'] = int(activity['average_heartrate'])

    if activity.get('max_heartrate'):
        activity_data['max_hr'] = int(activity['max_heartrate'])

    # Cadence data
    if activity.get('average_cadence'):
        activity_data['avg_cadence'] = int(activity['average_cadence'])

    if activity.get('max_cadence'):
        activity_data['max_cadence'] = int(activity['max_cadence'])

    # Training load (if available)
    if activity.get('suffer_score'):
        activity_data['training_load'] = int(activity['suffer_score'])

    return activity_data


def sync_from_strava(days=7, activity_id=None):
    """
    Sync activities from Strava to Supabase

    Args:
        days: Number of days to sync (default 7)
        activity_id: Optional specific Strava activity ID to sync
    """

    print("=" * 50)
    print("🟠 Strava Data Sync Starting...")
    print("=" * 50)

    try:
        access_token = get_strava_access_token()
        print("✅ Connected to Strava API")

        if activity_id:
            # Sync specific activity
            print(f"\n📥 Fetching specific activity: {activity_id}")
            activity = get_strava_activity_details(activity_id, access_token)

            if activity:
                activities = [activity]
            else:
                print("❌ Activity not found")
                return
        else:
            # Sync recent activities
            print(f"\n📥 Fetching activities from last {days} days...")
            activities = fetch_strava_activities(days)
            print(f"✅ Found {len(activities)} activities")

        # Filter for Peloton activities only
        peloton_activities = [
            act for act in activities
            if act.get('device_name') == 'Peloton Bike' or
               (act.get('trainer') and 'Peloton' in str(act.get('device_name', '')))
        ]

        if not activity_id and peloton_activities:
            print(f"🚴 Filtered to {len(peloton_activities)} Peloton activities (out of {len(activities)} total)")
            activities = peloton_activities
        elif not activity_id and not peloton_activities:
            print(f"ℹ️  No Peloton activities found in last {days} days")
            return

        # Process each activity
        synced_count = 0
        updated_count = 0

        for i, activity in enumerate(activities, 1):
            activity_name = activity.get('name', 'Unknown')
            activity_date = activity.get('start_date_local', 'Unknown')[:10]
            activity_type = activity.get('type', 'Unknown')
            device_name = activity.get('device_name', 'Unknown')

            print(f"\n  [{i}/{len(activities)}] {activity_name} ({activity_date})")
            print(f"      Type: {activity_type} | Device: {device_name}")

            # Get detailed data if needed
            if activity_id or activity.get('average_watts'):
                # We already have details or it's a specific request
                activity_details = activity
            else:
                # Fetch detailed data
                activity_details = get_strava_activity_details(activity['id'], access_token)

            if activity_details:
                # Parse activity data
                activity_data = parse_strava_activity(activity_details)

                # Check if this activity exists in Supabase
                existing = supabase.table('activities').select('*').eq('date', activity_data['date']).eq('workout_name', activity_data['workout_name']).execute()

                if existing.data:
                    # Check if power data is missing
                    existing_activity = existing.data[0]

                    if not existing_activity.get('avg_power') and activity_data.get('avg_power'):
                        # Update with Strava power data
                        print(f"      ⚡ Updating with power data: {activity_data.get('avg_power')}W avg, {activity_data.get('normalized_power')}W normalized")

                        supabase.table('activities').update(activity_data).eq('id', existing_activity['id']).execute()
                        updated_count += 1
                        print(f"      ✅ Updated existing activity")
                    else:
                        print(f"      ⏭️  Activity already has complete data")
                else:
                    # Insert new activity
                    print(f"      ⚡ Power: {activity_data.get('avg_power')}W avg, {activity_data.get('normalized_power')}W normalized")

                    supabase.table('activities').insert(activity_data).execute()
                    synced_count += 1
                    print(f"      ✅ Inserted new activity")

            # Rate limiting
            time.sleep(0.5)

        print("\n" + "=" * 50)
        print("✅ Strava sync complete!")
        print("=" * 50)
        print(f"\n📊 Results:")
        print(f"  • New activities synced: {synced_count}")
        print(f"  • Activities updated: {updated_count}")
        print(f"  • Total processed: {len(activities)}")

    except Exception as e:
        print(f"\n❌ Error during Strava sync: {e}")
        raise


if __name__ == '__main__':
    import sys

    # Check for specific activity ID
    if len(sys.argv) > 1:
        activity_id = sys.argv[1]
        print(f"Syncing specific activity: {activity_id}")
        sync_from_strava(activity_id=activity_id)
    else:
        # Default: sync last 7 days
        sync_from_strava(days=7)
