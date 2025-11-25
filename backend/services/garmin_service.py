import os
from datetime import datetime, timedelta, date
from garminconnect import Garmin
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()

class GarminService:
    """Service for interacting with Garmin Connect API"""

    def __init__(self):
        self.email = os.getenv('GARMIN_EMAIL')
        self.password = os.getenv('GARMIN_PASSWORD')
        self.client = None
        self.tokens_dir = Path.home() / '.garmin_tokens'
        self.tokens_dir.mkdir(exist_ok=True)
        self.tokens_file = self.tokens_dir / 'tokens.json'

    def login(self):
        """Login to Garmin Connect with token persistence"""
        try:
            self.client = Garmin(self.email, self.password)
            self.client.login()
            print("✓ Logged in to Garmin Connect")
            return True

        except Exception as e:
            print(f"✗ Failed to login to Garmin Connect: {e}")
            print(f"   Please verify your credentials in .env file")
            return False

    def get_daily_metrics(self, target_date: date):
        """Fetch wellness metrics for a specific date"""
        if not self.client:
            if not self.login():
                return None

        try:
            date_str = target_date.isoformat()

            # Get various wellness metrics
            stats = self.client.get_stats(date_str)
            sleep_data = self.client.get_sleep_data(date_str)
            heart_rate = self.client.get_heart_rates(date_str)
            stress = self.client.get_stress_data(date_str)
            body_battery = self.client.get_body_battery(date_str)

            # Parse metrics
            metrics = {
                'date': target_date,
                'resting_hr': heart_rate.get('restingHeartRate') if heart_rate else None,
                'stress_score': stress.get('avgStressLevel') if stress else None,
                'body_battery': body_battery[-1].get('charged') if body_battery and len(body_battery) > 0 else None,
                'steps': stats.get('totalSteps') if stats else None,
                'floors_climbed': stats.get('floorsAscended') if stats else None,
                'intensity_minutes': stats.get('intensityMinutesGoal') if stats else None,
                'respiration_rate': None,  # Will add if available in API response
                'spo2': None,  # Will add if available
            }

            # Parse sleep data
            if sleep_data:
                sleep_summary = sleep_data.get('dailySleepDTO', {})
                metrics['sleep_hours'] = sleep_summary.get('sleepTimeSeconds', 0) / 3600
                metrics['sleep_score'] = sleep_summary.get('sleepScores', {}).get('overall', {}).get('value')

                # Sleep stages
                sleep_levels = sleep_summary.get('sleepLevels', {})
                if sleep_levels:
                    metrics['sleep_deep_hours'] = sleep_levels.get('deepSleepSeconds', 0) / 3600
                    metrics['sleep_light_hours'] = sleep_levels.get('lightSleepSeconds', 0) / 3600
                    metrics['sleep_rem_hours'] = sleep_levels.get('remSleepSeconds', 0) / 3600
                    metrics['sleep_awake_hours'] = sleep_levels.get('awakeSleepSeconds', 0) / 3600

            return metrics

        except Exception as e:
            print(f"Error fetching daily metrics for {target_date}: {e}")
            return None

    def get_activities(self, start_date: date, end_date: date):
        """Fetch activities between two dates"""
        if not self.client:
            if not self.login():
                return []

        try:
            activities = self.client.get_activities_by_date(
                start_date.isoformat(),
                end_date.isoformat()
            )

            parsed_activities = []
            for activity in activities:
                # Parse activity details
                activity_id = activity.get('activityId')
                activity_type = activity.get('activityType', {}).get('typeKey', 'unknown')

                # Get detailed activity data for power/cadence
                details = activity
                try:
                    details = self.client.get_activity(activity_id)
                except Exception as e:
                    print(f"Could not fetch details for activity {activity_id}: {e}")

                parsed = {
                    'activity_id': str(activity_id),
                    'date': datetime.fromisoformat(activity['startTimeLocal'].replace('Z', '+00:00')).date(),
                    'start_time': datetime.fromisoformat(activity['startTimeLocal'].replace('Z', '+00:00')),
                    'source': 'garmin',
                    'activity_type': activity_type,
                    'duration_minutes': activity.get('duration', 0) / 60,
                    'distance_km': activity.get('distance', 0) / 1000 if activity.get('distance') else None,
                    'avg_hr': activity.get('averageHR'),
                    'max_hr': activity.get('maxHR'),
                    'calories': activity.get('calories'),
                    'elevation_gain': activity.get('elevationGain'),
                    'elevation_loss': activity.get('elevationLoss'),
                }

                # Cycling-specific metrics - check both summary and details
                if 'cycling' in activity_type.lower() or 'biking' in activity_type.lower():
                    parsed['avg_power'] = details.get('avgPower') or activity.get('avgPower')
                    parsed['max_power'] = details.get('maxPower') or activity.get('maxPower')
                    parsed['normalized_power'] = details.get('normalizedPower') or activity.get('normalizedPower')
                    parsed['avg_cadence'] = details.get('avgBikeCadence') or activity.get('avgBikeCadence')
                    parsed['max_cadence'] = details.get('maxBikeCadence') or activity.get('maxBikeCadence')

                # Running-specific
                if 'running' in activity_type.lower():
                    parsed['avg_pace'] = activity.get('avgPace')
                    parsed['max_pace'] = activity.get('maxPace')

                # Training effects
                parsed['aerobic_training_effect'] = activity.get('aerobicTrainingEffect')
                parsed['anaerobic_training_effect'] = activity.get('anaerobicTrainingEffect')
                parsed['vo2max_estimate'] = activity.get('vO2MaxValue')

                parsed_activities.append(parsed)

            return parsed_activities

        except Exception as e:
            print(f"Error fetching activities: {e}")
            return []

    def get_weight(self, target_date: date):
        """Fetch weight data for a specific date"""
        if not self.client:
            if not self.login():
                return None

        try:
            # Garmin weight is in kg, convert to lbs
            weight_data = self.client.get_body_composition(target_date.isoformat())
            if weight_data and 'weight' in weight_data:
                weight_kg = weight_data['weight'] / 1000  # Garmin returns in grams
                return weight_kg * 2.20462  # Convert to lbs
            return None
        except Exception as e:
            print(f"Error fetching weight for {target_date}: {e}")
            return None

    def fetch_historical_data(self, days: int = 90):
        """Fetch historical data for the past N days"""
        print(f"Fetching {days} days of historical data from Garmin Connect...")

        if not self.login():
            return None, None

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Fetch activities
        print(f"Fetching activities from {start_date} to {end_date}...")
        activities = self.get_activities(start_date, end_date)
        print(f"✓ Fetched {len(activities)} activities")

        # Fetch daily metrics
        print(f"Fetching daily wellness metrics...")
        daily_metrics = []
        current_date = start_date
        while current_date <= end_date:
            metrics = self.get_daily_metrics(current_date)
            if metrics:
                daily_metrics.append(metrics)
            current_date += timedelta(days=1)

        print(f"✓ Fetched {len(daily_metrics)} days of wellness metrics")

        return daily_metrics, activities
