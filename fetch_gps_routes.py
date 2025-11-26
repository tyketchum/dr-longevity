"""
Fetch GPS route data from Garmin Connect for outdoor cycling activities
Downloads GPX files and parses full GPS tracks
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin
from garth.exc import GarthHTTPError

load_dotenv()

def parse_gpx(gpx_bytes):
    """Parse GPX file and extract GPS coordinates"""
    try:
        # Parse the GPX XML
        root = ET.fromstring(gpx_bytes)

        # GPX namespace
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

        coordinates = []

        # Find all trackpoints in the GPX file
        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            coordinates.append([lat, lon])

        return coordinates
    except Exception as e:
        print(f"     ⚠️  Error parsing GPX: {e}")
        return []


def fetch_cycling_routes(days=None, limit=None):
    """Fetch GPS coordinates from ALL outdoor cycling activities by downloading GPX files"""

    print("🔐 Logging into Garmin Connect...")
    garmin = Garmin(os.getenv('GARMIN_EMAIL'), os.getenv('GARMIN_PASSWORD'))
    garmin.login()
    print("✅ Connected to Garmin Connect")

    if days:
        print(f"\n📡 Fetching cycling activities from last {days} days...")
        start_date = (datetime.now() - timedelta(days=days)).date()
        activities = garmin.get_activities_by_date(
            start_date.isoformat(),
            datetime.now().date().isoformat(),
            activitytype=None
        )
    else:
        print(f"\n📡 Fetching ALL cycling activities from your entire Garmin history...")
        # Fetch all activities (uses pagination internally)
        activities = garmin.get_activities(0, 1000)  # Get up to 1000 activities

    # Filter for outdoor cycling activities
    cycling_types = ['cycling', 'road_biking', 'gravel_cycling', 'mountain_biking']
    outdoor_cycling = [
        act for act in activities
        if any(act_type in act.get('activityType', {}).get('typeKey', '').lower() for act_type in cycling_types)
    ]

    if limit:
        outdoor_cycling = outdoor_cycling[:limit]

    print(f"🚴 Found {len(outdoor_cycling)} outdoor cycling activities")

    routes = []
    for i, activity in enumerate(outdoor_cycling, 1):
        activity_id = activity.get('activityId')
        activity_name = activity.get('activityName', 'Unknown')
        activity_date = activity.get('startTimeLocal', 'Unknown')
        device_name = activity.get('deviceName', 'Unknown')

        try:
            print(f"  [{i}/{len(outdoor_cycling)}] {activity_name} ({activity_date[:10]}) - {device_name}")

            # Download GPX file from Garmin Connect
            gpx_data = garmin.download_activity(activity_id, dl_fmt=Garmin.ActivityDownloadFormat.GPX)

            # Parse GPS coordinates from GPX
            coordinates = parse_gpx(gpx_data)

            if coordinates:
                routes.append({
                    'activity_id': activity_id,
                    'name': activity_name,
                    'date': activity_date,
                    'device': device_name,
                    'coordinates': coordinates,
                    'distance_km': activity.get('distance', 0) / 1000 if activity.get('distance') else 0
                })
                print(f"     ✅ Got {len(coordinates)} GPS points")
            else:
                print(f"     ⚠️  No GPS data in GPX file")

        except Exception as e:
            print(f"     ❌ Error: {e}")
            continue

    # Save routes to JSON file
    output_file = 'cycling_routes.json'
    with open(output_file, 'w') as f:
        json.dump(routes, f, indent=2)

    print(f"\n✅ Saved {len(routes)} routes with GPS data to {output_file}")
    print(f"📍 Total GPS points: {sum(len(r['coordinates']) for r in routes)}")

    return routes

if __name__ == '__main__':
    # Fetch ALL cycling activities from entire Garmin history
    routes = fetch_cycling_routes(days=None, limit=None)
