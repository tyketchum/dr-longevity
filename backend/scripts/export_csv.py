#!/usr/bin/env python3
"""
Export all data to CSV files for backup
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal, DailyMetrics, Activity, WeeklySummary, MonthlyLabs
import csv

def export_to_csv():
    """Export all database tables to CSV files"""
    db = SessionLocal()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = f'backups/export_{timestamp}'

    # Create export directory
    os.makedirs(export_dir, exist_ok=True)

    try:
        # Export daily metrics
        print("Exporting daily metrics...")
        daily_metrics = db.query(DailyMetrics).order_by(DailyMetrics.date).all()
        with open(f'{export_dir}/daily_metrics.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'date', 'resting_hr', 'hrv', 'stress_score', 'body_battery', 'weight',
                'sleep_hours', 'sleep_score', 'sleep_deep_hours', 'sleep_light_hours',
                'sleep_rem_hours', 'sleep_awake_hours', 'steps', 'floors_climbed',
                'intensity_minutes', 'training_load', 'respiration_rate', 'spo2',
                'days_since_last_activity', 'current_streak'
            ])
            for m in daily_metrics:
                writer.writerow([
                    m.date, m.resting_hr, m.hrv, m.stress_score, m.body_battery, m.weight,
                    m.sleep_hours, m.sleep_score, m.sleep_deep_hours, m.sleep_light_hours,
                    m.sleep_rem_hours, m.sleep_awake_hours, m.steps, m.floors_climbed,
                    m.intensity_minutes, m.training_load, m.respiration_rate, m.spo2,
                    m.days_since_last_activity, m.current_streak
                ])
        print(f"✓ Exported {len(daily_metrics)} daily metrics")

        # Export activities
        print("Exporting activities...")
        activities = db.query(Activity).order_by(Activity.start_time).all()
        with open(f'{export_dir}/activities.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'activity_id', 'date', 'start_time', 'source', 'activity_type',
                'zone_classification', 'duration_minutes', 'distance_km', 'avg_hr',
                'max_hr', 'calories', 'avg_power', 'max_power', 'normalized_power',
                'avg_cadence', 'max_cadence', 'elevation_gain', 'elevation_loss',
                'aerobic_training_effect', 'anaerobic_training_effect', 'vo2max_estimate',
                'workout_name', 'perceived_effort', 'hours_since_previous',
                'days_since_previous', 'notes'
            ])
            for a in activities:
                writer.writerow([
                    a.activity_id, a.date, a.start_time, a.source, a.activity_type,
                    a.zone_classification, a.duration_minutes, a.distance_km, a.avg_hr,
                    a.max_hr, a.calories, a.avg_power, a.max_power, a.normalized_power,
                    a.avg_cadence, a.max_cadence, a.elevation_gain, a.elevation_loss,
                    a.aerobic_training_effect, a.anaerobic_training_effect, a.vo2max_estimate,
                    a.workout_name, a.perceived_effort, a.hours_since_previous,
                    a.days_since_previous, a.notes
                ])
        print(f"✓ Exported {len(activities)} activities")

        # Export weekly summaries
        print("Exporting weekly summaries...")
        summaries = db.query(WeeklySummary).order_by(WeeklySummary.week_start_date).all()
        with open(f'{export_dir}/weekly_summaries.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'week_start_date', 'week_end_date', 'avg_resting_hr', 'avg_hrv',
                'avg_stress_score', 'avg_body_battery', 'avg_weight', 'avg_sleep_hours',
                'avg_sleep_score', 'avg_daily_steps', 'zone2_sessions', 'vo2max_sessions',
                'strength_sessions', 'total_activities', 'zone2_avg_hr', 'zone2_total_minutes',
                'total_training_load', 'longest_gap_days', 'activity_streak_end',
                'days_with_activity', 'missed_activity_days', 'hit_zone2_target',
                'hit_strength_target', 'hit_steps_target', 'no_long_gaps', 'perfect_week'
            ])
            for w in summaries:
                writer.writerow([
                    w.week_start_date, w.week_end_date, w.avg_resting_hr, w.avg_hrv,
                    w.avg_stress_score, w.avg_body_battery, w.avg_weight, w.avg_sleep_hours,
                    w.avg_sleep_score, w.avg_daily_steps, w.zone2_sessions, w.vo2max_sessions,
                    w.strength_sessions, w.total_activities, w.zone2_avg_hr, w.zone2_total_minutes,
                    w.total_training_load, w.longest_gap_days, w.activity_streak_end,
                    w.days_with_activity, w.missed_activity_days, w.hit_zone2_target,
                    w.hit_strength_target, w.hit_steps_target, w.no_long_gaps, w.perfect_week
                ])
        print(f"✓ Exported {len(summaries)} weekly summaries")

        # Export lab results
        print("Exporting lab results...")
        labs = db.query(MonthlyLabs).order_by(MonthlyLabs.date).all()
        with open(f'{export_dir}/lab_results.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'date', 'entry_type', 'apob', 'hba1c', 'bp_systolic', 'bp_diastolic',
                'vo2max', 'body_fat_percent', 'waist_circumference', 'back_squat_1rm',
                'deadlift_1rm', 'ohp_1rm', 'notes'
            ])
            for lab in labs:
                writer.writerow([
                    lab.date, lab.entry_type, lab.apob, lab.hba1c, lab.bp_systolic,
                    lab.bp_diastolic, lab.vo2max, lab.body_fat_percent,
                    lab.waist_circumference, lab.back_squat_1rm, lab.deadlift_1rm,
                    lab.ohp_1rm, lab.notes
                ])
        print(f"✓ Exported {len(labs)} lab results")

        print()
        print(f"✅ Export complete! Files saved to: {export_dir}")
        print()
        print("Files created:")
        print(f"  - {export_dir}/daily_metrics.csv")
        print(f"  - {export_dir}/activities.csv")
        print(f"  - {export_dir}/weekly_summaries.csv")
        print(f"  - {export_dir}/lab_results.csv")

    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    export_to_csv()
