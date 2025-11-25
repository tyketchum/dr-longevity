# Cloud Database Implementation Plan
**Goal**: Fully automated Garmin data sync with cloud-hosted database

## Why Move to Cloud Database?

**Current Setup (Option C)**:
- ✅ Works locally with sync button
- ❌ Requires manual button click
- ❌ Database lives in GitHub (not ideal for frequent updates)
- ❌ Commits database file on every sync (bloats git history)

**Cloud Setup (Option B)**:
- ✅ Fully automatic syncing
- ✅ No manual intervention needed
- ✅ Database updates instantly reflect on dashboard
- ✅ Clean git history (no database file)
- ✅ Can schedule syncs (every hour, twice daily, etc.)

---

## Free Cloud Database Options

### Option 1: Supabase (RECOMMENDED)
**Why**: Best free tier, PostgreSQL-based, easy to use
- **Free tier**: 500 MB database, unlimited API requests
- **Setup time**: ~15 minutes
- **Pros**:
  - PostgreSQL (robust, SQL-based)
  - Built-in authentication & security
  - Excellent Python library
  - Can run scheduled functions
- **Cons**: Need to learn basic Supabase setup

**Sign up**: https://supabase.com

### Option 2: PlanetScale
**Why**: Generous free tier, MySQL-based
- **Free tier**: 5 GB storage, 1 billion reads/month
- **Setup time**: ~20 minutes
- **Pros**: Very generous limits
- **Cons**: MySQL (slightly different from SQLite syntax)

**Sign up**: https://planetscale.com

### Option 3: Neon
**Why**: PostgreSQL serverless, scales to zero
- **Free tier**: 0.5 GB storage
- **Setup time**: ~15 minutes
- **Pros**: True PostgreSQL, auto-scaling
- **Cons**: Smaller storage limit

**Sign up**: https://neon.tech

---

## Implementation Steps

### Phase 1: Set Up Cloud Database (30 mins)

1. **Sign up for Supabase** (recommended)
   - Go to https://supabase.com
   - Click "Start your project"
   - Create new organization & project
   - Note down: Database URL, API keys

2. **Create Database Tables**
   - Use Supabase SQL Editor
   - Copy schema from current SQLite database
   - Tables needed:
     - `activities`
     - `daily_metrics`
     - Any other tables from current DB

3. **Test Connection**
   - Install Python library: `pip install supabase`
   - Test connection with simple query
   - Verify you can read/write data

### Phase 2: Update garmin_sync.py (20 mins)

1. **Add Supabase connection**
   ```python
   from supabase import create_client, Client

   SUPABASE_URL = os.getenv('SUPABASE_URL')
   SUPABASE_KEY = os.getenv('SUPABASE_KEY')
   supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
   ```

2. **Replace SQLite queries with Supabase**
   - Change `cursor.execute()` to `supabase.table().insert()`
   - Update all database operations
   - Keep same data structure

3. **Add environment variables**
   - Update `.env` file
   - Add to Streamlit Cloud secrets
   - Add to GitHub Actions secrets (for automation)

### Phase 3: Update streamlit_dashboard.py (15 mins)

1. **Connect to Supabase instead of SQLite**
   ```python
   @st.cache_resource
   def get_database_connection():
       return create_client(
           st.secrets["supabase"]["url"],
           st.secrets["supabase"]["key"]
       )
   ```

2. **Update all queries**
   - Replace SQL queries with Supabase API calls
   - Example:
     ```python
     # Old
     df = pd.read_sql_query(query, conn)

     # New
     response = supabase.table('activities').select('*').execute()
     df = pd.DataFrame(response.data)
     ```

3. **Test dashboard locally**
   - Run streamlit locally
   - Verify all data loads correctly
   - Check all visualizations work

### Phase 4: Automate Syncing (30 mins)

**Option A: GitHub Actions (Recommended)**
1. Create `.github/workflows/sync_garmin.yml`
2. Schedule to run twice daily
3. Runs `garmin_sync.py` which writes to Supabase
4. No commits needed - data goes straight to cloud DB

```yaml
name: Sync Garmin Data
on:
  schedule:
    - cron: '0 6,18 * * *'  # 6 AM & 6 PM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python3 garmin_sync.py
        env:
          GARMIN_EMAIL: ${{ secrets.GARMIN_EMAIL }}
          GARMIN_PASSWORD: ${{ secrets.GARMIN_PASSWORD }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

**Option B: Supabase Edge Functions**
- More advanced
- Runs directly in Supabase
- Requires learning Deno/TypeScript

### Phase 5: Deploy & Test (15 mins)

1. **Update Streamlit Cloud secrets**
   - Add SUPABASE_URL
   - Add SUPABASE_KEY
   - Remove local database file from git

2. **Push changes to GitHub**
   - Dashboard automatically redeploys
   - Verify dashboard loads
   - Check all data displays correctly

3. **Trigger first automated sync**
   - Run GitHub Action manually
   - Verify data appears in Supabase
   - Verify dashboard updates

4. **Remove database file from git**
   ```bash
   git rm longevity_dashboard.db
   git commit -m "Remove local database, now using Supabase"
   ```

---

## Migration Checklist

- [ ] Sign up for Supabase
- [ ] Create project & note credentials
- [ ] Create database tables (match current schema)
- [ ] Test connection with Python
- [ ] Update `garmin_sync.py` to use Supabase
- [ ] Update `streamlit_dashboard.py` to use Supabase
- [ ] Test dashboard locally
- [ ] Add secrets to Streamlit Cloud
- [ ] Create GitHub Actions workflow
- [ ] Add secrets to GitHub Actions
- [ ] Deploy to Streamlit Cloud
- [ ] Test automated sync
- [ ] Remove local database from git
- [ ] Verify everything works end-to-end

---

## Rollback Plan

If something goes wrong:
1. Keep current `streamlit_dashboard.py` as `streamlit_dashboard_sqlite.py`
2. Keep `longevity_dashboard.db` locally as backup
3. Can revert to SQLite version anytime
4. Supabase has automatic backups (daily on free tier)

---

## Expected Timeline

- **Setup Supabase**: 30 minutes
- **Update Python scripts**: 35 minutes
- **Test & deploy**: 15 minutes
- **Create automation**: 30 minutes

**Total**: ~2 hours

---

## Key Benefits After Migration

1. **True automation**: Data syncs twice daily without any action
2. **Instant updates**: Dashboard always shows latest data
3. **Clean git history**: No more database commits
4. **Scalable**: Can add more features easily
5. **Professional**: Production-ready architecture

---

## Questions to Consider

1. **Sync frequency**: How often do you want data to sync?
   - Twice daily (recommended for workouts)
   - Hourly (if you want very fresh data)
   - Once daily (minimal API usage)

2. **Data retention**: How much history to keep?
   - Current: 30-90 days
   - Supabase free: Can store years of data (500 MB is plenty)

3. **Privacy**: Who can access your dashboard?
   - Public URL (anyone with link)
   - Password protected (Streamlit feature)
   - Fully private (VPN or local only)

---

## Resources

- Supabase Docs: https://supabase.com/docs
- Supabase Python Client: https://supabase.com/docs/reference/python
- PostgreSQL to SQLite migration: https://supabase.com/docs/guides/database
- GitHub Actions docs: https://docs.github.com/actions

---

## Next Steps for Tomorrow

1. Review this plan
2. Sign up for Supabase account
3. Follow Phase 1 to set up cloud database
4. We'll implement together step-by-step
