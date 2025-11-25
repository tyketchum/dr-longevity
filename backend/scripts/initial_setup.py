#!/usr/bin/env python3
"""
Initial setup script for Longevity Dashboard
Authenticates with Garmin and pulls 90 days of historical data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal
from services.data_sync import DataSyncService

def main():
    print("=" * 60)
    print("LONGEVITY DASHBOARD - INITIAL SETUP")
    print("=" * 60)
    print()
    print("This script will:")
    print("1. Authenticate with Garmin Connect")
    print("2. Pull 90 days of historical data")
    print("3. Calculate activity gaps and streaks")
    print("4. Generate weekly summaries")
    print()

    # Check for required environment variables
    garmin_email = os.getenv('GARMIN_EMAIL')
    garmin_password = os.getenv('GARMIN_PASSWORD')

    if not garmin_email or not garmin_password:
        print("ERROR: Missing Garmin credentials!")
        print()
        print("Please set the following environment variables:")
        print("  GARMIN_EMAIL=your_email@example.com")
        print("  GARMIN_PASSWORD=your_password")
        print()
        print("You can add these to a .env file in the project root.")
        sys.exit(1)

    print()
    print("Starting initial sync...")
    print()

    # Initialize database session
    db = SessionLocal()

    try:
        # Run historical sync
        sync_service = DataSyncService(db)
        sync_service.sync_historical_data(days=90)

        print()
        print("=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start the API server: python backend/main.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Open http://localhost:3000 in your browser")
        print()
        print("To sync new data daily, run: python backend/scripts/daily_sync.py")
        print()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nSetup failed. Please check your Garmin credentials and try again.")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
