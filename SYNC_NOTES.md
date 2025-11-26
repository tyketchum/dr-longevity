# Dr. Longevity Sync Scripts

## ✅ RECOMMENDED: dr_longevity_sync_improved.py

This is the **comprehensive sync script** that captures all available data from Garmin API.

### What it syncs:

**Daily Metrics:**
- ✅ Steps, floors climbed, intensity minutes
- ✅ Resting heart rate
- ✅ Sleep data (hours, score, deep/light/REM/awake breakdown)
- ✅ Stress score
- ✅ Body battery
- ✅ Weight (from body composition scale if available)
- ✅ HRV (Heart Rate Variability)
- ✅ Training Load
- ✅ Respiration rate
- ✅ SpO2 (blood oxygen saturation)

**Activities:**
- ✅ Basic metrics (duration, distance, calories)
- ✅ Heart rate (avg/max)
- ✅ HR Zone times (time in zones 1-5)
- ✅ Power data (avg/max/normalized for cycling)
- ✅ Cadence (avg/max)
- ✅ Pace (avg/max for running)
- ✅ Elevation gain/loss
- ✅ Training effects (aerobic/anaerobic)
- ✅ VO2 Max estimates

### Usage:

```bash
python3 dr_longevity_sync_improved.py
```

Syncs last 30 days by default. Change with environment variable:
```bash
SYNC_DAYS=60 python3 dr_longevity_sync_improved.py
```

### Recent Test Results (2025-11-25):

✅ **30/30 daily metrics synced**
✅ **6 activities synced** with power data

Data captured:
- Steps: 11-10,747 per day
- Resting HR: 60-80 bpm
- Power: 136-158W average (8 activities total)
- VO2 Max: 1 estimate (49 ml/kg/min)

---

## ⚠️ OLD: dr_longevity_sync.py

This is the **original basic sync script** with limited data capture.

### Limitations:
- ❌ Does NOT capture weight
- ❌ Does NOT capture HRV
- ❌ Does NOT capture training load
- ❌ Does NOT capture VO2 Max estimates
- ❌ Does NOT capture HR zone times
- ❌ Does NOT capture normalized power
- ❌ Does NOT capture training effects

**Do not use this script unless you specifically need the old behavior.**

---

## Database Schema Notes

### Integer Type Conversions Required:

The Supabase database has INTEGER type constraints on several fields. The improved sync script properly converts:

**Daily Metrics:**
- resting_hr, hrv, stress_score, body_battery, steps, floors_climbed, intensity_minutes, training_load, respiration_rate, spo2, sleep_score

**Activities:**
- avg_hr, max_hr, avg_power, max_power, normalized_power, avg_cadence, max_cadence, calories, elevation_gain, elevation_loss, aerobic_training_effect, anaerobic_training_effect

---

## Data Availability Notes

### What Data is Available:

Since workouts are synced Peloton → Strava → Garmin without biometric sensors:

✅ **Available:**
- Steps (from phone/watch)
- Resting HR (from phone/watch)
- Power data (from bike power meter)
- Activities (duration, distance, calories)

❌ **Not Available:**
- Weight (no body composition scale connected)
- HRV (no heart rate sensor during sleep)
- HR Zones (no heart rate monitor during rides)
- VO2 Max (limited - only 1 estimate found)
- Training Load (not calculated by Garmin)

---

## GitHub Actions Automation

To use the improved sync script in automated workflow:

1. Replace `dr_longevity_sync.py` with `dr_longevity_sync_improved.py` in `.github/workflows/sync.yml`
2. Ensure credentials are in GitHub Secrets:
   - GARMIN_EMAIL
   - GARMIN_PASSWORD
   - SUPABASE_URL
   - SUPABASE_KEY

---

## FTP and Performance Tracking

### Current FTP: 216W

Based on 8 power activities:
- Average power range: 136-158W (63-73% of FTP)
- All rides are Zone 2 endurance efforts
- Longest ride: 178 minutes @ 148W
- FTP sparklines now available (8 data points)

### W/kg Calculation:

- Weight: 79.4 kg (175 lbs)
- FTP: 216W
- **W/kg: 2.72** (Good rating)

---

## Troubleshooting

### "invalid input syntax for type integer" error:
✅ Fixed in improved script with proper integer conversions

### "int() argument must be a string..." error:
✅ Fixed with proper None handling using `or 0` pattern

### Duplicate key errors:
✅ Expected - upsert will update existing records

### Missing data (None values):
✅ Expected - Garmin API doesn't have all data for Strava-synced activities
