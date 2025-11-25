-- Longevity Dashboard Database Schema for Supabase (PostgreSQL)
-- Run this in your Supabase SQL Editor after creating your project

-- Enable UUID extension (useful for future features)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Daily Metrics Table
CREATE TABLE IF NOT EXISTS daily_metrics (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    resting_hr INTEGER,
    hrv FLOAT,
    stress_score INTEGER,
    body_battery INTEGER,
    weight FLOAT,
    sleep_hours FLOAT,
    sleep_score INTEGER,
    sleep_deep_hours FLOAT,
    sleep_light_hours FLOAT,
    sleep_rem_hours FLOAT,
    sleep_awake_hours FLOAT,
    steps INTEGER,
    floors_climbed INTEGER,
    intensity_minutes INTEGER,
    training_load INTEGER,
    respiration_rate FLOAT,
    spo2 FLOAT,
    days_since_last_activity INTEGER,
    current_streak INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_daily_metrics_date ON daily_metrics(date);

-- Activities Table
CREATE TABLE IF NOT EXISTS activities (
    id BIGSERIAL PRIMARY KEY,
    activity_id VARCHAR(255) UNIQUE,
    date DATE NOT NULL,
    start_time TIMESTAMP,
    source VARCHAR(50) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    zone_classification VARCHAR(50),
    duration_minutes FLOAT NOT NULL,
    distance_km FLOAT,
    avg_hr INTEGER,
    max_hr INTEGER,
    hr_zone_1_minutes FLOAT,
    hr_zone_2_minutes FLOAT,
    hr_zone_3_minutes FLOAT,
    hr_zone_4_minutes FLOAT,
    hr_zone_5_minutes FLOAT,
    avg_power INTEGER,
    max_power INTEGER,
    normalized_power INTEGER,
    avg_cadence INTEGER,
    max_cadence INTEGER,
    avg_pace VARCHAR(20),
    max_pace VARCHAR(20),
    elevation_gain FLOAT,
    elevation_loss FLOAT,
    calories INTEGER,
    aerobic_training_effect FLOAT,
    anaerobic_training_effect FLOAT,
    vo2max_estimate FLOAT,
    workout_name TEXT,
    perceived_effort INTEGER,
    notes TEXT,
    hours_since_previous FLOAT,
    days_since_previous FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activities_date ON activities(date);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_source ON activities(source);

-- Weekly Summary Table
CREATE TABLE IF NOT EXISTS weekly_summary (
    id BIGSERIAL PRIMARY KEY,
    week_start_date DATE NOT NULL UNIQUE,
    week_end_date DATE NOT NULL,
    avg_resting_hr FLOAT,
    avg_hrv FLOAT,
    avg_stress_score FLOAT,
    avg_body_battery FLOAT,
    avg_weight FLOAT,
    avg_sleep_hours FLOAT,
    avg_sleep_score FLOAT,
    zone2_sessions INTEGER,
    vo2max_sessions INTEGER,
    strength_sessions INTEGER,
    total_activities INTEGER,
    zone2_avg_hr FLOAT,
    zone2_total_minutes FLOAT,
    total_training_load INTEGER,
    avg_daily_steps INTEGER,
    longest_gap_days FLOAT,
    activity_streak_end INTEGER,
    days_with_activity INTEGER,
    missed_activity_days INTEGER,
    hit_zone2_target INTEGER,
    hit_strength_target INTEGER,
    hit_steps_target INTEGER,
    no_long_gaps INTEGER,
    perfect_week INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_weekly_summary_start_date ON weekly_summary(week_start_date);

-- Monthly Labs Table
CREATE TABLE IF NOT EXISTS monthly_labs (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    entry_type VARCHAR(50) NOT NULL,
    apob FLOAT,
    hba1c FLOAT,
    bp_systolic INTEGER,
    bp_diastolic INTEGER,
    vo2max FLOAT,
    body_fat_percent FLOAT,
    waist_circumference FLOAT,
    back_squat_1rm FLOAT,
    deadlift_1rm FLOAT,
    ohp_1rm FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_monthly_labs_date ON monthly_labs(date);

-- Food Log Table
CREATE TABLE IF NOT EXISTS food_log (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIMESTAMP,
    meal_type VARCHAR(50) NOT NULL,
    food_name TEXT NOT NULL,
    portion_size VARCHAR(100),
    calories INTEGER,
    protein_g FLOAT,
    carbs_g FLOAT,
    fat_g FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_food_log_date ON food_log(date);

-- Water Log Table
CREATE TABLE IF NOT EXISTS water_log (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIMESTAMP,
    amount_oz FLOAT NOT NULL,
    with_electrolytes BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_water_log_date ON water_log(date);

-- Daily Summaries Table (from garmin_sync.py)
CREATE TABLE IF NOT EXISTS daily_summaries (
    date DATE PRIMARY KEY,
    steps INTEGER,
    distance_meters FLOAT,
    calories INTEGER,
    active_minutes INTEGER,
    resting_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_stress INTEGER,
    body_battery_charged INTEGER,
    sleep_score INTEGER,
    deep_sleep_seconds INTEGER,
    light_sleep_seconds INTEGER,
    rem_sleep_seconds INTEGER,
    awake_seconds INTEGER,
    last_synced TIMESTAMP DEFAULT NOW()
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to tables that have it
CREATE TRIGGER update_daily_metrics_updated_at BEFORE UPDATE ON daily_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_weekly_summary_updated_at BEFORE UPDATE ON weekly_summary
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_monthly_labs_updated_at BEFORE UPDATE ON monthly_labs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_food_log_updated_at BEFORE UPDATE ON food_log
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_water_log_updated_at BEFORE UPDATE ON water_log
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - Important for Supabase
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_labs ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE water_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_summaries ENABLE ROW LEVEL SECURITY;

-- Create policies to allow service role access (for your Python scripts)
-- These policies allow your backend to read/write all data

CREATE POLICY "Enable all access for service role" ON daily_metrics
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON activities
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON weekly_summary
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON monthly_labs
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON food_log
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON water_log
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON daily_summaries
    FOR ALL USING (true);

-- Success message
SELECT 'Database schema created successfully!' as message;
