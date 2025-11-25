# Daily Automatic Garmin Sync Setup

## ✅ Automatic Daily Sync is Configured!

Your app will automatically sync new Garmin data **every day at 6:00 AM**.

## What Gets Synced?

- ✅ Yesterday's activities (rides, runs, CrossFit, etc.)
- ✅ Daily wellness metrics (sleep, resting HR, steps, stress)
- ✅ Activity gaps and streak calculations
- ✅ Weekly summary statistics

## How It Works

A macOS LaunchAgent (`com.longevity.dailysync.plist`) runs daily at 6 AM and calls your app's sync endpoint.

**Important**: Your app must be running for the sync to work!

### Option 1: Always-On App (Recommended)
Add the app to auto-start on login:
```bash
launchctl load ~/Library/LaunchAgents/com.longevity.app.plist
```

Now your app starts automatically when you log in, and syncs happen automatically every morning.

### Option 2: Manual Daily Start
Start the app each morning before the 6 AM sync:
```bash
./start_app.sh
```

## Manual Sync Anytime

Want to sync right now? Use the app's "Sync Garmin" button, or run:
```bash
./manual_sync.sh
```

## Change Sync Time

To sync at a different time (e.g., 8:00 AM):
1. Edit: `~/Library/LaunchAgents/com.longevity.dailysync.plist`
2. Change `<integer>6</integer>` to your preferred hour (0-23)
3. Reload: `launchctl unload ~/Library/LaunchAgents/com.longevity.dailysync.plist && launchctl load ~/Library/LaunchAgents/com.longevity.dailysync.plist`

## Check Sync Logs

View sync history:
```bash
# Last sync
tail ~/Claude/Garmin/logs/daily_sync.log

# Any errors
tail ~/Claude/Garmin/logs/daily_sync_error.log

# All syncs
cat ~/Claude/Garmin/logs/daily_sync.log
```

## Disable Auto-Sync

```bash
launchctl unload ~/Library/LaunchAgents/com.longevity.dailysync.plist
```

## Test the Sync Now

```bash
# Make sure app is running first
curl -X POST http://localhost:8000/sync/daily
```

## Troubleshooting

**Sync not happening?**
1. Check if app is running: `curl http://localhost:8000`
2. Check if LaunchAgent is loaded: `launchctl list | grep longevity`
3. Check logs: `tail ~/Claude/Garmin/logs/daily_sync_error.log`

**Re-sync historical data:**
```bash
curl -X POST "http://localhost:8000/sync/historical?days=90"
```

---

## Summary

✅ **Automatic sync**: Every day at 6:00 AM
✅ **Manual sync**: Click "Sync Garmin" button or run `./manual_sync.sh`
✅ **Logs**: `~/Claude/Garmin/logs/daily_sync.log`
✅ **Always-on app**: Auto-start on login (optional but recommended)

Your Garmin data will stay fresh automatically! 💪📊
