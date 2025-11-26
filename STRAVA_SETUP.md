# Strava API Setup Guide

This guide will help you set up the Strava integration to automatically fetch power data that might be missing from Garmin Connect.

## Why Strava Integration?

Your Peloton activities sync to Strava first, then to Garmin Connect. Sometimes the Garmin sync drops power data. By connecting directly to Strava, we can:
- ✅ Automatically fill in missing power data
- ✅ Get the most accurate metrics from the source
- ✅ Avoid manual re-syncing

## Step 1: Create a Strava API Application

1. Go to https://www.strava.com/settings/api
2. Click "Create & Manage Your App" (or "My API Application")
3. Fill in the application details:
   - **Application Name**: `Dr. Longevity Sync` (or any name you prefer)
   - **Category**: `Data Importer`
   - **Club**: Leave blank
   - **Website**: `http://localhost`
   - **Authorization Callback Domain**: `localhost`
   - **Description**: "Personal fitness data sync tool"

4. Click "Create"

5. You'll see your **Client ID** and **Client Secret** - save these!

## Step 2: Get Your Refresh Token

You'll need to authorize your app to access your Strava data. Run this script:

```bash
python3 strava_auth.py
```

This will:
1. Open your browser to Strava's authorization page
2. Ask you to authorize the app
3. Generate a refresh token
4. Save the token to your `.env` file

## Step 3: Add Credentials to .env

Add these lines to your `.env` file:

```bash
# Strava API
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
STRAVA_REFRESH_TOKEN=your_refresh_token_here
```

## Step 4: Test the Integration

Run a test sync to verify everything works:

```bash
# Sync last 7 days from Strava
python3 strava_sync.py

# Or sync a specific activity by Strava ID
python3 strava_sync.py 12345678901
```

## How It Works

### Automatic Fallback

The integration is designed to work as a smart fallback:

1. **Primary**: Garmin sync runs first (fast, existing workflow)
2. **Fallback**: If power data is missing, Strava sync fills it in
3. **Update**: Existing activities are updated with missing power data

### What Data Gets Synced

From Strava activities, we capture:
- ✅ Average Power (watts)
- ✅ Weighted Average Power / Normalized Power (watts)
- ✅ Max Power (watts)
- ✅ Total Work (kilojoules)
- ✅ Average Heart Rate
- ✅ Average Cadence
- ✅ Elevation Gain
- ✅ Activity Name & Type

### Manual Sync for Specific Activities

If you notice a specific activity is missing power data:

1. Find the activity on Strava.com
2. Get the activity ID from the URL (e.g., `strava.com/activities/12345678901` → ID is `12345678901`)
3. Run: `python3 strava_sync.py 12345678901`

This will fetch that specific activity and update your database.

## Automated Sync

### Option 1: Combined Sync Script

We can enhance `dr_longevity_sync_improved.py` to automatically run Strava sync after Garmin:

```bash
# Run both syncs
python3 dr_longevity_sync_improved.py  # Garmin first
python3 strava_sync.py                  # Strava fills gaps
```

### Option 2: GitHub Actions

Update your GitHub Actions workflow to run both syncs:

```yaml
- name: Sync Garmin Data
  run: SYNC_DAYS=7 python3 dr_longevity_sync_improved.py

- name: Fill Missing Data from Strava
  run: python3 strava_sync.py
```

## Troubleshooting

### "Failed to get Strava access token"

- Check that your `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` are correct
- Verify your `STRAVA_REFRESH_TOKEN` is set
- Re-run `strava_auth.py` to get a fresh token

### "Activity not found"

- Make sure the activity ID is correct
- Check that the activity is visible on Strava (not private)
- Verify you're authorized to access the activity

### Rate Limiting

Strava API has rate limits:
- 100 requests per 15 minutes
- 1,000 requests per day

The script includes automatic rate limiting (0.5 second delay between requests) to stay under these limits.

## Privacy & Security

- Your Strava credentials are stored locally in `.env` (never committed to git)
- The refresh token allows access only to your activity data
- You can revoke access anytime at https://www.strava.com/settings/apps
- The app only reads data, never writes/modifies your Strava activities

## Next Steps

After setup:
1. Run a test sync to verify everything works
2. Check your dashboard to see updated power data
3. Set up automated daily syncs via GitHub Actions (optional)
4. Monitor for any activities missing data

---

**Questions?** Check the main README or create an issue on GitHub.
