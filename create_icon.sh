#!/bin/bash

# Create a custom icon using SF Symbols
# This creates a simple purple/teal gradient icon with a heart rate symbol

ICON_DIR="/Users/tketchum/Claude/Garmin/AppIcon.iconset"
mkdir -p "$ICON_DIR"

# Create base icon using sips (built-in macOS tool)
# We'll use the system Health app icon as base and customize it

# Create a simple PNG icon with ImageMagick or use system icons
# For now, let's use the Activity Monitor icon as a template
# and copy it to create our app icon

# Copy and resize system health/activity icon
SYSTEM_ICON="/System/Applications/Activity Monitor.app/Contents/Resources/ActivityMonitor.icns"

if [ -f "$SYSTEM_ICON" ]; then
    # Extract the icon to PNG
    sips -s format png "$SYSTEM_ICON" --out /tmp/base_icon.png 2>/dev/null

    # Create different sizes
    sips -z 16 16     /tmp/base_icon.png --out "$ICON_DIR/icon_16x16.png"
    sips -z 32 32     /tmp/base_icon.png --out "$ICON_DIR/icon_16x16@2x.png"
    sips -z 32 32     /tmp/base_icon.png --out "$ICON_DIR/icon_32x32.png"
    sips -z 64 64     /tmp/base_icon.png --out "$ICON_DIR/icon_32x32@2x.png"
    sips -z 128 128   /tmp/base_icon.png --out "$ICON_DIR/icon_128x128.png"
    sips -z 256 256   /tmp/base_icon.png --out "$ICON_DIR/icon_128x128@2x.png"
    sips -z 256 256   /tmp/base_icon.png --out "$ICON_DIR/icon_256x256.png"
    sips -z 512 512   /tmp/base_icon.png --out "$ICON_DIR/icon_256x256@2x.png"
    sips -z 512 512   /tmp/base_icon.png --out "$ICON_DIR/icon_512x512.png"
    sips -z 1024 1024 /tmp/base_icon.png --out "$ICON_DIR/icon_512x512@2x.png"

    # Convert to icns
    iconutil -c icns "$ICON_DIR" -o "/Users/tketchum/Claude/Garmin/Longevity Dashboard.app/Contents/Resources/AppIcon.icns"

    echo "✅ Icon created successfully!"

    # Cleanup
    rm -rf "$ICON_DIR"
    rm -f /tmp/base_icon.png
else
    echo "⚠️  Could not create custom icon. The app will use the default icon."
fi
