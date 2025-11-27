#!/usr/bin/env python3
"""Split cycling routes into multiple files to stay under size limits"""

import json
import os

# Load the full routes file
with open('cycling_routes.json', 'r') as f:
    routes = json.load(f)

print(f"Total routes: {len(routes)}")

# Split into chunks (aim for ~50MB per file to stay well under 100MB)
# With 575 routes, split into 2 files
chunk_size = len(routes) // 2 + 1

for i, start_idx in enumerate(range(0, len(routes), chunk_size), 1):
    chunk = routes[start_idx:start_idx + chunk_size]
    filename = f'cycling_routes_part{i}.json'

    with open(filename, 'w') as f:
        json.dump(chunk, f, indent=2)

    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"Created {filename}: {len(chunk)} routes, {size_mb:.1f}MB")

print("\n✅ Routes split successfully!")
