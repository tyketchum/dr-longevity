# Longevity App - Launch Instructions

## Quick Start (Manual Launch)

### Option 1: Simple Double-Click
1. Navigate to `/Users/tketchum/Claude/Garmin/`
2. Double-click `start_app.sh`
3. App will open in your browser automatically

### Option 2: From Terminal
```bash
cd /Users/tketchum/Claude/Garmin
./start_app.sh
```

The app will:
- Start the backend API on port 8000
- Start the frontend on port 3000
- Automatically open http://localhost:3000 in your browser

## Auto-Start on Login (Recommended)

To have the app automatically start every time you log in to your Mac:

```bash
# Load the launch agent
launchctl load ~/Library/LaunchAgents/com.longevity.app.plist
```

To disable auto-start:
```bash
launchctl unload ~/Library/LaunchAgents/com.longevity.app.plist
```

## Quick Launch with Spotlight

For fastest access:
1. Press `⌘ + Space` (Spotlight)
2. Type "start_app.sh"
3. Press Enter

## Create a Desktop Shortcut

1. Right-click on `start_app.sh`
2. Select "Make Alias"
3. Drag the alias to your Desktop
4. Rename it to "Longevity App"

Now you can double-click the desktop icon to launch!

## Stopping the App

Press `Ctrl + C` in the terminal where it's running, or:
```bash
# Kill backend
pkill -f "python3 backend/main.py"

# Kill frontend (if needed)
pkill -f "npm start"
```

## Accessing the App

Once running:
- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)

## Troubleshooting

If the app doesn't start:
1. Check that ports 3000 and 8000 are not in use
2. Make sure Python 3 and npm are installed
3. Check logs at:
   - `~/Claude/Garmin/app.log`
   - `~/Claude/Garmin/app.error.log`
