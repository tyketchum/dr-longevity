# Setup Checklist

Follow these steps to get your Longevity Dashboard up and running:

## ✅ Step 1: Install Dependencies

### Python (Backend)
```bash
pip install -r requirements.txt
```

Expected packages:
- garminconnect
- sqlalchemy
- fastapi
- uvicorn
- pandas
- python-dotenv

### Node.js (Frontend)
```bash
cd frontend
npm install
cd ..
```

Expected packages:
- react
- react-router-dom
- recharts
- axios

---

## ✅ Step 2: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# REQUIRED
GARMIN_EMAIL=your_email@example.com
GARMIN_PASSWORD=your_password

# OPTIONAL (for PushPress integration)
PUSHPRESS_API_KEY=
PUSHPRESS_GYM_ID=
```

**Important Notes:**
- Garmin credentials are needed to sync your wellness data
- PushPress is optional - you can manually enter CrossFit workouts
- All data stays local on your machine

---

## ✅ Step 3: Initial Data Sync

This is the most important step - it authenticates with Garmin and pulls 90 days of historical data:

```bash
python3 backend/scripts/initial_setup.py
```

**What to expect:**
1. Script will authenticate with Garmin Connect (credentials from .env)
2. May require browser authentication on first run
3. Pulls 90 days of:
   - Daily wellness metrics (HR, HRV, Body Battery, Sleep, Steps)
   - Activities (cycling, running, strength, etc.)
4. Calculates activity gaps and streak
5. Generates weekly summaries

**Troubleshooting:**
- If authentication fails, check your credentials in `.env`
- If Garmin requires 2FA, you may need to disable it temporarily
- Tokens are saved in `~/.garmin_tokens/` for future use

---

## ✅ Step 4: Start the Backend API

```bash
python3 backend/main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Leave this terminal running.

**Test it works:**
Visit http://localhost:8000/status in your browser - you should see JSON with your activity status.

---

## ✅ Step 5: Start the Frontend Dashboard

In a **new terminal**:

```bash
cd frontend
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view longevity-dashboard in the browser.

  Local:            http://localhost:3000
```

Your browser should automatically open to http://localhost:3000

---

## ✅ Step 6: Verify Everything Works

### Check the Command Center:
- [ ] "Days Since Last Activity" alert is showing
- [ ] Activity streak counter is displaying
- [ ] Today's metrics are populated (HR, Body Battery, Sleep, Steps)
- [ ] Trend charts show data

### Check the Activities Page:
- [ ] Past 90 days of activities are listed
- [ ] Activities are classified (Zone 2, VO2 Max, Strength, Other)
- [ ] Gap tracking is showing (days since previous activity)
- [ ] Can add a manual CrossFit workout (test the form)

### Check the Weekly Log:
- [ ] Past 12 weeks are showing
- [ ] Zone 2 and Strength session counts are correct
- [ ] Longest gap is highlighted in red if >2 days
- [ ] Target achievement indicators are working

### Check the Calendar:
- [ ] Activity heatmap is showing
- [ ] Days with activities are highlighted
- [ ] Can navigate between months

### Check Labs & Strength:
- [ ] Can add a lab entry (test the form)
- [ ] Can add strength PRs

---

## ✅ Step 7: Set Up Daily Sync (Optional but Recommended)

To automatically sync new data from Garmin daily:

### macOS/Linux (Cron):
```bash
crontab -e
```

Add this line (update path to your project):
```
0 7 * * * cd /Users/yourusername/path/to/project && python3 backend/scripts/daily_sync.py >> logs/sync.log 2>&1
```

This runs every day at 7:00 AM.

### Windows (Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 7:00 AM
4. Action: Start a program
5. Program: `python3`
6. Arguments: `backend/scripts/daily_sync.py`
7. Start in: `C:\path\to\project`

---

## ✅ Step 8: Customize Your Targets (Optional)

Edit `.env` to adjust targets for your fitness level:

```bash
# Your personal targets
TARGET_RESTING_HR=60              # Lower is better for longevity
TARGET_ZONE2_SESSIONS_PER_WEEK=3  # 3-4 recommended
TARGET_STRENGTH_SESSIONS_PER_WEEK=3
TARGET_STEPS_PER_DAY=8000
TARGET_WEIGHT_LBS=175             # Your target weight
TARGET_MAX_DAYS_BETWEEN_ACTIVITIES=2  # CRITICAL - never exceed this!

# Your Zone 2 HR range (adjust based on age/fitness)
ZONE2_HR_MIN=120
ZONE2_HR_MAX=140

# Your VO2 Max HR threshold (typically 85-95% of max HR)
VO2MAX_HR_MIN=170
```

After changing targets, restart the backend server.

---

## 🎉 You're All Set!

Your Longevity Dashboard is now running and tracking your health data.

### Daily Workflow:
1. Train as usual (Garmin will automatically track)
2. Run daily sync (manual or automated): `python3 backend/scripts/daily_sync.py`
3. Check your dashboard for streak status and target achievement
4. Log manual CrossFit workouts in the Activities page
5. Add lab results as you get them

### Quick Start (After Initial Setup):
```bash
./start.sh
```

This launches both backend and frontend servers.

---

## 📞 Support

If something doesn't work:

1. Check the **Troubleshooting** section in README.md
2. Verify your `.env` file has correct credentials
3. Check that both servers are running
4. Look for error messages in the terminal

Most common issues:
- Garmin authentication fails → Check credentials
- No data showing → Re-run initial setup script
- Activities not classified → Check HR zones in `.env`
- Dashboard won't load → Check backend is running on port 8000

---

**Now go build that 65-year health optimization streak! 🏃‍♂️💪🧠**
