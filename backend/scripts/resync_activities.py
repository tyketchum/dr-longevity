#!/usr/bin/env python3
"""
Re-sync all activities to pull missing power data
"""

import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal
from services.garmin_service import GarminService
from services.data_sync import DataSyncService

def main():
    print("Re-syncing activities to get power data...")

    db = SessionLocal()
    garmin = GarminService()
    sync = DataSyncService(db)

    try:
        # Fetch all activities from past 90 days
        activities = garmin.get_activities(date.today() - timedelta(days=90), date.today())
        print(f"Fetched {len(activities)} activities")

        # Save each activity (will update existing records)
        for activity in activities:
            from services.activity_classifier import ActivityClassifier
            activity['zone_classification'] = ActivityClassifier.classify_activity(activity)
            sync._save_activity(activity)

            if activity.get('avg_power'):
                print(f"  {activity['date']}: {activity['activity_type']} - {activity['avg_power']}W")

        sync.recalculate_all_gaps()

        print("✓ Activities re-synced with power data!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
