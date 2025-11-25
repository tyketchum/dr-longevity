from sqlalchemy import Column, Integer, Float, Date, DateTime, String, Text
from .database import Base
from datetime import datetime

class FoodLog(Base):
    __tablename__ = 'food_log'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(DateTime, default=datetime.now)
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack

    # Quick entry
    food_name = Column(String, nullable=False)
    portion_size = Column(String, nullable=True)  # "1 cup", "2 oz", "1 serving"

    # Optional macros (can be left blank for quick entry)
    calories = Column(Integer, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<FoodLog(date={self.date}, meal={self.meal_type}, food={self.food_name})>"


class WaterLog(Base):
    __tablename__ = 'water_log'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(DateTime, default=datetime.now)
    amount_oz = Column(Float, nullable=False)  # ounces
    with_electrolytes = Column(Integer, default=0)  # 0 = no, 1 = yes (SQLite doesn't have boolean)

    def __repr__(self):
        return f"<WaterLog(date={self.date}, amount={self.amount_oz}oz, electrolytes={bool(self.with_electrolytes)})>"
