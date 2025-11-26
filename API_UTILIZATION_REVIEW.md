# API Utilization Review: Garmin & Strava

This document reviews what we're currently using from Garmin Connect and Strava APIs, and highlights opportunities for additional data capture.

---

## 🔴 Garmin Connect API

### Library: `garminconnect`
Python wrapper for Garmin Connect API

### Currently Using:

#### Daily Metrics (`get_stats(date)`)
✅ **Captured:**
- Steps, floors climbed, intensity minutes
- Resting HR, stress score, body battery
- Respiration rate, SpO2, sleep scores
- HRV (when available from compatible devices)
- Training load, VO2 Max estimates
- Weight (when logged)

#### Activities (`get_activities_by_date()`)
✅ **Captured:**
- Basic: date, duration, distance, type
- Heart Rate: avg/max HR, HR zones (5 zones)
- Power: avg/max/normalized power
- Cadence: avg/max cadence
- Elevation: gain/loss
- Calories burned
- Training Effects: aerobic/anaerobic
- VO2 Max estimates (per activity)

#### HR Zones (`get_activity_hr_in_timezones(activity_id)`)
✅ **Captured:**
- Seconds in each HR zone (1-5)
- Zone boundaries (bpm)
- More accurate than summary data

#### Detailed Activity (`get_activity(activity_id)`)
✅ **Captured:**
- Normalized power (for cycling)
- Enhanced metrics beyond summary
- Activity-specific data points

---

### 🔍 Available But NOT Currently Used:

#### 1. **GPS/Lap Data**
📍 **Endpoints:**
- `get_activity_splits(activity_id)` - Lap/split data
- `get_activity_split_summaries(activity_id)` - Split summaries

**Data Available:**
- Pace/speed per lap
- Power per lap (cycling)
- HR per lap
- Elevation per lap
- Could build interval analysis

**Priority:** Medium (useful for analyzing interval workouts)

#### 2. **Detailed Power Curve Data**
⚡ **Endpoints:**
- `get_activity_power_curve(activity_id)` - Complete power duration curve
- Shows best power for every duration (5s, 20s, 1min, 5min, 20min, etc.)

**Data Available:**
- Critical Power (CP)
- Functional Threshold Power (FTP)
- Anaerobic capacity (W')
- Best power for all durations

**Priority:** HIGH - Critical for accurate FTP tracking and power analysis
**Implementation:** Should replace current FTP estimation (avg power × 0.95)

**Recommendation:** Add this to sync script to track true FTP over time

#### 3. **Sleep Detailed Data**
😴 **Endpoints:**
- `get_sleep_data(date)` - Detailed sleep stages
- `get_spo2_data(date)` - SpO2 during sleep

**Data Available:**
- Sleep stages: deep, light, REM, awake
- Sleep score breakdown
- SpO2 levels during sleep
- Sleep HRV data

**Priority:** Medium (good for recovery tracking)

#### 4. **Stress & Body Battery Details**
💪 **Endpoints:**
- `get_all_day_stress(date)` - Stress levels throughout day
- `get_body_battery(date)` - Body battery history

**Data Available:**
- Hourly stress levels
- Body battery drain/recharge rates
- Rest periods vs activity periods

**Priority:** Low (daily summary is sufficient for most use cases)

#### 5. **Training Status & Load**
🎯 **Endpoints:**
- `get_training_status()` - Training status (peaking, maintaining, productive, etc.)
- `get_training_readiness()` - Readiness score

**Data Available:**
- Training status: Productive/Maintaining/Peaking/Overreaching/Unproductive/Detraining/Recovery
- Load ratio (acute vs chronic load)
- Recovery time needed

**Priority:** HIGH - Excellent for preventing overtraining
**Recommendation:** Add to daily metrics sync

#### 6. **Respiration & HRV Trends**
🫁 **Endpoints:**
- `get_respiration_data(date)` - Detailed breathing patterns
- `get_hrv_data(date)` - HRV measurements (when available)

**Data Available:**
- Breathing rate throughout day
- HRV baseline and trends
- Stress-related respiration changes

**Priority:** Medium (device-dependent - Forerunner 935 may not provide)

#### 7. **Activity Weather**
🌤️ **Endpoints:**
- `get_activity_weather(activity_id)` - Weather during activity

**Data Available:**
- Temperature, humidity, wind
- Weather conditions
- Could correlate performance with weather

**Priority:** Low (interesting but not critical)

---

## 🟠 Strava API

### Currently Using:

#### Activities (`/api/v3/athlete/activities`)
✅ **Captured:**
- Basic activity data
- Power metrics (avg, weighted avg, max)
- Heart rate (avg/max)
- Cadence (avg/max)
- Elevation gain
- Kilojoules (total work)
- **Device filtering:** "Peloton Bike" only

#### Detailed Activity (`/api/v3/activities/{id}`)
✅ **Captured:**
- Enhanced power data
- Gear/equipment info
- Activity description (includes leaderboard rank for Peloton)

---

### 🔍 Available But NOT Currently Used:

#### 1. **Segments & KOMs**
🏆 **Endpoints:**
- `/api/v3/activities/{id}/segments` - Segment efforts
- `/api/v3/segments/{id}` - Segment details

**Data Available:**
- Personal records on segments
- KOM/QOM standings
- Segment leaderboards
- Compare efforts over time

**Priority:** Medium (for outdoor cycling routes)
**Note:** Not applicable to Peloton rides

#### 2. **Detailed Streams (Time-Series Data)**
📊 **Endpoints:**
- `/api/v3/activities/{id}/streams` - Raw data streams

**Data Available:**
- Second-by-second power
- Second-by-second HR
- Second-by-second cadence
- GPS coordinates (outdoor activities)
- Altitude, velocity, temperature

**Priority:** HIGH for advanced analysis
**Use Cases:**
- Power distribution analysis
- Identify coasting/freewheeling
- Analyze power spikes and variability
- Build custom training metrics

**Recommendation:** Capture for Peloton rides to analyze power consistency

#### 3. **Athlete Stats**
📈 **Endpoints:**
- `/api/v3/athletes/{id}/stats` - Athlete totals

**Data Available:**
- All-time totals (distance, time, elevation)
- Recent totals (last 4 weeks, YTD)
- Biggest ride/run
- Activity counts

**Priority:** Low (we calculate this from activities)

#### 4. **Kudos & Comments**
💬 **Endpoints:**
- `/api/v3/activities/{id}/kudos` - Activity kudos
- `/api/v3/activities/{id}/comments` - Activity comments

**Data Available:**
- Social interactions
- Motivation/engagement metrics

**Priority:** Very Low (not relevant for personal dashboard)

#### 5. **Training Zones**
🎯 **Endpoints:**
- `/api/v3/athlete/zones` - Athlete's training zones

**Data Available:**
- HR zones (custom or calculated)
- Power zones (based on FTP)
- Pace zones

**Priority:** Medium (could auto-update zones)
**Current State:** We calculate zones based on FTP/max HR

---

## 🎯 Recommended Additions

### High Priority:

1. **Garmin Power Curve Data** ⚡
   - Replace FTP estimation with true power curve
   - Track Critical Power (CP) and W'
   - More accurate than avg power × 0.95
   ```python
   power_curve = garmin.get_activity_power_curve(activity_id)
   ftp = power_curve['cp']  # or power_curve['20_min_power'] * 0.95
   ```

2. **Garmin Training Status** 🎯
   - Prevent overtraining
   - Track productive/peaking/recovery status
   - Load ratio (acute/chronic)
   ```python
   training_status = garmin.get_training_status()
   readiness = garmin.get_training_readiness()
   ```

3. **Strava Power Streams** 📊
   - Second-by-second power data for Peloton rides
   - Analyze power consistency/variability
   - Identify intervals and rest periods
   ```python
   streams = strava.get_activity_streams(activity_id, keys='watts,heartrate,cadence')
   power_data = streams['watts']['data']
   ```

### Medium Priority:

4. **Garmin Sleep Details** 😴
   - Sleep stages (deep, light, REM)
   - Better recovery tracking
   ```python
   sleep_data = garmin.get_sleep_data(date)
   ```

5. **Garmin Lap/Split Data** 📍
   - Interval workout analysis
   - Track performance per lap
   ```python
   splits = garmin.get_activity_splits(activity_id)
   ```

### Low Priority:

6. **Stress & Body Battery Details**
7. **Activity Weather Data**

---

## 🏗️ Implementation Plan

### Phase 1: Critical Power & Training Status (Week 1)
- [ ] Add `get_activity_power_curve()` to Garmin sync
- [ ] Store FTP, CP, W' in database
- [ ] Add `get_training_status()` and `get_training_readiness()`
- [ ] Display training status in dashboard
- [ ] Update FTP calculation to use true power curve

### Phase 2: Advanced Power Analysis (Week 2)
- [ ] Add Strava power streams for Peloton rides
- [ ] Calculate power variability metrics (VI, NP)
- [ ] Identify intervals automatically
- [ ] Build power distribution charts

### Phase 3: Recovery Tracking (Week 3)
- [ ] Add detailed sleep data
- [ ] Sleep stage tracking
- [ ] SpO2 during sleep
- [ ] Recovery recommendations based on sleep + training load

### Phase 4: Interval Analysis (Future)
- [ ] Lap/split data capture
- [ ] Interval detection and analysis
- [ ] Workout structure visualization

---

## 📊 Database Schema Updates Needed

### New Tables:

**`power_curve`**
```sql
- activity_id (FK)
- duration_seconds
- max_power
- Used to store: 5s, 20s, 1min, 5min, 20min, 60min power
```

**`training_status`**
```sql
- date
- status (productive/maintaining/peaking/etc)
- load_ratio
- acute_load
- chronic_load
- recovery_time_hours
```

**`sleep_stages`**
```sql
- date
- deep_minutes
- light_minutes
- rem_minutes
- awake_minutes
- sleep_score
- spo2_avg
```

**`activity_streams`** (optional, large data)
```sql
- activity_id
- timestamp
- power
- heart_rate
- cadence
- Only for detailed analysis, not displayed in UI
```

---

## 🚫 What We're Intentionally NOT Using

### Garmin:
- **Social features** (challenges, badges) - Not relevant
- **Golf/swim data** - Different sports
- **Menstrual cycle tracking** - Not applicable
- **Hydration tracking** - Not consistently logged

### Strava:
- **Social features** (kudos, comments, clubs) - Not for personal dashboard
- **Route planning** - Not using Strava for planning
- **Segments** (for now) - Limited outdoor cycling
- **Photos** - Not needed for metrics dashboard

---

## 🔄 Data Sync Strategy

### Current Architecture:
```
Garmin Connect (primary) → Supabase
Strava (Peloton only) → Supabase
```

### Why This Works:
- **Garmin**: Garmin Edge 1040 Solar & Forerunner 935 data
  - Direct device sync to Garmin Connect
  - Most complete data (GPS, HR zones, power, etc.)

- **Strava**: Peloton Bike data only
  - Peloton → Strava → Supabase
  - Filtered by `device_name == "Peloton Bike"`
  - Prevents duplicate outdoor cycling activities

### Avoids Duplicates:
- Outdoor rides: Garmin only (Edge 1040 Solar)
- Indoor rides: Strava only (Peloton Bike)
- Watches: Garmin only (Forerunner 935)

---

## 📝 Summary

### What We're Using Well:
✅ Daily wellness metrics (HRV, stress, sleep score, body battery)
✅ Activity basics (duration, distance, HR, zones)
✅ Power metrics (avg, max, normalized)
✅ Device-specific filtering (Peloton vs Garmin)

### Quick Wins:
🎯 **Add Power Curve** - More accurate FTP
🎯 **Add Training Status** - Prevent overtraining
📊 **Add Power Streams** - Detailed Peloton analysis

### Future Enhancements:
😴 Sleep stage tracking
📍 Interval/lap analysis
🌤️ Weather correlations

---

**Status**: Ready for Phase 1 implementation (Power Curve & Training Status)
