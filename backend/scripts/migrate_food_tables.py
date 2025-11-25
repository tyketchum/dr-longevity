#!/usr/bin/env python3
"""
Create food_log and water_log tables
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base, engine
from models.food_log import FoodLog, WaterLog

def main():
    print("Creating food_log and water_log tables...")

    # Create only the food-related tables
    FoodLog.__table__.create(bind=engine, checkfirst=True)
    WaterLog.__table__.create(bind=engine, checkfirst=True)

    print("✓ Tables created successfully!")

if __name__ == "__main__":
    main()
