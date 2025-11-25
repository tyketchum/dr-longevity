# Supabase Migration - Setup Instructions 🚀

## What I've Done While You Were At Dinner

✅ Created PostgreSQL database schema for Supabase
✅ Updated `garmin_sync.py` to work with Supabase
✅ Updated `streamlit_app.py` to work with Supabase
✅ Created GitHub Actions workflow for automatic syncing (twice daily)
✅ Updated requirements.txt with Supabase library

## What You Need to Do (15 minutes)

### Step 1: Create Supabase Account (5 mins)

1. Go to **https://supabase.com**
2. Click **"Start your project"**
3. Sign in with GitHub (easiest)
4. Create a new organization (name it whatever you want)
5. Create a new project:
   - **Name**: `longevity-app` (or whatever you prefer)
   - **Database Password**: Create a strong password (save it somewhere safe!)
   - **Region**: Choose closest to you (US East, US West, etc.)
   - Click **"Create new project"**
6. Wait 1-2 minutes for project to provision

### Step 2: Set Up Database Schema (3 mins)

1. In your Supabase project, click **"SQL Editor"** in the left sidebar
2. Click **"New query"**
3. Open the file `supabase_schema.sql` on your computer
4. Copy ALL the contents
5. Paste into the Supabase SQL Editor
6. Click **"Run"** (or press Cmd+Enter)
7. You should see: "Database schema created successfully!"

### Step 3: Get Your Credentials (2 mins)

1. Click **"Settings"** (gear icon) in the left sidebar
2. Click **"API"** under Project Settings
3. Copy these two values:

   **Project URL** (looks like: `https://xxxxx.supabase.co`)
   **anon/public key** (long string starting with `eyJ...`)

### Step 4: Add Secrets to Streamlit Cloud (2 mins)

1. Go to **https://share.streamlit.io**
2. Click on your `dr-longevity` app
3. Click **Settings** (⚙️) → **Secrets**
4. Add the following (replace with your actual values):

```toml
[supabase]
url = "https://xxxxx.supabase.co"
key = "eyJhbGc..."

[garmin]
email = "your_email@example.com"
password = "your_password"
```

5. Click **"Save"**

### Step 5: Add Secrets to GitHub Actions (3 mins)

1. Go to **https://github.com/tyketchum/dr-longevity**
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each:

   - Name: `SUPABASE_URL`, Value: Your Supabase project URL
   - Name: `SUPABASE_KEY`, Value: Your Supabase anon key
   - Name: `GARMIN_EMAIL`, Value: Your Garmin email
   - Name: `GARMIN_PASSWORD`, Value: Your Garmin password

4. You should have 4 secrets total

### Step 6: Deploy & Test (5 mins)

#### A. Push New Code to GitHub

Use GitHub Desktop:
1. You should see multiple files changed
2. Commit message: "Migrate to Supabase cloud database"
3. Click **"Commit to main"**
4. Click **"Push origin"**

#### B. Update Streamlit App

1. Go to your Streamlit app settings
2. Change **Main file path** from `streamlit_app.py` to `dr_longevity_app.py`
3. Click **"Save"**
4. App will automatically redeploy

#### C. Run Initial Sync

Option 1 - GitHub Actions (Recommended):
1. Go to **Actions** tab in your GitHub repo
2. Click **"Sync Garmin Data to Supabase"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 2-3 minutes for it to complete
5. Check the logs to confirm success

Option 2 - Local:
```bash
cd /Users/tketchum/Claude/Garmin
pip install supabase
python3 dr_longevity_sync.py
```

#### D. Verify App

1. Go to **https://dr-longevity.streamlit.app**
2. Wait for it to reload
3. You should see your data!
4. If not, click the **"Sync Garmin Data"** button in the sidebar

---

## What Happens Now (Automatic!)

Once setup is complete:

🔄 **Twice Daily Sync**: GitHub Actions will automatically sync your Garmin data at:
   - 12:00 AM CST (6 AM UTC)
   - 12:00 PM CST (6 PM UTC)

📊 **Instant Updates**: Your app will always show the latest data from the cloud database

🎯 **No More Manual Work**: Everything runs automatically!

---

## Files Created/Modified

### New Files:
- `supabase_schema.sql` - Database schema for Supabase
- `dr_longevity_sync.py` - Supabase version of sync script
- `dr_longevity_app.py` - Supabase version of app
- `.github/workflows/sync_garmin_to_supabase.yml` - Automated sync workflow
- `SUPABASE_SETUP_INSTRUCTIONS.md` - This file!

### Modified Files:
- `requirements.txt` - Added `supabase` library

### Legacy Files (Removed):
- Old SQLite versions have been removed for clarity
- `longevity_app.db` - Local database (keep until migration complete)

---

## Troubleshooting

### "Missing Supabase credentials" Error
- Double-check you added secrets in both Streamlit Cloud AND GitHub Actions
- Make sure secret names match exactly (case-sensitive!)

### "Database schema error"
- Make sure you ran the entire `supabase_schema.sql` file
- Check Supabase SQL Editor for any error messages

### "No data showing in app"
- Run the GitHub Actions workflow manually to do initial sync
- Or click "Sync Garmin Data" button in app sidebar
- Check that your Garmin credentials are correct

### GitHub Actions failing
- Go to Actions tab and check the error logs
- Most common: incorrect secrets or Garmin authentication issue

---

## Next Steps After Setup

1. **Delete local database from git** (optional):
   ```bash
   git rm longevity_app.db
   git commit -m "Remove local database, using Supabase"
   git push
   ```

2. **Monitor first automated sync**:
   - Check tomorrow at noon or midnight
   - Go to Actions tab to see if workflow ran successfully

3. **Celebrate!** 🎉
   - You now have a fully automated cloud-based app
   - No more manual syncing or database commits

---

## Need Help?

If anything doesn't work:
1. Check the error message carefully
2. Make sure all 4 GitHub secrets are set
3. Make sure Streamlit secrets are set
4. Verify you ran the SQL schema in Supabase
5. Ask me for help!

---

**Estimated total time**: 15 minutes
**Difficulty**: Easy (just copying and pasting!)
**Result**: Fully automated cloud app! 🚀
