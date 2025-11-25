import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Load targets from environment
ZONE2_HR_MIN = int(os.getenv('ZONE2_HR_MIN', 120))
ZONE2_HR_MAX = int(os.getenv('ZONE2_HR_MAX', 140))
ZONE2_MIN_DURATION = int(os.getenv('ZONE2_MIN_DURATION_MINUTES', 40))

VO2MAX_HR_MIN = int(os.getenv('VO2MAX_HR_MIN', 170))
VO2MAX_MIN_DURATION = int(os.getenv('VO2MAX_MIN_DURATION_MINUTES', 25))
VO2MAX_MAX_DURATION = int(os.getenv('VO2MAX_MAX_DURATION_MINUTES', 50))

class ActivityClassifier:
    """Classifies activities into Zone 2, VO2 Max, Strength, or Other"""

    @staticmethod
    def classify_activity(activity: dict) -> str:
        """
        Classify an activity based on its characteristics.

        Classification logic:
        - Zone 2: Cycling/running, duration >40 min, avg HR 120-140 bpm
        - VO2 Max: Cycling/running, duration 25-50 min, avg HR >170 bpm
        - Strength: CrossFit, strength training, weightlifting activities
        - Other: Walking, hiking, yoga, etc.

        Returns: 'zone2', 'vo2max', 'strength', 'other'
        """
        activity_type = activity.get('activity_type', '').lower()
        avg_hr = activity.get('avg_hr')
        duration = activity.get('duration_minutes', 0)
        source = activity.get('source', '')

        # CrossFit is always strength
        if source == 'crossfit':
            return 'strength'

        # Strength activities
        strength_keywords = ['strength', 'weight', 'crossfit', 'gym', 'training', 'fitness']
        if any(keyword in activity_type for keyword in strength_keywords):
            return 'strength'

        # Zone 2 classification (cardio activities only)
        cardio_keywords = ['cycling', 'running', 'biking', 'ride', 'run', 'indoor_cycling']
        is_cardio = any(keyword in activity_type for keyword in cardio_keywords)

        if is_cardio and avg_hr and duration:
            # Check Zone 2 criteria
            if duration >= ZONE2_MIN_DURATION and ZONE2_HR_MIN <= avg_hr <= ZONE2_HR_MAX:
                return 'zone2'

            # Check VO2 Max criteria
            if VO2MAX_MIN_DURATION <= duration <= VO2MAX_MAX_DURATION and avg_hr >= VO2MAX_HR_MIN:
                return 'vo2max'

        # Everything else is "other" (still counts toward activity streak)
        return 'other'

    @staticmethod
    def calculate_activity_gaps(activities: list):
        """
        Calculate gaps between activities and add gap info to each activity.

        Args:
            activities: List of activity dicts sorted by start_time (oldest first)

        Returns:
            activities with added fields: hours_since_previous, days_since_previous
        """
        if not activities:
            return activities

        # Sort by start_time to ensure chronological order
        sorted_activities = sorted(activities, key=lambda x: x['start_time'])

        # First activity has no previous activity
        sorted_activities[0]['hours_since_previous'] = None
        sorted_activities[0]['days_since_previous'] = None

        # Calculate gaps for subsequent activities
        for i in range(1, len(sorted_activities)):
            current = sorted_activities[i]['start_time']
            previous = sorted_activities[i-1]['start_time']

            gap = current - previous
            hours_gap = gap.total_seconds() / 3600
            days_gap = gap.total_seconds() / 86400

            sorted_activities[i]['hours_since_previous'] = round(hours_gap, 2)
            sorted_activities[i]['days_since_previous'] = round(days_gap, 2)

        return sorted_activities

    @staticmethod
    def calculate_streak(activities: list, max_gap_days: float = 2.0):
        """
        Calculate current activity streak.

        A streak continues as long as there's no gap >max_gap_days between activities.
        Streak counts from most recent activity backwards.

        **CRITICAL**: If the most recent activity is >max_gap_days ago from NOW, streak is 0!

        Args:
            activities: List of activity dicts sorted by start_time (oldest first)
            max_gap_days: Maximum gap in days before streak resets (default: 2.0)

        Returns:
            Current streak in days (number of consecutive days with activity)
        """
        if not activities:
            return 0

        # Sort by start_time descending (most recent first)
        sorted_activities = sorted(activities, key=lambda x: x['start_time'], reverse=True)

        # CRITICAL FIX: Check if most recent activity is too old
        most_recent = sorted_activities[0]['start_time']
        gap_from_now = datetime.now() - most_recent
        days_since_last = gap_from_now.total_seconds() / 86400

        if days_since_last > max_gap_days:
            # Streak is broken! Last activity was too long ago
            return 0

        streak_days = set()
        last_activity_date = None

        for activity in sorted_activities:
            activity_date = activity['start_time'].date()

            if last_activity_date is None:
                # First (most recent) activity
                streak_days.add(activity_date)
                last_activity_date = activity_date
            else:
                # Check gap from last activity
                gap_days = (last_activity_date - activity_date).days

                if gap_days <= max_gap_days:
                    # Streak continues
                    streak_days.add(activity_date)
                    last_activity_date = activity_date
                else:
                    # Streak broken
                    break

        return len(streak_days)

    @staticmethod
    def days_since_last_activity(activities: list):
        """
        Calculate days since the most recent activity.

        Args:
            activities: List of activity dicts

        Returns:
            Number of days since last activity (float), or None if no activities
        """
        if not activities:
            return None

        # Find most recent activity
        most_recent = max(activities, key=lambda x: x['start_time'])
        gap = datetime.now() - most_recent['start_time']

        return round(gap.total_seconds() / 86400, 1)
