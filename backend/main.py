from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import os

from models import Base, engine, SessionLocal, DailyMetrics, Activity, WeeklySummary, MonthlyLabs, FoodLog, WaterLog
from models.database import init_db, get_db
from services.data_sync import DataSyncService

# Initialize database
init_db()

app = FastAPI(title="Longevity Dashboard API")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class ActivityCreate(BaseModel):
    date: date
    source: str = "crossfit"
    activity_type: str = "strength"
    workout_name: Optional[str] = None
    duration_minutes: float
    perceived_effort: Optional[int] = None
    notes: Optional[str] = None

class LabEntry(BaseModel):
    date: date
    entry_type: str
    apob: Optional[float] = None
    hba1c: Optional[float] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    vo2max: Optional[float] = None
    body_fat_percent: Optional[float] = None
    waist_circumference: Optional[float] = None
    back_squat_1rm: Optional[float] = None
    deadlift_1rm: Optional[float] = None
    ohp_1rm: Optional[float] = None
    notes: Optional[str] = None

class DashboardStatus(BaseModel):
    days_since_last_activity: float
    current_streak: int
    alert_level: str  # 'green', 'yellow', 'red'
    last_activity_date: Optional[date]
    last_activity_type: Optional[str]

class FoodEntry(BaseModel):
    date: date
    meal_type: str  # breakfast, lunch, dinner, snack
    food_name: str
    portion_size: Optional[str] = None
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: Optional[str] = None

class WaterEntry(BaseModel):
    date: date
    amount_oz: float
    with_electrolytes: bool = False

# ============= ENDPOINTS =============

@app.get("/")
def root():
    return {"message": "Longevity Dashboard API", "status": "running"}

@app.get("/status", response_model=DashboardStatus)
def get_status(db: Session = Depends(get_db)):
    """Get current activity status - the CRITICAL metric"""
    # Get most recent daily metric
    today_metric = db.query(DailyMetrics).filter(
        DailyMetrics.date == date.today()
    ).first()

    # Get most recent activity
    last_activity = db.query(Activity).order_by(Activity.start_time.desc()).first()

    if not last_activity:
        return {
            "days_since_last_activity": 999,
            "current_streak": 0,
            "alert_level": "red",
            "last_activity_date": None,
            "last_activity_type": None
        }

    # Calculate days since last activity
    gap = datetime.now() - last_activity.start_time
    days_since = gap.total_seconds() / 86400

    # Determine alert level
    if days_since < 1.5:
        alert_level = "green"
    elif days_since < 2.0:
        alert_level = "yellow"
    else:
        alert_level = "red"

    streak = today_metric.current_streak if today_metric else 0

    return {
        "days_since_last_activity": round(days_since, 1),
        "current_streak": streak,
        "alert_level": alert_level,
        "last_activity_date": last_activity.date,
        "last_activity_type": last_activity.activity_type
    }

@app.get("/daily-metrics")
def get_daily_metrics(days: int = 90, db: Session = Depends(get_db)):
    """Get daily wellness metrics for the past N days"""
    start_date = date.today() - timedelta(days=days)
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.date >= start_date
    ).order_by(DailyMetrics.date.desc()).all()

    return [
        {
            "date": m.date.isoformat(),
            "resting_hr": m.resting_hr,
            "hrv": m.hrv,
            "stress_score": m.stress_score,
            "body_battery": m.body_battery,
            "weight": m.weight,
            "sleep_hours": m.sleep_hours,
            "sleep_score": m.sleep_score,
            "steps": m.steps,
            "training_load": m.training_load,
            "days_since_last_activity": m.days_since_last_activity,
            "current_streak": m.current_streak
        }
        for m in metrics
    ]

@app.get("/activities")
def get_activities(days: int = 90, db: Session = Depends(get_db)):
    """Get activities for the past N days"""
    start_date = date.today() - timedelta(days=days)
    activities = db.query(Activity).filter(
        Activity.date >= start_date
    ).order_by(Activity.start_time.desc()).all()

    return [
        {
            "id": a.id,
            "date": a.date.isoformat(),
            "start_time": a.start_time.isoformat(),
            "source": a.source,
            "activity_type": a.activity_type,
            "zone_classification": a.zone_classification,
            "duration_minutes": a.duration_minutes,
            "distance_km": a.distance_km,
            "avg_hr": a.avg_hr,
            "max_hr": a.max_hr,
            "calories": a.calories,
            "avg_power": a.avg_power,
            "avg_cadence": a.avg_cadence,
            "elevation_gain": a.elevation_gain,
            "workout_name": a.workout_name,
            "hours_since_previous": a.hours_since_previous,
            "days_since_previous": a.days_since_previous,
            "notes": a.notes
        }
        for a in activities
    ]

@app.get("/weekly-summaries")
def get_weekly_summaries(weeks: int = 12, db: Session = Depends(get_db)):
    """Get weekly summary statistics"""
    summaries = db.query(WeeklySummary).order_by(
        WeeklySummary.week_start_date.desc()
    ).limit(weeks).all()

    return [
        {
            "week_start": w.week_start_date.isoformat(),
            "week_end": w.week_end_date.isoformat(),
            "avg_resting_hr": w.avg_resting_hr,
            "avg_stress_score": w.avg_stress_score,
            "avg_body_battery": w.avg_body_battery,
            "avg_weight": w.avg_weight,
            "avg_sleep_hours": w.avg_sleep_hours,
            "zone2_sessions": w.zone2_sessions,
            "vo2max_sessions": w.vo2max_sessions,
            "strength_sessions": w.strength_sessions,
            "total_activities": w.total_activities,
            "zone2_avg_hr": w.zone2_avg_hr,
            "avg_daily_steps": w.avg_daily_steps,
            "longest_gap_days": w.longest_gap_days,
            "activity_streak_end": w.activity_streak_end,
            "days_with_activity": w.days_with_activity,
            "hit_zone2_target": w.hit_zone2_target,
            "hit_strength_target": w.hit_strength_target,
            "no_long_gaps": w.no_long_gaps,
            "perfect_week": w.perfect_week
        }
        for w in summaries
    ]

@app.get("/labs")
def get_labs(db: Session = Depends(get_db)):
    """Get all lab results and measurements"""
    labs = db.query(MonthlyLabs).order_by(MonthlyLabs.date.desc()).all()

    return [
        {
            "id": lab.id,
            "date": lab.date.isoformat(),
            "entry_type": lab.entry_type,
            "apob": lab.apob,
            "hba1c": lab.hba1c,
            "bp_systolic": lab.bp_systolic,
            "bp_diastolic": lab.bp_diastolic,
            "vo2max": lab.vo2max,
            "body_fat_percent": lab.body_fat_percent,
            "waist_circumference": lab.waist_circumference,
            "back_squat_1rm": lab.back_squat_1rm,
            "deadlift_1rm": lab.deadlift_1rm,
            "ohp_1rm": lab.ohp_1rm,
            "notes": lab.notes
        }
        for lab in labs
    ]

@app.post("/activities")
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Manually add a CrossFit or other activity"""
    new_activity = Activity(
        date=activity.date,
        start_time=datetime.combine(activity.date, datetime.min.time()),
        source=activity.source,
        activity_type=activity.activity_type,
        workout_name=activity.workout_name,
        duration_minutes=activity.duration_minutes,
        perceived_effort=activity.perceived_effort,
        notes=activity.notes,
        zone_classification='strength' if activity.source == 'crossfit' else 'other'
    )

    db.add(new_activity)
    db.commit()

    # Recalculate gaps
    sync_service = DataSyncService(db)
    sync_service.recalculate_all_gaps()

    return {"message": "Activity created", "id": new_activity.id}

@app.post("/labs")
def create_lab_entry(lab: LabEntry, db: Session = Depends(get_db)):
    """Add a lab result or measurement"""
    new_lab = MonthlyLabs(**lab.dict())
    db.add(new_lab)
    db.commit()

    return {"message": "Lab entry created", "id": new_lab.id}

@app.post("/sync/daily")
def sync_daily(db: Session = Depends(get_db)):
    """Sync yesterday's data from Garmin"""
    try:
        sync_service = DataSyncService(db)
        sync_service.sync_daily_data()
        return {"message": "Daily sync complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync/historical")
def sync_historical(days: int = 90, db: Session = Depends(get_db)):
    """Sync historical data from Garmin (one-time setup)"""
    try:
        sync_service = DataSyncService(db)
        sync_service.sync_historical_data(days)
        return {"message": f"Historical sync complete for {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar")
def get_calendar_data(year: int, month: int, db: Session = Depends(get_db)):
    """Get activity calendar data for a specific month"""
    from calendar import monthrange

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    activities = db.query(Activity).filter(
        Activity.date >= start_date,
        Activity.date <= end_date
    ).all()

    # Group by date
    activity_dates = {}
    for a in activities:
        date_str = a.date.isoformat()
        if date_str not in activity_dates:
            activity_dates[date_str] = []
        activity_dates[date_str].append({
            "type": a.activity_type,
            "classification": a.zone_classification,
            "duration": a.duration_minutes
        })

    return activity_dates

@app.post("/export/csv")
def export_to_csv(db: Session = Depends(get_db)):
    """Export all data to CSV files"""
    import subprocess
    from datetime import datetime

    try:
        # Run export script
        result = subprocess.run(
            ['python3', 'backend/scripts/export_csv.py'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return {
                "message": "CSV export complete",
                "export_dir": f"backups/export_{timestamp}",
                "output": result.stdout
            }
        else:
            raise HTTPException(status_code=500, detail=result.stderr)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/food")
def get_food_log(days: int = 7, db: Session = Depends(get_db)):
    """Get food log entries for the past N days"""
    start_date = date.today() - timedelta(days=days)
    entries = db.query(FoodLog).filter(
        FoodLog.date >= start_date
    ).order_by(FoodLog.time.desc()).all()

    return [
        {
            "id": entry.id,
            "date": entry.date.isoformat(),
            "time": entry.time.isoformat(),
            "meal_type": entry.meal_type,
            "food_name": entry.food_name,
            "portion_size": entry.portion_size,
            "calories": entry.calories,
            "protein_g": entry.protein_g,
            "carbs_g": entry.carbs_g,
            "fat_g": entry.fat_g,
            "notes": entry.notes
        }
        for entry in entries
    ]

@app.post("/food")
def log_food(food: FoodEntry, db: Session = Depends(get_db)):
    """Add a food log entry"""
    new_entry = FoodLog(**food.dict())
    db.add(new_entry)
    db.commit()
    return {"message": "Food entry logged", "id": new_entry.id}

@app.get("/water")
def get_water_log(days: int = 7, db: Session = Depends(get_db)):
    """Get water log entries for the past N days"""
    start_date = date.today() - timedelta(days=days)
    entries = db.query(WaterLog).filter(
        WaterLog.date >= start_date
    ).order_by(WaterLog.time.desc()).all()

    return [
        {
            "id": entry.id,
            "date": entry.date.isoformat(),
            "time": entry.time.isoformat(),
            "amount_oz": entry.amount_oz,
            "with_electrolytes": bool(entry.with_electrolytes)
        }
        for entry in entries
    ]

@app.post("/water")
def log_water(water: WaterEntry, db: Session = Depends(get_db)):
    """Add a water log entry"""
    data = water.dict()
    data['with_electrolytes'] = 1 if data['with_electrolytes'] else 0
    new_entry = WaterLog(**data)
    db.add(new_entry)
    db.commit()
    return {"message": "Water intake logged", "id": new_entry.id}

@app.get("/water/today")
def get_today_water(db: Session = Depends(get_db)):
    """Get today's total water intake"""
    today = date.today()
    entries = db.query(WaterLog).filter(WaterLog.date == today).all()
    total = sum(entry.amount_oz for entry in entries)
    return {"total_oz": total, "goal_oz": 140}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('API_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
