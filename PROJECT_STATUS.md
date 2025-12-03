# Dr. Longevity - Project Status
**Last Updated**: December 3, 2025

## 🌐 Live Deployment

- **Production URL**: https://dr-longevity.streamlit.app
- **Repository**: https://github.com/tyketchum/dr-longevity
- **Platform**: Streamlit Community Cloud
- **Database**: Supabase (PostgreSQL)

## ✅ Current Features

### Data Sync & Integration
- **Garmin Connect Integration**: Syncs activities, metrics, VO2 max, HRV, training load
- **Strava Integration**: Captures Peloton rides and power data not available from Garmin
- **Manual Sync Button**: Quick 7-day sync in the app
- **Supabase Cloud Database**: All data stored in cloud PostgreSQL

### Dashboard & KPIs
- **Activity Summary KPIs**:
  - Current Streak (consecutive workout days)
  - Days Since Last Workout (color-coded: green/yellow/red)
  - Weekly Avg Hours (with period-over-period comparison)
  - Weekly Avg Workouts (progress bar showing X/5 goal)
  - YTD # of Workouts

### Performance Metrics
- **Cycling Performance**:
  - FTP tracking with trend sparklines
  - Watts/kg calculation
  - Last 10 activities trend
  - Manual FTP override option

- **VO2 Max**:
  - Automatic tracking from Garmin
  - Age/gender-based ratings (Elite, Excellent, Good, Fair, Poor)
  - Trend visualization

### AI Training Recommendations
- **Powered by Claude AI (Anthropic)**
- Generates personalized training recommendations based on:
  - Current FTP and VO2 max
  - Recent training volume
  - Performance trends
- **Features**:
  - Collapsible expander view
  - Download as Markdown or Text
  - Recommendations persist after generation
  - Evidence-based coaching advice

### Activity Tracking
- **Monthly Summary**: Current vs previous month comparison
- **Recent Activities Table**: Last 10 workouts with details
- **Activity Types**: Cycling, running, strength, and more

### Data Visualization
- Charts and sparklines for trends
- Color-coded metrics for quick insights
- Interactive tables

## 🔧 Technical Architecture

### Frontend
- **Framework**: Streamlit
- **Main App**: `dr_longevity_app.py`
- **Design System**: Custom color palette, typography, spacing documented in code

### Backend & Data
- **Database**: Supabase (PostgreSQL)
- **Garmin Sync**: `dr_longevity_sync_improved.py`
- **Strava Sync**: `strava_sync.py`
- **Data Models**:
  - `activities` table: Workout details
  - `daily_summaries` table: Daily health metrics
  - `vo2max` table: VO2 max history
  - Additional tables for HRV, training load, etc.

### APIs & Integrations
- **Garmin Connect**: garminconnect library
- **Strava API**: OAuth2 with refresh tokens
- **Anthropic Claude API**: Claude Sonnet 4.5 for AI recommendations
- **Supabase**: Python client for database operations

### Configuration
- **Secrets Management**: `.streamlit/secrets.toml` (local) and Streamlit Cloud secrets
- **Environment Variables**: `.env` file for local development
- **Required Secrets**:
  - Supabase URL and API key
  - Garmin email and password
  - Strava client_id, client_secret, refresh_token
  - Anthropic API key

## 📝 Key Files

### Application Files
- `dr_longevity_app.py` - Main Streamlit application
- `dr_longevity_sync_improved.py` - Garmin data sync script
- `strava_sync.py` - Strava/Peloton data sync
- `test_strava_auth.py` - Strava authentication testing

### Configuration
- `requirements.txt` - Python dependencies
- `.streamlit/secrets.toml` - Local secrets (not in git)
- `.env` - Environment variables (not in git)
- `supabase_schema.sql` - Database schema

### Documentation
- `README_FIRST.md` - Initial setup guide
- `DEPLOY.md` - Deployment instructions
- `PROJECT_STATUS.md` - This file
- `SETUP_CHECKLIST.md` - Setup checklist

## 🎯 Recent Updates (This Session)

### Duplicate Activity Removal (December 3, 2025 - Evening)
- **Issue**: December 2, 2025 cycling workout appeared twice in dashboard
  - Generic "Cycling" activity from Garmin (ID: 21160832655)
  - "60 min Power Zone Endurance Ride with Christian Vande Velde" from Strava/Peloton
- **Resolution Process**:
  1. Deleted duplicate activity from Garmin Connect using `garmin.delete_activity()`
  2. Ran sync to update Supabase (`dr_longevity_sync_improved.py`)
  3. Manually deleted record from Supabase database (sync doesn't auto-remove deleted activities)
  4. Verified only Peloton class remains in database
- **Key Learning**: Sync scripts only add/update activities, they don't remove deleted activities from Supabase
- **Documentation**: Added duplicate removal procedures to SYNC_NOTES.md

### Data Sync Configuration Fix (December 3, 2025 - Earlier)
- **Fixed Duplicate Activities**: Resolved issue where Peloton rides appeared twice in dashboard
- **Sync Direction Configured**: Set Garmin ↔ Strava to one-way sync (Garmin → Strava only)
  - Garmin Connect → Strava: ✅ ON (Activities)
  - Strava → Garmin Connect: ❌ OFF (Training & Courses disabled)
- **Removed Duplicates**: Deleted 2 duplicate "Cycling" records that came from Strava → Garmin sync
- **Data Flow Now**:
  - Peloton → Strava (with full ride details) ✅
  - Garmin devices → Garmin Connect → Strava ✅
  - App pulls from both Garmin API and Strava API independently ✅
  - No more duplicates from bidirectional sync ✅

### Previous Session: AI Recommendations Enhancement (December 2, 2025)
- Fixed API key detection (supports multiple secret formats)
- Made recommendations collapsible with expander
- Moved download buttons to top of recommendations
- Used session state to persist recommendations after download
- Removed extra white space between sections
- Clean, professional interface with better error handling

## ⚠️ Known Issues & Notes

### Deployment
- **Reboot Required**: After pushing code changes, manually reboot the app at share.streamlit.io for changes to take effect properly
- Automatic redeployment works, but secrets and session state may not reload without manual reboot

### API Keys
- Anthropic API key must be in `[anthropic]` section with key name `api_key`
- Legacy top-level `ANTHROPIC_API_KEY` is supported as fallback
- Strava `client_id` must be integer (no quotes in TOML)

## 📊 Data Sources

### Garmin Connect
- Activities (cycling, running, strength, etc.)
- Daily summaries (resting HR, stress, body battery, steps)
- VO2 max estimates
- HRV data
- Training load/stress scores

### Strava
- Peloton bike activities (device-filtered)
- Power data (average, normalized, max watts)
- Heart rate data
- Cadence data
- Training load (suffer score)

## 🔐 Security

- All credentials stored in Streamlit Cloud secrets (encrypted)
- Local secrets files excluded from git (`.gitignore`)
- API keys never exposed in client-side code
- Supabase Row Level Security can be enabled for additional protection

## 🚀 Future Enhancements (Ideas)

- Automatic daily sync via GitHub Actions
- Training plan creation and tracking
- Goal setting and progress tracking
- Nutrition tracking integration
- Sleep data analysis
- Recovery recommendations
- Mobile-responsive improvements
- Multi-user support with authentication

## 📞 Support & Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Supabase Docs**: https://supabase.com/docs
- **Garmin Connect**: https://connect.garmin.com
- **Strava API**: https://developers.strava.com
- **Anthropic**: https://console.anthropic.com

## 🏁 Quick Start

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure secrets in `.streamlit/secrets.toml`
4. Run locally: `streamlit run dr_longevity_app.py`
5. Or deploy to Streamlit Cloud (see DEPLOY.md)

---

**Status**: ✅ Production-ready and fully deployed
**Maintainer**: Tyler Ketchum
**Last Session**: December 3, 2025 - Removed duplicate cycling activity from Dec 2, 2025 dashboard
