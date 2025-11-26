"""
Fetch GPS route data from Strava for outdoor cycling activities
(Garmin Edge 1040 rides - not Peloton)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_strava_access_token():
    """Get a fresh access token using refresh token"""
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': os.getenv('STRAVA_CLIENT_ID'),
            'client_secret': os.getenv('STRAVA_CLIENT_SECRET'),
            'grant_type': 'refresh_token',
            'refresh_token': os.getenv('STRAVA_REFRESH_TOKEN')
        }
    )

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get Strava access token: {response.text}")


def fetch_outdoor_cycling_routes(days=180, limit=50):
    """Fetch GPS coordinates from outdoor cycling activities (Garmin Edge, not Peloton)"""

    print("🔐 Logging into Strava...")
    access_token = get_strava_access_token()
    print("✅ Connected to Strava")

    print(f"\n📡 Fetching activities from last {days} days...")
    after_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())

    # Fetch activities
    activities = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'after': after_timestamp, 'per_page': 100}
    ).json()

    # Filter for outdoor rides (NOT Peloton)
    outdoor_rides = [
        act for act in activities
        if act.get('type') == 'Ride' and
           act.get('device_name') != 'Peloton Bike' and
           act.get('start_latlng')  # Has GPS coordinates
    ][:limit]

    print(f"🚴 Found {len(outdoor_rides)} outdoor rides with GPS data")

    routes = []
    for i, activity in enumerate(outdoor_rides, 1):
        activity_id = activity['id']
        activity_name = activity['name']
        activity_date = activity['start_date_local']
        device_name = activity.get('device_name', 'Unknown')

        try:
            print(f"  [{i}/{len(outdoor_rides)}] Fetching GPS for: {activity_name} ({activity_date[:10]}) - {device_name}")

            # Get GPS stream (lat/lng coordinates)
            streams = requests.get(
                f'https://www.strava.com/api/v3/activities/{activity_id}/streams',
                headers={'Authorization': f'Bearer {access_token}'},
                params={'keys': 'latlng', 'key_by_type': 'true'}
            )

            if streams.status_code == 200:
                stream_data = streams.json()

                if 'latlng' in stream_data:
                    coordinates = stream_data['latlng']['data']

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
                    print(f"     ⚠️  No GPS stream available")
            else:
                print(f"     ⚠️  Failed to fetch streams: {streams.status_code}")

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
    routes = fetch_outdoor_cycling_routes(days=180, limit=50)
