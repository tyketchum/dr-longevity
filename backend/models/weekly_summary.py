from sqlalchemy import Column, Integer, Float, Date, String
from .database import Base

class WeeklySummary(Base):
    __tablename__ = 'weekly_summary'

    id = Column(Integer, primary_key=True, index=True)
    week_start_date = Column(Date, unique=True, nullable=False, index=True)  # Monday of the week
    week_end_date = Column(Date, nullable=False)  # Sunday of the week

    # Heart metrics (7-day moving averages)
    avg_resting_hr = Column(Float, nullable=True)
    avg_hrv = Column(Float, nullable=True)
    avg_stress_score = Column(Float, nullable=True)
    avg_body_battery = Column(Float, nullable=True)

    # Weight
    avg_weight = Column(Float, nullable=True)

    # Sleep (weekly averages)
    avg_sleep_hours = Column(Float, nullable=True)
    avg_sleep_score = Column(Float, nullable=True)

    # Activity counts
    zone2_sessions = Column(Integer, default=0)
    vo2max_sessions = Column(Integer, default=0)
    strength_sessions = Column(Integer, default=0)
    total_activities = Column(Integer, default=0)

    # Zone 2 metrics
    zone2_avg_hr = Column(Float, nullable=True)  # Average HR across all Zone 2 sessions
    zone2_total_minutes = Column(Float, nullable=True)

    # Training load
    total_training_load = Column(Integer, nullable=True)
    avg_daily_steps = Column(Integer, nullable=True)

    # Gap tracking (CRITICAL)
    longest_gap_days = Column(Float, nullable=True)  # Longest gap between activities this week
    activity_streak_end = Column(Integer, nullable=True)  # Streak at end of week
    days_with_activity = Column(Integer, default=0)  # How many days had activity
    missed_activity_days = Column(Integer, default=0)  # Days with >2 day gap

    # Target achievement
    hit_zone2_target = Column(Integer, default=0)  # Boolean: 1 if hit 3-4 Zone 2 sessions
    hit_strength_target = Column(Integer, default=0)  # Boolean: 1 if hit 3 strength sessions
    hit_steps_target = Column(Integer, default=0)  # Boolean: 1 if hit 8000+ steps daily avg
    no_long_gaps = Column(Integer, default=0)  # Boolean: 1 if no gaps >2 days
    perfect_week = Column(Integer, default=0)  # Boolean: 1 if hit all targets

    def __repr__(self):
        return f"<WeeklySummary(week={self.week_start_date}, activities={self.total_activities}, longest_gap={self.longest_gap_days}, perfect={self.perfect_week})>"
