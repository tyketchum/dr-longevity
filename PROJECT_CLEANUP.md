# Project Cleanup & Organization

## 📁 Current File Count: 42 files

This document identifies files to keep, consolidate, or remove to maintain a clean, understandable project structure.

---

## ✅ Core Application Files (Keep)

### Main Application
- `dr_longevity_app.py` (49K) - **PRIMARY** - Streamlit dashboard
- `requirements.txt` (122B) - Python dependencies

### Data Sync Scripts
- `dr_longevity_sync_improved.py` (18K) - **PRIMARY** - Enhanced Garmin sync
- `strava_sync.py` (9.3K) - **PRIMARY** - Strava integration (Peloton only)
- `strava_auth.py` (7.1K) - OAuth helper for Strava setup

### Database
- `supabase_schema.sql` (7.3K) - Database schema definition
- `.env` - Credentials (not in git)

---

## 🗑️ Files to DELETE (Outdated/Redundant)

### 1. **Deprecated Sync Scripts**
- ❌ `dr_longevity_sync.py` (8.9K) - **OLD VERSION** - Replaced by `_improved.py`
  - Missing power curve data
  - Less accurate HR zones
  - Only syncs 30 days

### 2. **Backup Files**
- ❌ `dr_longevity_app_backup.py` (24K) - **BACKUP** - Not needed (use git history)

### 3. **Migration Scripts** (One-time use, completed)
- ❌ `migrate_sqlite_to_supabase.py` (4.2K) - Migration complete
- ❌ `longevity_dashboard.db` (96K) - **SQLite DB** - Migrated to Supabase

### 4. **Old Shell Scripts**
- ❌ `start.sh` (1.3K) - Redundant with `start_dashboard.sh`
- ❌ `manual_sync.sh` (417B) - Use sync scripts directly

### 5. **Failed/Empty Outputs**
- ❌ `cycling_routes.json` (2B) - Empty (no GPS data available)

### 6. **Log Files** (Optional cleanup)
- ⚠️ `sync_progress.log` (337K) - **LARGE** - Archive or delete
- ⚠️ `sync_full_history.log` (16K) - Archive or delete
- ⚠️ `resync.log` (1.7K) - Archive or delete
- ⚠️ `dashboard.log` (319B) - Delete
- ⚠️ `dashboard.error.log` (296B) - Delete

### 7. **Requirements Files**
- ❌ `requirements_streamlit.txt` (58B) - Consolidate into main `requirements.txt`

---

## 📚 Documentation Files (Consolidate)

### Keep As-Is:
- ✅ `README.md` (10K) - Main project README
- ✅ `API_UTILIZATION_REVIEW.md` (11K) - **NEW** - Comprehensive API reference
- ✅ `STRAVA_SETUP.md` (4.4K) - Strava integration guide

### Consolidate Into Single Docs:

#### Create: **`SETUP_GUIDE.md`** (Merge these)
- `README_FIRST.md` (3.2K)
- `SETUP_CHECKLIST.md` (5.6K)
- `SUPABASE_SETUP_INSTRUCTIONS.md` (5.8K)
- `DAILY_SYNC_SETUP.md` (2.4K)
- `LAUNCH_INSTRUCTIONS.md` (1.6K)
- `ADD_TO_DOCK.md` (1.5K)

**Result:** One comprehensive setup guide instead of 6 fragmentedfiles

#### Create: **`REFERENCE.md`** (Merge these)
- `QUICK_REFERENCE.md` (6.9K)
- `SYNC_NOTES.md` (3.9K)
- `IMPROVEMENTS_SUMMARY.md` (6.6K)

**Result:** Single reference doc for daily use

#### Keep Separate:
- ✅ `PROJECT_OVERVIEW.md` (17K) - High-level architecture
- ✅ `DEPLOY.md` (2.2K) - Deployment instructions
- ✅ `CLOUD_DATABASE_PLAN.md` (7.1K) - Database design rationale

---

## 🎯 Utility Scripts (Keep)

- ✅ `check_activity.py` (792B) - Database query helper
- ✅ `fetch_gps_routes.py` (4.2K) - GPS route fetcher (for future outdoor rides)
- ✅ `create_app_icon.py` (2.6K) - Icon generator for macOS app
- ✅ `create_icon.sh` (1.9K) - Shell script for icon creation
- ✅ `start_dashboard.sh` (979B) - Dashboard launcher
- ✅ `stop_dashboard.sh` (575B) - Dashboard stopper

---

## 📋 Cleanup Commands

```bash
# 1. Delete outdated sync scripts
rm dr_longevity_sync.py dr_longevity_app_backup.py

# 2. Delete migration files (completed)
rm migrate_sqlite_to_supabase.py longevity_dashboard.db

# 3. Delete redundant shell scripts
rm start.sh manual_sync.sh

# 4. Delete empty/failed outputs
rm cycling_routes.json

# 5. Archive log files
mkdir -p .archive
mv sync_progress.log sync_full_history.log resync.log dashboard.log dashboard.error.log .archive/

# 6. Delete redundant requirements file
rm requirements_streamlit.txt

# 7. Add .archive to .gitignore
echo ".archive/" >> .gitignore
```

---

## 📝 Documentation Consolidation

### Create `SETUP_GUIDE.md`:

```markdown
# Dr. Longevity Setup Guide

## Table of Contents
1. Prerequisites
2. Environment Setup
3. Supabase Configuration
4. Garmin Connect Setup
5. Strava Integration (Optional - Peloton only)
6. Daily Sync Automation
7. Launch Instructions
8. Add to macOS Dock

[Consolidate content from 6 setup docs]
```

### Create `REFERENCE.md`:

```markdown
# Dr. Longevity Reference

## Daily Operations
- Running manual syncs
- Checking sync status
- Viewing logs

## Sync Scripts
- Garmin sync (dr_longevity_sync_improved.py)
- Strava sync (strava_sync.py)
- Recent improvements

## Troubleshooting
[Quick reference content]
```

---

## 🗂️ Final Project Structure

```
dr-longevity/
├── 📱 APPLICATION
│   ├── dr_longevity_app.py          # Main Streamlit app
│   └── requirements.txt              # Dependencies
│
├── 🔄 SYNC SCRIPTS
│   ├── dr_longevity_sync_improved.py # Garmin sync (primary)
│   ├── strava_sync.py                # Strava sync (Peloton only)
│   └── strava_auth.py                # Strava OAuth setup
│
├── 🗄️ DATABASE
│   ├── supabase_schema.sql           # Database schema
│   └── .env                          # Credentials (not in git)
│
├── 🛠️ UTILITIES
│   ├── check_activity.py             # Database query helper
│   ├── fetch_gps_routes.py           # GPS route fetcher
│   ├── start_dashboard.sh            # Dashboard launcher
│   ├── stop_dashboard.sh             # Dashboard stopper
│   ├── create_app_icon.py            # macOS icon generator
│   └── create_icon.sh                # Icon creation script
│
├── 📚 DOCUMENTATION
│   ├── README.md                     # Main project README
│   ├── SETUP_GUIDE.md                # Comprehensive setup (NEW)
│   ├── REFERENCE.md                  # Daily reference (NEW)
│   ├── API_UTILIZATION_REVIEW.md     # API deep dive
│   ├── STRAVA_SETUP.md               # Strava integration guide
│   ├── PROJECT_OVERVIEW.md           # Architecture overview
│   ├── DEPLOY.md                     # Deployment guide
│   └── CLOUD_DATABASE_PLAN.md        # Database design rationale
│
└── 📜 META
    ├── LICENSE
    └── .gitignore
```

**Result:**
- **Before:** 42 files, 25 docs
- **After:** ~25 files, 9 consolidated docs
- **Removed:** 17 redundant/outdated files

---

## 🎯 Benefits of Cleanup

1. **Easier Onboarding**
   - One setup guide instead of 6
   - Clear file organization
   - No confusion about which files to use

2. **Maintainability**
   - Only one sync script to maintain (not 2)
   - Documentation stays in sync
   - Less technical debt

3. **Repository Size**
   - Remove 337K log file
   - Remove 96K SQLite database
   - Cleaner git history

4. **Clarity**
   - `_improved.py` clearly marks the better version
   - Scripts grouped by purpose
   - Docs grouped by use case

---

## ✅ Action Items

### Immediate (Do Now):
- [ ] Delete deprecated sync script (`dr_longevity_sync.py`)
- [ ] Delete backup app (`dr_longevity_app_backup.py`)
- [ ] Delete SQLite database (migrated)
- [ ] Archive log files to `.archive/`

### Soon (This Week):
- [ ] Consolidate setup docs into `SETUP_GUIDE.md`
- [ ] Consolidate reference docs into `REFERENCE.md`
- [ ] Update README.md with new structure
- [ ] Test all remaining scripts still work

### Optional (Future):
- [ ] Add automated log rotation
- [ ] Create backup/restore scripts
- [ ] Add CI/CD testing

---

## 🚫 DO NOT Delete

These look redundant but serve specific purposes:

- `PROJECT_OVERVIEW.md` - High-level architecture (different from README)
- `DEPLOY.md` - Streamlit Cloud deployment (different from setup)
- `CLOUD_DATABASE_PLAN.md` - Database design decisions (historical context)
- `fetch_gps_routes.py` - Needed when doing outdoor rides in future
- `create_app_icon.py` - Needed if recreating macOS app

---

**Status**: Ready for cleanup. Start with "Immediate" items, then consolidate docs.
