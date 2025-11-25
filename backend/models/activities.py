from sqlalchemy import Column, Integer, Float, Date, DateTime, String, Text
from .database import Base

class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(String, unique=True, nullable=True)  # Garmin activity ID
    date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=True)

    # Source and type
    source = Column(String, nullable=False)  # 'garmin' or 'crossfit'
    activity_type = Column(String, nullable=False)  # cycling, running, strength, etc.
    zone_classification = Column(String, nullable=True)  # zone2, vo2max, strength, other

    # Duration and distance
    duration_minutes = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=True)

    # Heart rate
    avg_hr = Column(Integer, nullable=True)
    max_hr = Column(Integer, nullable=True)
    hr_zone_1_minutes = Column(Float, nullable=True)
    hr_zone_2_minutes = Column(Float, nullable=True)
    hr_zone_3_minutes = Column(Float, nullable=True)
    hr_zone_4_minutes = Column(Float, nullable=True)
    hr_zone_5_minutes = Column(Float, nullable=True)

    # Cycling-specific
    avg_power = Column(Integer, nullable=True)  # watts
    max_power = Column(Integer, nullable=True)  # watts
    normalized_power = Column(Integer, nullable=True)  # watts
    avg_cadence = Column(Integer, nullable=True)  # rpm
    max_cadence = Column(Integer, nullable=True)  # rpm

    # Running-specific
    avg_pace = Column(String, nullable=True)  # min/km or min/mile
    max_pace = Column(String, nullable=True)

    # Elevation
    elevation_gain = Column(Float, nullable=True)  # meters
    elevation_loss = Column(Float, nullable=True)  # meters

    # Performance metrics
    calories = Column(Integer, nullable=True)
    aerobic_training_effect = Column(Float, nullable=True)  # Garmin metric
    anaerobic_training_effect = Column(Float, nullable=True)  # Garmin metric
    vo2max_estimate = Column(Float, nullable=True)  # ml/kg/min

    # CrossFit-specific
    workout_name = Column(String, nullable=True)
    perceived_effort = Column(Integer, nullable=True)  # 1-10 scale

    # Notes
    notes = Column(Text, nullable=True)

    # Gap tracking
    hours_since_previous = Column(Float, nullable=True)  # Hours since last activity
    days_since_previous = Column(Float, nullable=True)  # Days since last activity (decimal)

    def __repr__(self):
        return f"<Activity(date={self.date}, type={self.activity_type}, duration={self.duration_minutes}min, classification={self.zone_classification})>"
