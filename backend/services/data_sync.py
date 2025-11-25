from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models import DailyMetrics, Activity, WeeklySummary
from .garmin_service import GarminService
from .activity_classifier import ActivityClassifier
import os

class DataSyncService:
    """Service for syncing data from Garmin and calculating derived metrics"""

    def __init__(self, db: Session):
        self.db = db
        self.garmin = GarminService()
        self.classifier = ActivityClassifier()

    def sync_daily_data(self, target_date: date = None):
        """Sync data for a specific date (defaults to yesterday)"""
        if target_date is None:
            target_date = date.today() - timedelta(days=1)

        print(f"Syncing data for {target_date}...")

        # Fetch Garmin data
        metrics = self.garmin.get_daily_metrics(target_date)
        activities = self.garmin.get_activities(target_date, target_date)

        # Save or update daily metrics
        if metrics:
            self._save_daily_metrics(metrics)

        # Save activities
        for activity in activities:
            activity['zone_classification'] = self.classifier.classify_activity(activity)
            self._save_activity(activity)

        # Recalculate gaps and streaks
        self.recalculate_all_gaps()

        print(f"✓ Sync complete for {target_date}")

    def sync_historical_data(self, days: int = 90):
        """Sync historical data for the past N days"""
        print(f"Starting historical sync for past {days} days...")

        # Fetch from Garmin
        daily_metrics, activities = self.garmin.fetch_historical_data(days)

        # Save daily metrics
        if daily_metrics:
            for metrics in daily_metrics:
                self._save_daily_metrics(metrics)
            print(f"✓ Saved {len(daily_metrics)} days of wellness metrics")

        # Classify and save activities
        if activities:
            for activity in activities:
                activity['zone_classification'] = self.classifier.classify_activity(activity)
                self._save_activity(activity)
            print(f"✓ Saved {len(activities)} activities")

        # Calculate gaps and streaks
        self.recalculate_all_gaps()

        # Calculate weekly summaries
        self.calculate_weekly_summaries()

        print("✓ Historical sync complete!")

    def _save_daily_metrics(self, metrics: dict):
        """Save or update daily metrics in database"""
        existing = self.db.query(DailyMetrics).filter(
            DailyMetrics.date == metrics['date']
        ).first()

        if existing:
            # Update existing record
            for key, value in metrics.items():
                if key != 'date' and value is not None:
                    setattr(existing, key, value)
        else:
            # Create new record
            daily_metric = DailyMetrics(**metrics)
            self.db.add(daily_metric)

        self.db.commit()

    def _save_activity(self, activity: dict):
        """Save or update activity in database"""
        # Check if activity already exists (by activity_id for Garmin, or date+source for CrossFit)
        if activity.get('activity_id'):
            existing = self.db.query(Activity).filter(
                Activity.activity_id == activity['activity_id']
            ).first()
        else:
            # For manual CrossFit entries without activity_id
            existing = self.db.query(Activity).filter(
                and_(
                    Activity.date == activity['date'],
                    Activity.source == activity['source'],
                    Activity.start_time == activity['start_time']
                )
            ).first()

        if existing:
            # Update existing activity
            for key, value in activity.items():
                if value is not None:
                    setattr(existing, key, value)
        else:
            # Create new activity
            new_activity = Activity(**activity)
            self.db.add(new_activity)

        self.db.commit()

    def recalculate_all_gaps(self):
        """Recalculate gaps between all activities and update daily metrics"""
        print("Recalculating activity gaps and streaks...")

        # Get all activities sorted by time
        all_activities = self.db.query(Activity).order_by(Activity.start_time).all()

        if not all_activities:
            print("No activities found, skipping gap calculation")
            return

        # Convert to dict for classifier
        activities_dict = []
        for a in all_activities:
            activities_dict.append({
                'id': a.id,
                'start_time': a.start_time,
                'date': a.date,
                'activity_type': a.activity_type,
                'avg_hr': a.avg_hr,
                'duration_minutes': a.duration_minutes,
                'source': a.source
            })

        # Calculate gaps
        activities_with_gaps = self.classifier.calculate_activity_gaps(activities_dict)

        # Update activities with gap info
        for activity_dict in activities_with_gaps:
            activity = self.db.query(Activity).filter(Activity.id == activity_dict['id']).first()
            if activity:
                activity.hours_since_previous = activity_dict.get('hours_since_previous')
                activity.days_since_previous = activity_dict.get('days_since_previous')

        self.db.commit()

        # Calculate current streak
        current_streak = self.classifier.calculate_streak(activities_dict)

        # Calculate days since last activity
        days_since = self.classifier.days_since_last_activity(activities_dict)

        # Update the most recent daily metric with streak and gap info
        today = date.today()
        recent_metric = self.db.query(DailyMetrics).filter(
            DailyMetrics.date == today
        ).first()

        if not recent_metric:
            # Create today's metric if it doesn't exist
            recent_metric = DailyMetrics(date=today)
            self.db.add(recent_metric)

        recent_metric.current_streak = current_streak
        recent_metric.days_since_last_activity = days_since if days_since else 0

        self.db.commit()

        print(f"✓ Current streak: {current_streak} days")
        print(f"✓ Days since last activity: {days_since}")

    def calculate_weekly_summaries(self):
        """Calculate and save weekly summary statistics"""
        print("Calculating weekly summaries...")

        # Get date range for all data
        first_activity = self.db.query(Activity).order_by(Activity.date).first()
        if not first_activity:
            print("No activities found, skipping weekly summaries")
            return

        # Start from the Monday of the week containing the first activity
        start_date = first_activity.date
        start_date = start_date - timedelta(days=start_date.weekday())  # Move to Monday

        end_date = date.today()

        # Calculate summaries week by week
        current_week_start = start_date
        weeks_calculated = 0

        while current_week_start <= end_date:
            current_week_end = current_week_start + timedelta(days=6)  # Sunday
            self._calculate_week_summary(current_week_start, current_week_end)
            current_week_start += timedelta(days=7)
            weeks_calculated += 1

        self.db.commit()
        print(f"✓ Calculated {weeks_calculated} weekly summaries")

    def _calculate_week_summary(self, week_start: date, week_end: date):
        """Calculate summary statistics for a single week"""
        # Get daily metrics for this week
        daily_metrics = self.db.query(DailyMetrics).filter(
            and_(DailyMetrics.date >= week_start, DailyMetrics.date <= week_end)
        ).all()

        # Get activities for this week
        activities = self.db.query(Activity).filter(
            and_(Activity.date >= week_start, Activity.date <= week_end)
        ).all()

        # Calculate averages
        def safe_avg(values):
            valid = [v for v in values if v is not None]
            return sum(valid) / len(valid) if valid else None

        avg_resting_hr = safe_avg([m.resting_hr for m in daily_metrics])
        avg_hrv = safe_avg([m.hrv for m in daily_metrics])
        avg_stress = safe_avg([m.stress_score for m in daily_metrics])
        avg_body_battery = safe_avg([m.body_battery for m in daily_metrics])
        avg_weight = safe_avg([m.weight for m in daily_metrics])
        avg_sleep_hours = safe_avg([m.sleep_hours for m in daily_metrics])
        avg_sleep_score = safe_avg([m.sleep_score for m in daily_metrics])
        avg_steps = safe_avg([m.steps for m in daily_metrics])

        # Count activities by classification
        zone2_sessions = len([a for a in activities if a.zone_classification == 'zone2'])
        vo2max_sessions = len([a for a in activities if a.zone_classification == 'vo2max'])
        strength_sessions = len([a for a in activities if a.zone_classification == 'strength'])
        total_activities = len(activities)

        # Zone 2 metrics
        zone2_activities = [a for a in activities if a.zone_classification == 'zone2']
        zone2_avg_hr = safe_avg([a.avg_hr for a in zone2_activities if a.avg_hr])
        zone2_total_minutes = sum([a.duration_minutes for a in zone2_activities])

        # Training load
        total_training_load = sum([m.training_load for m in daily_metrics if m.training_load])

        # Gap tracking
        activity_gaps = [a.days_since_previous for a in activities if a.days_since_previous]
        longest_gap = max(activity_gaps) if activity_gaps else None

        # Count unique days with activity
        activity_dates = set([a.date for a in activities])
        days_with_activity = len(activity_dates)

        # Count days with >2 day gaps
        missed_days = len([gap for gap in activity_gaps if gap > 2])

        # Get streak at end of week (from most recent daily metric)
        end_metric = next((m for m in daily_metrics if m.date == week_end), None)
        streak_end = end_metric.current_streak if end_metric else 0

        # Target achievement
        MAX_DAYS_GAP = int(os.getenv('TARGET_MAX_DAYS_BETWEEN_ACTIVITIES', 2))
        TARGET_STEPS = int(os.getenv('TARGET_STEPS_PER_DAY', 8000))
        TARGET_ZONE2 = int(os.getenv('TARGET_ZONE2_SESSIONS_PER_WEEK', 3))
        TARGET_STRENGTH = int(os.getenv('TARGET_STRENGTH_SESSIONS_PER_WEEK', 3))

        hit_zone2_target = 1 if zone2_sessions >= TARGET_ZONE2 else 0
        hit_strength_target = 1 if strength_sessions >= TARGET_STRENGTH else 0
        hit_steps_target = 1 if avg_steps and avg_steps >= TARGET_STEPS else 0
        no_long_gaps = 1 if longest_gap is None or longest_gap <= MAX_DAYS_GAP else 0

        perfect_week = 1 if all([
            hit_zone2_target,
            hit_strength_target,
            hit_steps_target,
            no_long_gaps
        ]) else 0

        # Save or update weekly summary
        existing = self.db.query(WeeklySummary).filter(
            WeeklySummary.week_start_date == week_start
        ).first()

        summary_data = {
            'week_start_date': week_start,
            'week_end_date': week_end,
            'avg_resting_hr': avg_resting_hr,
            'avg_hrv': avg_hrv,
            'avg_stress_score': avg_stress,
            'avg_body_battery': avg_body_battery,
            'avg_weight': avg_weight,
            'avg_sleep_hours': avg_sleep_hours,
            'avg_sleep_score': avg_sleep_score,
            'avg_daily_steps': int(avg_steps) if avg_steps else None,
            'zone2_sessions': zone2_sessions,
            'vo2max_sessions': vo2max_sessions,
            'strength_sessions': strength_sessions,
            'total_activities': total_activities,
            'zone2_avg_hr': zone2_avg_hr,
            'zone2_total_minutes': zone2_total_minutes,
            'total_training_load': int(total_training_load) if total_training_load else None,
            'longest_gap_days': longest_gap,
            'activity_streak_end': streak_end,
            'days_with_activity': days_with_activity,
            'missed_activity_days': missed_days,
            'hit_zone2_target': hit_zone2_target,
            'hit_strength_target': hit_strength_target,
            'hit_steps_target': hit_steps_target,
            'no_long_gaps': no_long_gaps,
            'perfect_week': perfect_week
        }

        if existing:
            for key, value in summary_data.items():
                setattr(existing, key, value)
        else:
            weekly_summary = WeeklySummary(**summary_data)
            self.db.add(weekly_summary)
