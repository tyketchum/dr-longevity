# Longevity App - Medicine 3.0 Health Tracking System

A comprehensive performance monitoring app for longevity optimization, integrating Garmin Connect wellness data with CrossFit/strength training tracking. Built for Peter Attia-style Medicine 3.0 health optimization.

## 🎯 Key Features

- **CRITICAL METRIC**: Days Since Last Activity tracker with visual alerts (never go >2 days!)
- **Activity Streak Counter**: Track consecutive days with activity (with milestone celebrations)
- **Garmin Integration**: Automatic sync of wellness data, activities, sleep, HRV, Body Battery
- **CrossFit Tracking**: Manual entry or PushPress API integration
- **Zone 2 & VO2 Max Detection**: Automatic classification based on HR and duration
- **Weekly Performance Log**: Track progress against longevity-focused targets
- **Lab Results Tracking**: ApoB, HbA1c, blood pressure, VO2 max, strength PRs
- **Activity Calendar**: GitHub-style heatmap showing consistency
- **Trend Analysis**: Charts for resting HR, HRV, body battery, weight, and more

## 📊 Tracked Metrics

### Daily Wellness (from Garmin)
- Resting heart rate (target: <60 bpm)
- HRV / Stress score (target: <25)
- Body Battery (target: >70)
- Sleep duration & quality
- Steps (target: >8,000/day)
- Training load

### Activities (Garmin + Manual Entry)
- Auto-classified: Zone 2, VO2 Max, Strength, Other
- HR data, power data (cycling), cadence, elevation
- Gap tracking between activities
- Activity streak counter

### Weekly Targets
- Zone 2 sessions: 3-4/week, 45-60min, HR 120-140 bpm
- Strength/CrossFit: 3 sessions/week
- VO2 Max intervals: 1/week, HR >170 bpm, 25-50min
- **CRITICAL**: No gaps >2 days between activities

### Lab Results (Manual Entry)
- ApoB (target: <60 mg/dL)
- HbA1c (target: <5.2%)
- Blood pressure (target: <120/80)
- VO2 max, body fat %, waist circumference
- Strength 1RMs: Back squat, deadlift, strict OHP

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 16+
- Garmin Connect account
- Garmin Forerunner 935 or Edge 1040 (or any Garmin device)

### 1. Clone and Setup Environment

```bash
cd /path/to/project
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Required
GARMIN_EMAIL=your_garmin_email@example.com
GARMIN_PASSWORD=your_garmin_password

# Optional - for PushPress integration (leave empty to use manual entry)
PUSHPRESS_API_KEY=
PUSHPRESS_GYM_ID=

# Customize your targets
TARGET_RESTING_HR=60
TARGET_ZONE2_SESSIONS_PER_WEEK=3
TARGET_STRENGTH_SESSIONS_PER_WEEK=3
TARGET_STEPS_PER_DAY=8000
TARGET_WEIGHT_LBS=175
ZONE2_HR_MIN=120
ZONE2_HR_MAX=140
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Initial Garmin Data Sync (ONE-TIME SETUP)

This will authenticate with Garmin Connect and pull 90 days of historical data:

```bash
python3 backend/scripts/initial_setup.py
```

**Important**: On first run, Garmin may require browser authentication. Follow the prompts. Your tokens will be saved for future use.

Expected output:
```
Fetching 90 days of historical data from Garmin Connect...
✓ Logged in to Garmin Connect and saved tokens
Fetching activities from 2024-08-26 to 2024-11-24...
✓ Fetched 87 activities
✓ Fetched 90 days of wellness metrics
Recalculating activity gaps and streaks...
✓ Current streak: 5 days
✓ Days since last activity: 0.5
✓ Calculated 12 weekly summaries
SETUP COMPLETE!
```

### 5. Start the Backend API

```bash
python3 backend/main.py
```

API will run on `http://localhost:8000`

### 6. Start the Frontend App

In a new terminal:

```bash
cd frontend
npm start
```

App will open at `http://localhost:3000`

## 📅 Daily Sync

Run this once per day (manually or via cron) to sync yesterday's data:

```bash
python3 backend/scripts/daily_sync.py
```

### Automate with Cron (macOS/Linux)

Add to your crontab (`crontab -e`):

```bash
# Sync Garmin data daily at 7:00 AM
0 7 * * * cd /path/to/project && python3 backend/scripts/daily_sync.py >> logs/sync.log 2>&1
```

### Automate with Task Scheduler (Windows)

Create a scheduled task to run `daily_sync.py` every morning.

## 📖 How to Use

### Command Center (Home Page)

- **BIG RED ALERT**: Shows days since last activity
  - Green (0-1 days): ✓ Active
  - Yellow (1-2 days): ⚠ Rest day ending
  - Red (>2 days): 🚨 GET MOVING NOW!
- **Streak Counter**: Current activity streak (celebrates milestones at 7, 14, 30, 60, 90+ days)
- **Today's Metrics**: Resting HR, Body Battery, Stress, Sleep, Steps, Weight
- **Trend Charts**: Resting HR, Body Battery, Stress over past 90 days
- **This Week's Performance**: Zone 2, Strength, VO2 Max session counts

### Activities Page

- **View all activities** from past 90 days with gap tracking
- **Add CrossFit workouts manually** if PushPress API not available
- **Auto-classification**: Activities are classified as Zone 2, VO2 Max, Strength, or Other
- **Gap highlighting**: Gaps >2 days shown in RED

### Weekly Log

- **12-week summary** with target achievement tracking
- **Perfect weeks** highlighted in green (hit all targets + no long gaps)
- **Weeks with >2 day gaps** highlighted in red
- **Target indicators**: Green checkmarks when targets met

### Calendar

- **GitHub-style heatmap** showing activity consistency
- **Green days**: Activity logged
- **Gray days**: No activity
- Navigate between months

### Labs & Strength

- **Add lab results**: ApoB, HbA1c, blood pressure, body composition
- **Track strength progress**: 1RM charts for squat, deadlift, overhead press
- **VO2 max tracking**: Monitor cardiorespiratory fitness over time

## 🎯 Target Guidelines (Medicine 3.0 / Peter Attia)

### Cardiovascular Health
- **Zone 2 Training**: 3-4 sessions per week, 45-60 minutes each
  - Target HR: 120-140 bpm (adjust for your age/fitness)
  - Builds mitochondrial function and fat oxidation
  - Should be able to hold a conversation but not sing

- **VO2 Max Training**: 1 session per week (after 8-week base)
  - Target HR: >170 bpm (85-95% max HR)
  - Duration: 25-50 minutes (including intervals and rest)
  - Improves peak cardiovascular capacity

### Strength & Stability
- **Strength Training**: 3 sessions per week
  - CrossFit, weightlifting, resistance training
  - Focus on functional movements and compound lifts
  - Prevents sarcopenia (age-related muscle loss)

### Recovery & Consistency
- **No gaps >2 days**: Most important behavioral metric
  - Maintains metabolic adaptations
  - Prevents detraining
  - Builds habit consistency

- **Resting HR**: <60 bpm (indicator of cardiovascular fitness)
- **HRV/Stress**: <25 (lower stress = better recovery)
- **Body Battery**: >70 (indicates readiness for hard training)
- **Steps**: >8,000 per day (NEAT - non-exercise activity thermogenesis)

### Lab Markers
- **ApoB**: <60 mg/dL (atherosclerotic cardiovascular disease risk)
- **HbA1c**: <5.2% (glucose control)
- **Blood Pressure**: <120/80 mmHg
- **VO2 Max**: >50 ml/kg/min (top 20% for age)

## 🛠️ Troubleshooting

### Garmin Authentication Issues

If Garmin login fails:

1. Delete saved tokens: `rm -rf ~/.garmin_tokens/`
2. Re-run setup: `python3 backend/scripts/initial_setup.py`
3. Check your email/password in `.env`
4. Ensure you don't have 2FA enabled on Garmin (not currently supported)

### No Data Showing in App

1. Check backend is running: `http://localhost:8000/status`
2. Check database was created: `ls -la longevity_app.db`
3. Re-run initial sync: `python3 backend/scripts/initial_setup.py`

### Activities Not Classified Correctly

Zone 2 and VO2 Max classification requires:
- Heart rate data from Garmin
- Cycling or running activities
- Correct HR zones configured in `.env`

Adjust your targets in `.env`:
```bash
ZONE2_HR_MIN=120  # Adjust for your fitness level
ZONE2_HR_MAX=140
VO2MAX_HR_MIN=170  # Usually 85-95% of max HR
```

### PushPress Integration

PushPress API is available but requires an API key from your gym. If unavailable, use manual entry form in Activities page.

## 📁 Project Structure

```
.
├── backend/
│   ├── models/           # SQLAlchemy database models
│   ├── services/         # Garmin API, data sync, activity classifier
│   ├── scripts/          # Setup and daily sync scripts
│   └── main.py           # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/   # React components (alerts, streak counter)
│   │   ├── pages/        # App pages
│   │   └── services/     # API client
│   └── package.json
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── README.md
```

## 🔒 Data Privacy

- All data stored locally in SQLite database (`longevity_app.db`)
- No cloud services or third-party analytics
- Garmin tokens stored in `~/.garmin_tokens/` (excluded from git)
- You own 100% of your health data

## 🚧 Known Limitations

- Garmin Connect API is unofficial (uses `garminconnect` library)
- No mobile app (web-only, but mobile-responsive)
- CSV export not yet implemented
- Push notifications not yet implemented
- No integration with Oura, Whoop, or Apple Health (future enhancement)

## 🎉 Feature Roadmap (Stretch Goals)

- [ ] CSV export functionality
- [ ] Push notifications for 2-day activity alerts
- [ ] Progressive Web App (PWA) for mobile
- [ ] Dark mode toggle
- [ ] Predictive analytics (trend forecasting)
- [ ] Auto-insights generation ("Your RHR is trending down 2bpm/month!")
- [ ] Integration with Apple Health / Oura / Whoop
- [ ] Social sharing ("I just hit a 60-day streak!")

## 📚 References

- [Peter Attia - Exercise for Longevity](https://peterattiamd.com/exercise/)
- [Medicine 3.0 Framework](https://peterattiamd.com/outlive/)
- [Garmin Connect API](https://github.com/cyberjunky/python-garminconnect)
- [Zone 2 Training Guide](https://www.trainingpeaks.com/learn/articles/zone-2-heart-rate-training/)

## 📝 License

MIT License - Use this for the next 65 years of longevity optimization!

---

**Built for Medicine 3.0 health optimization. Train smart, live long. 🏃‍♂️💪🧠**
