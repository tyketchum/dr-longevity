# Deploying to Streamlit Community Cloud 🚀

Your Longevity App can be deployed for FREE on Streamlit Community Cloud!

## Prerequisites

- GitHub account
- Your Garmin Connect credentials

## Step-by-Step Deployment

### 1. Push Code to GitHub

Make sure your code is pushed to a GitHub repository (public or private).

### 2. Go to Streamlit Community Cloud

Visit: **https://share.streamlit.io**

### 3. Sign In

Click "Sign in with GitHub" and authorize Streamlit.

### 4. Deploy Your App

1. Click **"New app"**
2. Select your repository: `Claude/Garmin` (or wherever this code is)
3. Set the main file path: `streamlit_app.py`
4. Click **"Deploy!"**

### 5. Add Your Secrets

Once deployed (or during deployment):

1. Click on your app settings (⚙️ icon)
2. Go to **"Secrets"**
3. Add your Garmin credentials:

```toml
[garmin]
email = "your_email@example.com"
password = "your_password"
```

4. Click "Save"

### 6. That's It!

Your app is now live! 🎉

You'll get a URL like: `https://your-app-name.streamlit.app`

## Updating Your App

Whenever you push changes to GitHub, Streamlit will automatically redeploy your app!

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
