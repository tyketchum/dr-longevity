# Deploying to Streamlit Community Cloud 🚀

Your Dr. Longevity App is deployed at: **https://dr-longevity.streamlit.app**

## Current Deployment Status

- **Live URL**: https://dr-longevity.streamlit.app
- **Repository**: tyketchum/dr-longevity
- **Main File**: `dr_longevity_app.py`
- **Auto-Deploy**: Enabled (on git push)

## Important Deployment Notes

### ⚠️ Reboot After Deployment

**IMPORTANT**: After pushing code changes, the app often needs to be manually rebooted to work correctly:

1. Go to https://share.streamlit.io
2. Find your app in the dashboard
3. Click the **"⋮"** menu (three dots)
4. Select **"Reboot app"**
5. Wait for reboot to complete (30 seconds)

This ensures:
- Secrets are reloaded properly
- New code is fully initialized
- Session state is reset

### Secrets Configuration

Your app requires these secrets in Streamlit Cloud (Settings → Secrets):

```toml
[supabase]
url = "https://rqgmobpywjmvdofysqjq.supabase.co"
key = "your_supabase_anon_key"

[garmin]
email = "your_garmin_email@example.com"
password = "your_garmin_password"

[strava]
client_id = 167377
client_secret = "your_strava_client_secret"
refresh_token = "your_strava_refresh_token"

[anthropic]
api_key = "your_anthropic_api_key"
```

**Note**: Use the section-based format above. Top-level keys may not load correctly.

## Updating Your App

### Automatic Deployment

Whenever you push changes to GitHub:
1. Streamlit Cloud detects the changes
2. Automatically redeploys the app
3. **Remember to reboot if needed** (see above)

### Manual Deployment

To force a redeploy:
1. Go to https://share.streamlit.io
2. Click your app
3. Click **"⋮"** → **"Reboot app"**

## Adding a Sync Button

The app includes a "Sync Garmin Data" button in the sidebar. Click it to fetch fresh data from Garmin Connect.

## Sharing Your App

Your app URL can be shared with anyone! They'll be able to view your health data (if that's what you want).

To make it private:
1. Go to app settings
2. Enable "Require password" or restrict access

## Troubleshooting

**App won't start?**
- Check that `requirements_streamlit.txt` is in the repo
- Verify your secrets are set correctly
- Check the logs in the Streamlit Cloud app

**Database empty?**
- Click the "Sync Garmin Data" button in the sidebar
- Or run `python garmin_sync.py` locally and push the database to GitHub

**Need help?**
- Streamlit docs: https://docs.streamlit.io
- Streamlit forum: https://discuss.streamlit.io

---

## Alternative: Running Locally

```bash
# Install dependencies
pip install -r requirements_streamlit.txt

# Create secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your credentials

# Sync Garmin data
python garmin_sync.py

# Run app
streamlit run streamlit_app.py
```

Your app will open at http://localhost:8501
