#!/bin/bash
# Manual Garmin Sync Script

echo "🔄 Syncing data from Garmin Connect..."

# Call the sync endpoint
response=$(curl -s -X POST http://localhost:8000/sync/daily)

if [ $? -eq 0 ]; then
    echo "✅ Sync complete!"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo "❌ Sync failed. Is the dashboard running?"
    echo "   Start it with: ./start_dashboard.sh"
fi
