# Longevity Dashboard - Project Overview

## 🎯 Mission

Build a production-ready health tracking system optimized for longevity, with a laser focus on the **#1 behavioral metric: Never go more than 2 days without activity**.

This is your accountability mechanism for the next 65 years.

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (REST API)
- SQLAlchemy (ORM)
- SQLite (Database)
- garminconnect (Unofficial Garmin API)

**Frontend:**
- React 18
- React Router (Navigation)
- Recharts (Data Visualization)
- Axios (API Client)

**Deployment:**
- Local-first (no cloud dependencies)
- Mobile-responsive web interface
- All data owned by user

---

## 📁 Project Structure

```
longevity-dashboard/
├── backend/
│   ├── models/                 # Database models
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── daily_metrics.py    # Daily wellness data
│   │   ├── activities.py       # Activity tracking
│   │   ├── weekly_summary.py   # Weekly aggregations
│   │   └── monthly_labs.py     # Lab results & measurements
│   ├── services/               # Business logic
│   │   ├── garmin_service.py   # Garmin API integration
│   │   ├── activity_classifier.py  # Zone 2/VO2 Max/Strength classification
│   │   └── data_sync.py        # Sync & aggregation engine
│   ├── scripts/                # Utility scripts
│   │   ├── initial_setup.py    # One-time 90-day sync
│   │   ├── daily_sync.py       # Daily data refresh
│   │   └── export_csv.py       # Backup to CSV
│   └── main.py                 # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ActivityGapAlert.js   # CRITICAL: Days since last activity
│   │   │   └── StreakCounter.js      # Activity streak with milestones
│   │   ├── pages/              # Dashboard pages
│   │   │   ├── CommandCenter.js     # Main dashboard
│   │   │   ├── Activities.js        # Activity log + manual entry
│   │   │   ├── WeeklyLog.js         # 12-week performance table
│   │   │   ├── Calendar.js          # Activity heatmap
│   │   │   └── Labs.js              # Lab results & strength tracking
│   │   ├── services/
│   │   │   └── api.js          # Axios API client
│   │   ├── App.js              # Main React component
│   │   ├── index.js            # React entry point
│   │   └── index.css           # Global styles
│   ├── public/
│   │   └── index.html
│   └── package.json
├── .env.example                # Environment template
├── .gitignore
├── requirements.txt            # Python dependencies
├── start.sh                    # Quick start script
├── README.md                   # Full documentation
├── SETUP_CHECKLIST.md          # Step-by-step setup
├── QUICK_REFERENCE.md          # Common tasks & commands
└── PROJECT_OVERVIEW.md         # This file
```

---

## 🗄️ Database Schema

### `daily_metrics`
**Purpose**: Store daily wellness data from Garmin

| Column | Type | Description |
|--------|------|-------------|
| date | Date | Primary key |
| resting_hr | Integer | Resting heart rate (bpm) |
| hrv | Float | Heart rate variability (ms) |
| stress_score | Integer | Garmin stress 0-100 (lower better) |
| body_battery | Integer | Garmin recovery metric 0-100 |
| weight | Float | Body weight (lbs) |
| sleep_hours | Float | Total sleep duration |
| sleep_score | Integer | Garmin sleep quality score |
| sleep_deep_hours | Float | Deep sleep duration |
| sleep_light_hours | Float | Light sleep duration |
| sleep_rem_hours | Float | REM sleep duration |
| sleep_awake_hours | Float | Awake time during night |
| steps | Integer | Daily step count |
| floors_climbed | Integer | Floors climbed |
| intensity_minutes | Integer | Garmin intensity minutes |
| training_load | Integer | Garmin training load |
| respiration_rate | Float | Breaths per minute |
| spo2 | Float | Blood oxygen % |
| days_since_last_activity | Integer | **CRITICAL METRIC** |
| current_streak | Integer | Activity streak (days) |

### `activities`
**Purpose**: Store all activities (Garmin + manual CrossFit)

| Column | Type | Description |
|--------|------|-------------|
| activity_id | String | Garmin activity ID |
| date | Date | Activity date |
| start_time | DateTime | Exact start time |
| source | String | 'garmin' or 'crossfit' |
| activity_type | String | cycling, running, strength, etc. |
| zone_classification | String | zone2, vo2max, strength, other |
| duration_minutes | Float | Duration |
| distance_km | Float | Distance (if applicable) |
| avg_hr | Integer | Average heart rate |
| max_hr | Integer | Max heart rate |
| avg_power | Integer | Average power (cycling) |
| avg_cadence | Integer | Average cadence |
| elevation_gain | Float | Elevation gain (meters) |
| calories | Integer | Calories burned |
| aerobic_training_effect | Float | Garmin training effect |
| vo2max_estimate | Float | VO2 max estimate |
| workout_name | String | CrossFit workout name |
| perceived_effort | Integer | 1-10 scale |
| hours_since_previous | Float | **Gap tracking** |
| days_since_previous | Float | **Gap tracking** |
| notes | Text | Freeform notes |

### `weekly_summary`
**Purpose**: Aggregated weekly statistics

| Column | Type | Description |
|--------|------|-------------|
| week_start_date | Date | Monday of week |
| week_end_date | Date | Sunday of week |
| avg_resting_hr | Float | 7-day average |
| avg_hrv | Float | 7-day average |
| avg_stress_score | Float | 7-day average |
| avg_body_battery | Float | 7-day average |
| avg_weight | Float | 7-day moving average |
| avg_sleep_hours | Float | Weekly average |
| avg_sleep_score | Float | Weekly average |
| zone2_sessions | Integer | Count of Zone 2 sessions |
| vo2max_sessions | Integer | Count of VO2 Max sessions |
| strength_sessions | Integer | Count of Strength sessions |
| total_activities | Integer | Total activities this week |
| zone2_avg_hr | Float | Avg HR across Zone 2 sessions |
| zone2_total_minutes | Float | Total Zone 2 time |
| total_training_load | Integer | Sum of training load |
| avg_daily_steps | Integer | Average daily steps |
| longest_gap_days | Float | **Longest gap between activities** |
| activity_streak_end | Integer | Streak at end of week |
| days_with_activity | Integer | Days that had activity |
| missed_activity_days | Integer | Days with >2 day gap |
| hit_zone2_target | Boolean | Did we hit 3-4 Zone 2 sessions? |
| hit_strength_target | Boolean | Did we hit 3 strength sessions? |
| hit_steps_target | Boolean | Did we hit 8000+ steps avg? |
| no_long_gaps | Boolean | Did we avoid >2 day gaps? |
| perfect_week | Boolean | **All targets met!** |

### `monthly_labs`
**Purpose**: Lab results, measurements, and strength PRs

| Column | Type | Description |
|--------|------|-------------|
| date | Date | Test/measurement date |
| entry_type | String | 'lab', 'measurement', 'strength' |
| apob | Float | ApoB (mg/dL) - Target: <60 |
| hba1c | Float | HbA1c (%) - Target: <5.2 |
| bp_systolic | Integer | Blood pressure systolic |
| bp_diastolic | Integer | Blood pressure diastolic |
| vo2max | Float | VO2 max (ml/kg/min) |
| body_fat_percent | Float | Body fat % (DEXA) |
| waist_circumference | Float | Waist (inches) |
| back_squat_1rm | Float | Back squat 1RM (lbs) |
| deadlift_1rm | Float | Deadlift 1RM (lbs) |
| ohp_1rm | Float | Strict overhead press 1RM (lbs) |
| notes | String | Freeform notes |

---

## 🔄 Data Flow

### Initial Setup (One-time)
```
User → initial_setup.py
       ↓
   GarminService.login()
       ↓
   Fetch 90 days of data
       ↓
   Save to database (daily_metrics, activities)
       ↓
   ActivityClassifier.classify_all()
       ↓
   ActivityClassifier.calculate_gaps()
       ↓
   DataSyncService.calculate_weekly_summaries()
       ↓
   Dashboard shows data ✅
```

### Daily Sync (Automated)
```
Cron job → daily_sync.py (7:00 AM)
           ↓
       GarminService.get_daily_metrics(yesterday)
           ↓
       GarminService.get_activities(yesterday)
           ↓
       Save to database
           ↓
       Recalculate gaps & streak
           ↓
       Update weekly summary
           ↓
       User refreshes dashboard → sees updated data
```

### Manual Activity Entry
```
User → Activities page → Add CrossFit Workout
       ↓
   POST /activities (API)
       ↓
   Save to activities table (source='crossfit')
       ↓
   DataSyncService.recalculate_all_gaps()
       ↓
   Dashboard updates automatically
```

### Lab Entry
```
User → Labs page → Add Entry
       ↓
   POST /labs (API)
       ↓
   Save to monthly_labs table
       ↓
   Chart updates to show new data point
```

---

## 🎯 Key Features

### 1. Activity Gap Alert (CRITICAL)
**Location**: Command Center (home page)
**Purpose**: Make it PAINFUL to see >2 days since last activity

**Logic**:
```python
gap = (now - last_activity.start_time).days

if gap < 1.5:
    alert = "GREEN" → "✓ ACTIVE"
elif gap < 2.0:
    alert = "YELLOW" → "⚠ REST DAY ENDING"
else:
    alert = "RED" → "🚨 GET MOVING NOW!"
```

**Visual Design**:
- Green: Subtle border, small font
- Yellow: Warning colors, larger font
- Red: HUGE text, pulsing animation, impossible to ignore

### 2. Activity Streak Counter
**Location**: Command Center
**Purpose**: Gamification + motivation

**Logic**:
```python
streak = 0
for activity in reversed(activities):
    if days_since_previous <= 2.0:
        streak += 1
    else:
        break  # Streak broken
```

**Milestones** (with celebration animations):
- 7 days: "Great start! ✨"
- 14 days: "Two weeks! 🔥"
- 30 days: "One month! 🔥🔥"
- 60 days: "Unstoppable! 🔥🔥🔥"
- 90 days: "This is your lifestyle now! ⚡"
- 180 days: "Medicine 3.0 Champion! 💎"
- 365 days: "You are immortal! 🏆"

### 3. Auto Activity Classification
**Location**: Backend service
**Purpose**: Automatically categorize activities based on HR + duration

**Classification Logic**:
```python
def classify_activity(activity):
    if activity.source == 'crossfit':
        return 'strength'

    if 'strength' in activity.activity_type:
        return 'strength'

    if activity.activity_type in ['cycling', 'running']:
        # Zone 2: 40+ min, HR 120-140
        if duration >= 40 and 120 <= avg_hr <= 140:
            return 'zone2'

        # VO2 Max: 25-50 min, HR >170
        if 25 <= duration <= 50 and avg_hr >= 170:
            return 'vo2max'

    return 'other'
```

### 4. Weekly Target Tracking
**Location**: Weekly Log page
**Purpose**: Show progress toward longevity-focused targets

**Targets**:
- Zone 2: 3-4 sessions/week ✅
- Strength: 3 sessions/week ✅
- VO2 Max: 1 session/week ✅
- No gaps >2 days ✅
- Steps: 8000+/day avg ✅

**Perfect Week** = All targets met!

### 5. Calendar Heatmap
**Location**: Calendar page
**Purpose**: Visual consistency tracker (like GitHub contributions)

**Color Coding**:
- 🟢 Green: Activity logged
- ⚪ Gray: No activity (shame!)

**Psychology**: Seeing a long streak of green squares is HIGHLY motivating.

---

## 🔌 API Endpoints

### GET /status
Returns current activity status (days since last activity, streak, alert level)

### GET /daily-metrics?days=90
Returns daily wellness metrics for past N days

### GET /activities?days=90
Returns activities for past N days with gap tracking

### GET /weekly-summaries?weeks=12
Returns weekly summary statistics

### GET /labs
Returns all lab results and measurements

### GET /calendar?year=2024&month=11
Returns activity data for calendar heatmap

### POST /activities
Add manual activity (CrossFit workout)

### POST /labs
Add lab result or measurement

### POST /sync/daily
Trigger manual sync of yesterday's data

### POST /sync/historical?days=90
Trigger historical sync (initial setup)

### POST /export/csv
Export all data to CSV files

---

## 🎨 Design Philosophy

### Colors
- **Green (#00ff88)**: Target achieved, healthy, active
- **Yellow (#ffc107)**: Warning, approaching threshold
- **Red (#ff5252)**: ALERT, missed target, gap >2 days
- **Dark Theme**: Easy on eyes, modern, focus on data

### Typography
- **Big numbers**: Metrics are visual, easy to scan
- **Color-coded values**: Instant feedback on targets
- **Minimal text**: Data speaks for itself

### Layout
- **Mobile-first**: Responsive grid layouts
- **Card-based**: Modular, easy to scan
- **Charts**: Trends over time (Recharts library)

### User Experience
- **Zero friction**: No login, no cloud, just run locally
- **Fast**: SQLite queries are instant
- **Reliable**: Offline-first, no dependencies on external services

---

## 🔐 Security & Privacy

### Data Storage
- **Local SQLite database** (`longevity_dashboard.db`)
- **No cloud sync** (by design)
- **No analytics** or tracking
- **User owns 100%** of data

### Credentials
- Garmin credentials stored in `.env` (gitignored)
- OAuth tokens stored in `~/.garmin_tokens/` (gitignored)
- No passwords sent to any server except Garmin

### Backup Strategy
- **CSV export**: `python3 backend/scripts/export_csv.py`
- **Database backup**: Copy `longevity_dashboard.db` file
- Recommended: Weekly CSV exports to external drive

---

## 📈 Future Enhancements

### Phase 2 (Stretch Goals)
- [ ] Push notifications (2-day alert)
- [ ] Progressive Web App (mobile app experience)
- [ ] Dark mode toggle
- [ ] Predictive analytics (trend forecasting)
- [ ] Auto-insights ("Your RHR is trending down 2bpm/month!")

### Phase 3 (Integrations)
- [ ] Apple Health integration
- [ ] Oura Ring integration
- [ ] Whoop integration
- [ ] Strava sync (backup for Garmin data)

### Phase 4 (Social)
- [ ] Share streak achievements
- [ ] Compare with friends (opt-in)
- [ ] Community challenges

---

## 🧪 Testing Strategy

### Manual Testing Checklist
- [ ] Initial setup syncs 90 days
- [ ] Daily sync updates yesterday's data
- [ ] Activity gap alert changes colors correctly
- [ ] Streak counter increments properly
- [ ] Streak resets when gap >2 days
- [ ] Manual CrossFit entry works
- [ ] Lab entry works
- [ ] Calendar heatmap displays correctly
- [ ] Charts render with data
- [ ] CSV export creates 4 files
- [ ] Responsive design works on mobile

### Data Integrity Checks
- [ ] No duplicate activities (check by activity_id)
- [ ] Gap calculations are accurate
- [ ] Weekly summaries match raw data
- [ ] Targets are correctly evaluated

---

## 🚀 Deployment Options

### Option 1: Local Development (Current)
- Run on localhost
- Best for single user
- Zero cost
- Full control

### Option 2: Home Server (Future)
- Run on Raspberry Pi or NAS
- Access from any device on home network
- Still private, still local
- Requires: Static local IP, basic networking

### Option 3: Self-Hosted VPS (Future)
- Deploy to DigitalOcean, AWS, etc.
- Access from anywhere
- Requires: SSL cert, domain, authentication
- Cost: ~$5-10/month

**Recommendation**: Start with local, upgrade to home server if needed.

---

## 🎓 Key Learnings from Medicine 3.0

### Exercise Framework (Peter Attia)

1. **Zone 2 Training** (3-4 sessions/week, 45-60min each)
   - Builds mitochondrial density
   - Improves fat oxidation
   - Foundation of aerobic fitness
   - Target: Conversational pace, HR 120-140

2. **VO2 Max Training** (1 session/week, 25-50min)
   - Improves peak cardiovascular capacity
   - Strongest predictor of longevity
   - Target: 85-95% max HR
   - Format: 4-8 minute intervals

3. **Strength Training** (3 sessions/week)
   - Prevents sarcopenia (muscle loss)
   - Bone density (prevents osteoporosis)
   - Functional fitness (carry groceries at 90!)
   - Focus: Compound movements, progressive overload

4. **Stability** (daily)
   - Balance, proprioception
   - Prevents falls (leading cause of death in elderly)
   - Improves movement quality

### Key Biomarkers

1. **ApoB** (<60 mg/dL)
   - Best predictor of atherosclerotic disease
   - Better than LDL cholesterol

2. **HbA1c** (<5.2%)
   - Glucose control
   - Diabetes risk

3. **VO2 Max** (top 20% for age)
   - Single best predictor of all-cause mortality
   - Higher = longer healthspan

4. **Resting Heart Rate** (<60 bpm)
   - Cardiovascular fitness indicator
   - Lower = better

5. **HRV** (higher is better)
   - Autonomic nervous system health
   - Recovery indicator

### The Longevity Game Plan

**Goal**: Live to 100+ with quality of life
**Strategy**: Delay chronic disease onset by 10-20 years
**Method**: Optimize exercise, nutrition, sleep, emotional health

**This dashboard is your accountability system for the exercise pillar.**

---

## 📞 Support & Contribution

### Getting Help
- Check README.md troubleshooting section
- Review SETUP_CHECKLIST.md for step-by-step guide
- Verify .env configuration
- Check backend logs for errors

### Reporting Issues
- Describe the problem
- Include error messages
- Share your setup (OS, Python version, Node version)

### Contributing
This is a personal project, but if you want to adapt it:
- Fork the repository
- Customize for your needs
- Share your improvements!

---

**Built for Medicine 3.0 health optimization. Train smart, live long. 🏃‍♂️💪🧠**

Now go build that 65-year streak! 🔥
