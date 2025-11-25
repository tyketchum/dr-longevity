from sqlalchemy import Column, Integer, Float, Date, String
from .database import Base

class MonthlyLabs(Base):
    __tablename__ = 'monthly_labs'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    entry_type = Column(String, nullable=False)  # 'lab' or 'measurement' or 'strength'

    # Lab results
    apob = Column(Float, nullable=True)  # mg/dL - Target: <60
    hba1c = Column(Float, nullable=True)  # % - Target: <5.2
    bp_systolic = Column(Integer, nullable=True)  # mmHg - Target: <120
    bp_diastolic = Column(Integer, nullable=True)  # mmHg - Target: <80
    vo2max = Column(Float, nullable=True)  # ml/kg/min

    # Body composition
    body_fat_percent = Column(Float, nullable=True)  # % from DEXA
    waist_circumference = Column(Float, nullable=True)  # inches

    # Strength metrics (1RM)
    back_squat_1rm = Column(Float, nullable=True)  # lbs
    deadlift_1rm = Column(Float, nullable=True)  # lbs
    ohp_1rm = Column(Float, nullable=True)  # lbs - strict overhead press

    # Notes
    notes = Column(String, nullable=True)

    def __repr__(self):
        return f"<MonthlyLabs(date={self.date}, type={self.entry_type}, apob={self.apob}, hba1c={self.hba1c})>"
