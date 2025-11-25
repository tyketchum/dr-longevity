#!/usr/bin/env python3
"""
Daily sync script for Longevity Dashboard
Run this once per day (via cron or manually) to sync yesterday's data
"""

import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal
from services.data_sync import DataSyncService

def main():
    print(f"Starting daily sync for {date.today()}...")

    db = SessionLocal()

    try:
        sync_service = DataSyncService(db)
        sync_service.sync_daily_data()
        sync_service.calculate_weekly_summaries()

        print("✅ Daily sync complete!")

    except Exception as e:
        print(f"❌ Sync failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
