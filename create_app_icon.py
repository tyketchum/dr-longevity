#!/usr/bin/env python3
"""
Create a custom app icon for Longevity Dashboard
Uses PIL to create a gradient icon with health symbols
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    def create_icon(size):
        """Create a gradient icon with pulse/heart symbol"""
        # Create image with purple to teal gradient
        img = Image.new('RGB', (size, size))
        draw = ImageDraw.Draw(img)

        # Draw gradient background (purple to teal)
        for y in range(size):
            # Interpolate between purple (#6633ff) and teal (#17e5c7)
            r = int(102 + (23 - 102) * y / size)
            g = int(51 + (229 - 51) * y / size)
            b = int(255 + (199 - 255) * y / size)
            draw.line([(0, y), (size, y)], fill=(r, g, b))

        # Draw a heart rate / pulse line in white
        points = []
        center_y = size // 2
        amplitude = size // 6

        for x in range(size):
            # Create ECG-like waveform
            if x < size * 0.2:
                y = center_y
            elif x < size * 0.3:
                y = center_y - amplitude * 2
            elif x < size * 0.35:
                y = center_y + amplitude
            elif x < size * 0.4:
                y = center_y
            elif x < size * 0.6:
                y = center_y
            elif x < size * 0.7:
                y = center_y - amplitude * 2
            elif x < size * 0.75:
                y = center_y + amplitude
            else:
                y = center_y

            points.append((x, int(y)))

        # Draw the pulse line
        draw.line(points, fill='white', width=max(2, size // 64))

        return img

    # Create iconset directory
    iconset_dir = "/Users/tketchum/Claude/Garmin/AppIcon.iconset"
    os.makedirs(iconset_dir, exist_ok=True)

    # Generate all required icon sizes
    sizes = [
        (16, 'icon_16x16.png'),
        (32, 'icon_16x16@2x.png'),
        (32, 'icon_32x32.png'),
        (64, 'icon_32x32@2x.png'),
        (128, 'icon_128x128.png'),
        (256, 'icon_128x128@2x.png'),
        (256, 'icon_256x256.png'),
        (512, 'icon_256x256@2x.png'),
        (512, 'icon_512x512.png'),
        (1024, 'icon_512x512@2x.png'),
    ]

    for size, filename in sizes:
        icon = create_icon(size)
        icon.save(os.path.join(iconset_dir, filename))

    print("✅ Icon images created successfully!")
    print("Run: iconutil -c icns AppIcon.iconset")

except ImportError:
    print("⚠️  PIL/Pillow not installed. Installing...")
    import subprocess
    subprocess.run(['pip3', 'install', 'pillow'])
    print("Please run this script again after installation.")
