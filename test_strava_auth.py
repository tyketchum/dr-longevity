"""
Test and refresh Strava authentication automatically
Run this script to verify your Strava credentials and get fresh tokens
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

def test_strava_auth():
    """Test Strava authentication and refresh token"""
    print("=" * 60)
    print("🔐 Testing Strava Authentication")
    print("=" * 60)

    # Print credentials (masked for security)
    print(f"\n📋 Current Credentials:")
    print(f"   Client ID: {STRAVA_CLIENT_ID}")
    print(f"   Client Secret: {STRAVA_CLIENT_SECRET[:10]}...{STRAVA_CLIENT_SECRET[-10:]}")
    print(f"   Refresh Token: {STRAVA_REFRESH_TOKEN[:10]}...{STRAVA_REFRESH_TOKEN[-10:]}")

    print(f"\n🔄 Attempting to refresh access token...")

    # Try to get a fresh access token
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
        token_data = response.json()

        print(f"\n✅ SUCCESS! Token refreshed successfully")
        print(f"\n📊 Token Details:")
        print(f"   Access Token: {token_data['access_token'][:20]}...{token_data['access_token'][-20:]}")
        print(f"   Refresh Token: {token_data['refresh_token'][:20]}...{token_data['refresh_token'][-20:]}")
        print(f"   Expires At: {datetime.fromtimestamp(token_data['expires_at']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Token Type: {token_data['token_type']}")

        # Check if refresh token changed
        if token_data['refresh_token'] != STRAVA_REFRESH_TOKEN:
            print(f"\n⚠️  WARNING: Refresh token has changed!")
            print(f"   Old: {STRAVA_REFRESH_TOKEN}")
            print(f"   New: {token_data['refresh_token']}")
            print(f"\n   You should update your .env file and Streamlit secrets with the new refresh token.")

        # Test the access token by getting athlete info
        print(f"\n🏃 Testing access token by fetching athlete info...")
        athlete_response = requests.get(
            'https://www.strava.com/api/v3/athlete',
            headers={'Authorization': f"Bearer {token_data['access_token']}"}
        )

        if athlete_response.status_code == 200:
            athlete = athlete_response.json()
            print(f"✅ Access token works!")
            print(f"   Athlete: {athlete.get('firstname')} {athlete.get('lastname')}")
            print(f"   Username: {athlete.get('username')}")
            print(f"\n🎉 All Strava authentication tests passed!")
            return True
        else:
            print(f"❌ Access token test failed: {athlete_response.status_code}")
            print(f"   Response: {athlete_response.text}")
            return False

    else:
        print(f"\n❌ FAILED to refresh token")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")

        # Provide helpful error messages
        error_data = response.json()
        if 'errors' in error_data:
            for error in error_data['errors']:
                if error.get('field') == 'client_id':
                    print(f"\n🔍 Client ID issue detected!")
                    print(f"   Your client_id might be invalid or the app was deleted")
                    print(f"   Check: https://www.strava.com/settings/api")
                elif error.get('field') == 'refresh_token':
                    print(f"\n🔍 Refresh token issue detected!")
                    print(f"   Your refresh token might be expired or revoked")
                    print(f"   You'll need to reauthorize the application")

        return False

if __name__ == '__main__':
    success = test_strava_auth()
    print("\n" + "=" * 60)
    if success:
        print("✅ Ready to sync Strava data!")
    else:
        print("❌ Fix the issues above before syncing")
    print("=" * 60)
