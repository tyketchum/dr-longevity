# Add Longevity Dashboard to Your Dock

## Your Custom App is Ready! 🎉

I've created a macOS app bundle called **"Longevity Dashboard.app"** with a custom purple-to-teal gradient icon featuring a heart rate pulse line.

## Add to Dock (Easy!)

### Method 1: Drag and Drop
1. Open Finder
2. Navigate to: `/Users/tketchum/Claude/Garmin/`
3. Find **"Longevity Dashboard.app"**
4. **Drag it to your Dock** (anywhere you like)
5. Done! 🎉

### Method 2: Right-Click in Dock
1. Double-click "Longevity Dashboard.app" to launch it
2. Once it appears in the Dock (while running)
3. Right-click the Dock icon
4. Options → Keep in Dock
5. Done! 🎉

## Usage

**Click the Dock icon** → Dashboard opens automatically in your browser!

The icon shows a purple-to-teal gradient (matching your InterWorks theme) with a heart rate pulse line.

## What Happens When You Click It?

1. ✅ Backend API starts (port 8000)
2. ✅ Frontend starts (port 3000)
3. ✅ Browser opens to http://localhost:3000
4. ✅ Dashboard loads with your activity data

## Customize the Icon (Optional)

If you want a different icon:
1. Find an image you like (PNG, JPEG, etc.)
2. Right-click "Longevity Dashboard.app" → Get Info
3. Drag your image onto the small icon in the top-left of the Info window
4. The icon will update!

## Remove from Dock

Right-click the icon → Options → Remove from Dock

---

**Note**: The app runs in the background. To fully quit, use Activity Monitor to stop the Python and npm processes, or run:
```bash
pkill -f "python3 backend/main.py"
pkill -f "npm start"
```
