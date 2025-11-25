# Quick Reference Guide

## 🚀 Quick Commands

### Start App
```bash
./start.sh
```
Opens backend (port 8000) + frontend (port 3000)

### Manual Sync
```bash
# Sync yesterday's data
python3 backend/scripts/daily_sync.py

# Initial setup (90 days)
python3 backend/scripts/initial_setup.py
```

### Export Data
```bash
python3 backend/scripts/export_csv.py
```
Creates `backups/export_TIMESTAMP/` with 4 CSV files

### Start Individual Servers
```bash
# Backend only
python3 backend/main.py

# Frontend only
cd frontend && npm start
```

---

## 🎯 Target Summary (Your Personal Goals)

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Days Since Last Activity** | **<2 days** | **CRITICAL - maintains metabolic adaptations** |
| Resting HR | <60 bpm | Cardiovascular fitness indicator |
| Body Battery | >70 | Recovery readiness |
| Stress Score | <25 | Lower = better recovery |
| Zone 2 Sessions | 3-4/week | Mitochondrial health, fat oxidation |
| Strength Sessions | 3/week | Prevents sarcopenia, bone density |
| VO2 Max Intervals | 1/week | Peak cardiovascular capacity |
| Steps | >8,000/day | NEAT (non-exercise activity) |
| ApoB | <60 mg/dL | Atherosclerotic disease risk |
| HbA1c | <5.2% | Glucose control |
| Blood Pressure | <120/80 | Cardiovascular health |

---

## 📊 Activity Classification Logic

Activities are auto-classified based on heart rate and duration:

### Zone 2
- **Type**: Cycling or running
- **Duration**: >40 minutes
- **Avg HR**: 120-140 bpm (adjust in `.env`)
- **Purpose**: Build aerobic base, mitochondrial function

### VO2 Max
- **Type**: Cycling or running
- **Duration**: 25-50 minutes
- **Avg HR**: >170 bpm (adjust in `.env`)
- **Purpose**: Peak cardiovascular capacity

### Strength
- **Type**: CrossFit, weightlifting, strength training
- **Source**: Garmin or manual entry
- **Purpose**: Muscle mass, bone density, functional fitness

### Other
- **Type**: Walking, hiking, yoga, etc.
- **Counts toward**: Activity streak (prevents >2 day gaps)
- **Doesn't count toward**: Zone 2 or Strength targets

---

## 🗓️ Weekly Targets Breakdown

| Day | Ideal Activities | Notes |
|-----|------------------|-------|
| Mon | Zone 2 (60min) | Start week with aerobic base |
| Tue | Strength/CrossFit | Full body or upper focus |
| Wed | Zone 2 (45min) | Active recovery |
| Thu | Strength/CrossFit | Lower body or full body |
| Fri | VO2 Max (30min) | High intensity intervals |
| Sat | Strength/CrossFit | Full body |
| Sun | Zone 2 (60min) OR Active Recovery | Walking, light bike |

**Key Rule**: Never go more than 2 consecutive days without ANY activity!

---

## 🔍 App Pages Quick Guide

### Command Center (Home)
- **BIG ALERT**: Days since last activity (your accountability mechanism)
- **Streak Counter**: Current streak with milestone celebrations
- **Today's Metrics**: RHR, Body Battery, Stress, Sleep, Steps, Weight
- **Trend Charts**: 90-day trends for key wellness metrics
- **This Week**: Current week performance vs targets

### Activities
- **Log View**: Past 90 days with gap tracking
- **Add Workout**: Manual entry for CrossFit (if no PushPress API)
- **Gap Colors**: Green (<1.5d), Yellow (1.5-2d), Red (>2d)

### Weekly Log
- **12-Week Table**: All metrics with target achievement
- **Perfect Week**: Green highlight (all targets + no gaps >2d)
- **Missed Week**: Red highlight (>2 day gap occurred)

### Calendar
- **Heatmap**: Visual consistency tracker
- **Green Days**: Activity logged
- **Gray Days**: No activity (shame!)

### Labs & Strength
- **Lab Results**: ApoB, HbA1c, BP, VO2 max
- **Body Comp**: Body fat %, waist circumference
- **Strength Progress**: 1RM tracking (squat, deadlift, OHP)
- **Charts**: Visualize progress over time

---

## 🛠️ Common Tasks

### Add Manual CrossFit Workout
1. Go to **Activities** page
2. Click **+ Add CrossFit Workout**
3. Fill in: Date, Duration, Workout Name (optional), Notes
4. Click **Add Workout**
5. Gap tracking updates automatically

### Add Lab Results
1. Go to **Labs & Strength** page
2. Click **+ Add Entry**
3. Fill in relevant fields (leave others blank)
4. Choose entry type: Lab Results, Body Measurement, or Strength Test
5. Click **Add Entry**

### Check Your Status
Visit http://localhost:8000/status (JSON API response) or just look at Command Center alert!

### Sync New Data
```bash
python3 backend/scripts/daily_sync.py
```
Then refresh app in browser.

### Export Your Data
```bash
python3 backend/scripts/export_csv.py
```
Files saved to `backups/export_TIMESTAMP/`

---

## 🎨 Alert Color Codes

### Activity Gap Alert
- 🟢 **Green** (0-1 days): ✓ Active - Keep it up!
- 🟡 **Yellow** (1-2 days): ⚠ Rest day ending - Train today or tomorrow
- 🔴 **RED** (>2 days): 🚨 GET MOVING NOW - Streak at risk!

### Target Indicators
- 🟢 **Green**: Target achieved
- 🟡 **Yellow**: Close but not quite
- 🔴 **Red**: Missing target

---

## 📱 Mobile Usage

App is mobile-responsive! Access from phone:

1. Find your computer's local IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)
2. On phone browser: `http://YOUR_IP:3000`
3. Bookmark for easy access

Example: `http://192.168.1.100:3000`

---

## 🔐 Data Privacy

✅ All data stored locally in SQLite database
✅ No cloud services
✅ No third-party analytics
✅ You own 100% of your data
✅ Garmin tokens stored in `~/.garmin_tokens/`
✅ Export to CSV anytime

---

## 🚨 Streak Preservation Tips

**Your streak resets if you go >2 days without activity!**

Tips to maintain consistency:
1. Set a daily reminder at 6 PM: "Did you train today?"
2. Schedule workouts in advance (treat them like meetings)
3. Have backup "quick win" activities:
   - 20min walk/jog
   - 15min bodyweight circuit
   - 30min bike ride
4. Check app EVERY morning (accountability!)
5. Use yellow alert (day 1-2) as trigger to train TODAY
6. Never let red alert appear!

**Remember**: The goal isn't perfection, it's consistency over decades.

---

## 🎯 Medicine 3.0 Philosophy

This app is built on Peter Attia's Medicine 3.0 framework:

**Medicine 1.0**: Treat disease after it occurs
**Medicine 2.0**: Prevent disease with screenings
**Medicine 3.0**: Optimize healthspan and lifespan proactively

### Four Pillars:
1. **Exercise**: Zone 2 (aerobic base) + VO2 Max (peak capacity) + Strength (muscle/bone)
2. **Nutrition**: Not tracked here (use MyFitnessPal or Renaissance Diet)
3. **Sleep**: Tracked via Garmin (7-9h, good sleep score)
4. **Emotional Health**: Reflected in HRV/Stress scores

**Optimize for**:
- Living to 100+ with quality of life
- Delaying chronic disease onset by 10-20 years
- Maintaining physical capacity into your 90s

---

## 📚 Learn More

- [Peter Attia Podcast](https://peterattiamd.com/podcast/)
- [Zone 2 Training Deep Dive](https://peterattiamd.com/inigo-san-millan/)
- [VO2 Max and Longevity](https://peterattiamd.com/vo2max/)
- [Strength Training for Longevity](https://peterattiamd.com/strength-training/)

---

**Now go build that 65-year streak! 🏃‍♂️💪🧠**
