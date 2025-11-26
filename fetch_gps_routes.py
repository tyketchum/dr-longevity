"""
Fetch GPS route data from Garmin Connect for outdoor cycling activities
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin
from garth.exc import GarthHTTPError

load_dotenv()

def fetch_cycling_routes(days=180, limit=50):
    """Fetch GPS coordinates from recent outdoor cycling activities"""

    print("🔐 Logging into Garmin Connect...")
    garmin = Garmin(os.getenv('GARMIN_EMAIL'), os.getenv('GARMIN_PASSWORD'))
    garmin.login()

    print(f"📡 Fetching cycling activities from last {days} days...")
    start_date = (datetime.now() - timedelta(days=days)).date()
    activities = garmin.get_activities_by_date(
        start_date.isoformat(),
        datetime.now().date().isoformat(),
        activitytype=None  # Get all activities, filter below
    )

    # Filter for outdoor cycling activities
    cycling_types = ['cycling', 'road_biking', 'gravel_cycling', 'mountain_biking']
    outdoor_cycling = [
        act for act in activities
        if any(act_type in act.get('activityType', {}).get('typeKey', '').lower() for act_type in cycling_types)
    ][:limit]

    print(f"🚴 Found {len(outdoor_cycling)} outdoor cycling activities")

    routes = []
    for i, activity in enumerate(outdoor_cycling, 1):
        activity_id = activity.get('activityId')
        activity_name = activity.get('activityName', 'Unknown')
        activity_date = activity.get('startTimeLocal', 'Unknown')

        try:
            print(f"  [{i}/{len(outdoor_cycling)}] Fetching GPS data for: {activity_name} ({activity_date[:10]})")

            # Get detailed activity data with GPS coordinates
            details = garmin.get_activity(activity_id)

            # Try to get GPS data from activity splits
            splits = garmin.get_activity_splits(activity_id)

            # Extract GPS coordinates if available
            coordinates = []

            # Method 1: Check if splits have location data
            if splits and isinstance(splits, list):
                for split in splits:
                    if 'startLatitude' in split and 'startLongitude' in split:
                        lat = split.get('startLatitude')
                        lon = split.get('startLongitude')
                        if lat and lon:
                            # Convert from semicircles to degrees
                            lat_deg = lat * (180 / 2**31) if abs(lat) > 180 else lat
                            lon_deg = lon * (180 / 2**31) if abs(lon) > 180 else lon
                            coordinates.append([lat_deg, lon_deg])

            # Method 2: Check details for start/end coordinates
            if not coordinates and details:
                start_lat = details.get('startLatitude')
                start_lon = details.get('startLongitude')
                end_lat = details.get('endLatitude')
                end_lon = details.get('endLongitude')

                if start_lat and start_lon:
                    coordinates.append([start_lat, start_lon])
                if end_lat and end_lon and (end_lat != start_lat or end_lon != start_lon):
                    coordinates.append([end_lat, end_lon])

            if coordinates:
                routes.append({
                    'activity_id': activity_id,
                    'name': activity_name,
                    'date': activity_date,
                    'coordinates': coordinates,
                    'distance_km': activity.get('distance', 0) / 1000 if activity.get('distance') else 0
                })
                print(f"     ✅ Got {len(coordinates)} GPS points")
            else:
                print(f"     ⚠️  No GPS data available")

        except Exception as e:
            print(f"     ❌ Error fetching GPS data: {e}")
            continue

    # Save routes to JSON file
    output_file = 'cycling_routes.json'
    with open(output_file, 'w') as f:
        json.dump(routes, f, indent=2)

    print(f"\n✅ Saved {len(routes)} routes with GPS data to {output_file}")
    print(f"📍 Total GPS points: {sum(len(r['coordinates']) for r in routes)}")

    return routes

if __name__ == '__main__':
    routes = fetch_cycling_routes(days=180, limit=50)
