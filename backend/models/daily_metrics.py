from sqlalchemy import Column, Integer, Float, Date, String
from .database import Base

class DailyMetrics(Base):
    __tablename__ = 'daily_metrics'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)

    # Heart metrics
    resting_hr = Column(Integer, nullable=True)  # bpm
    hrv = Column(Float, nullable=True)  # ms (if available)
    stress_score = Column(Integer, nullable=True)  # Garmin stress 0-100 (lower is better)

    # Recovery metrics
    body_battery = Column(Integer, nullable=True)  # 0-100

    # Body composition
    weight = Column(Float, nullable=True)  # lbs

    # Sleep metrics
    sleep_hours = Column(Float, nullable=True)
    sleep_score = Column(Integer, nullable=True)  # Garmin sleep score
    sleep_deep_hours = Column(Float, nullable=True)
    sleep_light_hours = Column(Float, nullable=True)
    sleep_rem_hours = Column(Float, nullable=True)
    sleep_awake_hours = Column(Float, nullable=True)

    # Activity metrics
    steps = Column(Integer, nullable=True)
    floors_climbed = Column(Integer, nullable=True)
    intensity_minutes = Column(Integer, nullable=True)  # Garmin intensity minutes
    training_load = Column(Integer, nullable=True)  # Garmin training load

    # Respiratory
    respiration_rate = Column(Float, nullable=True)  # breaths/min
    spo2 = Column(Float, nullable=True)  # % blood oxygen

    # Calculated fields
    days_since_last_activity = Column(Integer, nullable=True)  # Critical metric
    current_streak = Column(Integer, nullable=True)  # Days with activity (resets if >2 day gap)

    def __repr__(self):
        return f"<DailyMetrics(date={self.date}, resting_hr={self.resting_hr}, days_since_last_activity={self.days_since_last_activity})>"
