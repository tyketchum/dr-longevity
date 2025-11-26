"""
Strava OAuth Authorization Helper
Helps you get a refresh token for the Strava API
"""

import os
from dotenv import load_dotenv, set_key
import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

load_dotenv()

# Get client credentials from .env
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')

# Global variable to store the authorization code
auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to receive OAuth callback"""

    def do_GET(self):
        global auth_code

        # Parse the callback URL
        query = parse_qs(urlparse(self.path).query)

        if 'code' in query:
            auth_code = query['code'][0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: #FC4C02;">Success!</h1>
                    <p>You've authorized Dr. Longevity to access your Strava data.</p>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """.encode('utf-8'))
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Error</h1>
                    <p>Authorization failed. Please try again.</p>
                </body>
                </html>
            """.encode('utf-8'))

    def log_message(self, format, *args):
        """Suppress server logs"""
        pass


def get_authorization_code():
    """Start OAuth flow and get authorization code"""

    if not STRAVA_CLIENT_ID:
        print("❌ STRAVA_CLIENT_ID not found in .env file")
        print("\nPlease add your Strava Client ID to .env:")
        print("STRAVA_CLIENT_ID=your_client_id_here")
        return None

    # Build authorization URL
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={STRAVA_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri=http://localhost:8000/callback"
        f"&approval_prompt=force"
        f"&scope=activity:read_all"
    )

    print("=" * 60)
    print("🟠 Strava Authorization")
    print("=" * 60)
    print("\n1. Opening browser to authorize Strava access...")
    print("2. Click 'Authorize' to grant access")
    print("3. You'll be redirected back to this script\n")

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    print("⏳ Waiting for authorization...")
    print("   (Listening on http://localhost:8000)\n")

    server = HTTPServer(('localhost', 8000), CallbackHandler)

    # Handle one request (the callback)
    server.handle_request()

    server.server_close()

    return auth_code


def exchange_code_for_token(auth_code):
    """Exchange authorization code for access and refresh tokens"""

    if not STRAVA_CLIENT_SECRET:
        print("❌ STRAVA_CLIENT_SECRET not found in .env file")
        print("\nPlease add your Strava Client Secret to .env:")
        print("STRAVA_CLIENT_SECRET=your_client_secret_here")
        return None

    print("🔄 Exchanging authorization code for tokens...")

    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code'
        }
    )

    if response.status_code == 200:
        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': token_data['expires_at'],
            'athlete': token_data['athlete']
        }
    else:
        print(f"❌ Failed to get tokens: {response.text}")
        return None


def save_refresh_token(refresh_token):
    """Save refresh token to .env file"""

    env_file = '.env'

    try:
        set_key(env_file, 'STRAVA_REFRESH_TOKEN', refresh_token)
        print(f"✅ Refresh token saved to {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to save token: {e}")
        return False


def test_strava_connection(access_token):
    """Test the connection by fetching athlete info"""

    print("\n🧪 Testing Strava API connection...")

    response = requests.get(
        'https://www.strava.com/api/v3/athlete',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code == 200:
        athlete = response.json()
        print(f"✅ Connected to Strava!")
        print(f"   Athlete: {athlete['firstname']} {athlete['lastname']}")
        print(f"   Username: {athlete['username']}")
        return True
    else:
        print(f"❌ Connection test failed: {response.text}")
        return False


def main():
    """Main authorization flow"""

    print("\n" + "=" * 60)
    print("🟠 Strava API Authorization Setup")
    print("=" * 60)

    # Check prerequisites
    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        print("\n❌ Missing Strava API credentials!")
        print("\n📋 Setup Steps:")
        print("1. Go to https://www.strava.com/settings/api")
        print("2. Create an API application")
        print("3. Add credentials to .env file:")
        print("   STRAVA_CLIENT_ID=your_client_id")
        print("   STRAVA_CLIENT_SECRET=your_client_secret")
        print("\nSee STRAVA_SETUP.md for detailed instructions.")
        return

    # Step 1: Get authorization code
    code = get_authorization_code()

    if not code:
        print("❌ Failed to get authorization code")
        return

    print("✅ Authorization code received!")

    # Step 2: Exchange for tokens
    tokens = exchange_code_for_token(code)

    if not tokens:
        print("❌ Failed to get tokens")
        return

    print("✅ Tokens received!")

    # Step 3: Test connection
    if test_strava_connection(tokens['access_token']):
        # Step 4: Save refresh token
        if save_refresh_token(tokens['refresh_token']):
            print("\n" + "=" * 60)
            print("🎉 Setup Complete!")
            print("=" * 60)
            print("\nYou can now use the Strava sync:")
            print("  python3 strava_sync.py")
            print("\nOr sync a specific activity:")
            print("  python3 strava_sync.py <activity_id>")
        else:
            print("\n⚠️  Token received but not saved to .env")
            print(f"Please manually add to .env:")
            print(f"STRAVA_REFRESH_TOKEN={tokens['refresh_token']}")
    else:
        print("❌ Connection test failed")


if __name__ == '__main__':
    main()
