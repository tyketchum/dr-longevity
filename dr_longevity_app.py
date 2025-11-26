"""
Dr. Longevity App
Track your workouts and fitness progress from Garmin Connect
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import json

# Optional: Anthropic for AI recommendations
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Dr. Longevity",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    h2 {
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Color palette
COLORS = {
    'primary': '#0066CC',
    'secondary': '#FF6B35',
    'success': '#059669',
    'warning': '#F59E0B',
    'danger': '#ef4444',
    'info': '#8B5CF6',
    'neutral': '#6B7280',
    'zone1': '#3b82f6',
    'zone2': '#10b981',
    'zone3': '#f59e0b',
    'zone4': '#f97316',
    'zone5': '#ef4444',
}

# Supabase connection
@st.cache_resource
def get_supabase_client():
    """Get Supabase client"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and 'supabase' in st.secrets:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
        else:
            # Fall back to environment variables
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')

        if not url or not key:
            st.error("❌ Missing Supabase credentials!")
            st.stop()

        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Error connecting to Supabase: {str(e)}")
        st.stop()

def get_activities_data(supabase: Client, days=1825):
    """Fetch activities data from Supabase"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        response = supabase.table('activities')\
            .select('*')\
            .gte('date', start_date.date())\
            .order('date', desc=True)\
            .execute()

        if response.data:
            df = pd.DataFrame(response.data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching activities: {str(e)}")
        return pd.DataFrame()

def get_daily_metrics(supabase: Client, days=1825):
    """Fetch daily metrics from Supabase"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        response = supabase.table('daily_metrics')\
            .select('*')\
            .gte('date', start_date.date())\
            .order('date', desc=True)\
            .execute()

        if response.data:
            df = pd.DataFrame(response.data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching daily metrics: {str(e)}")
        return pd.DataFrame()

def safe_int(value, default="N/A"):
    """Safely convert to int, handle NaN"""
    try:
        if pd.notna(value) and value is not None:
            return int(value)
        return default
    except:
        return default

def safe_float(value, decimals=1, default="N/A"):
    """Safely convert to float, handle NaN"""
    try:
        if pd.notna(value) and value is not None:
            return f"{float(value):.{decimals}f}"
        return default
    except:
        return default

def calculate_training_stress_metrics(metrics_df):
    """Calculate CTL, ATL, and TSB from training load data"""
    if metrics_df.empty or 'training_load' not in metrics_df.columns:
        return None

    # Sort by date ascending for proper calculation
    df = metrics_df.sort_values('date').copy()
    df['training_load'] = df['training_load'].fillna(0)

    # CTL (Chronic Training Load) - 42-day exponentially weighted average
    df['ctl'] = df['training_load'].ewm(span=42, adjust=False).mean()

    # ATL (Acute Training Load) - 7-day exponentially weighted average
    df['atl'] = df['training_load'].ewm(span=7, adjust=False).mean()

    # TSB (Training Stress Balance) = CTL - ATL
    # Positive TSB = Fresh, Negative TSB = Fatigued
    df['tsb'] = df['ctl'] - df['atl']

    return df.sort_values('date', ascending=False)

def estimate_ftp_from_activities(activities_df):
    """Get FTP - uses 216W from Garmin data"""
    # FTP from Garmin Connect
    # TODO: Pull this dynamically from Garmin API if available
    return 216

def get_power_zones(ftp):
    """Calculate power zones based on FTP"""
    if not ftp:
        return None

    return {
        'Active Recovery': (0, int(ftp * 0.55)),
        'Endurance': (int(ftp * 0.55), int(ftp * 0.75)),
        'Tempo': (int(ftp * 0.75), int(ftp * 0.90)),
        'Threshold': (int(ftp * 0.90), int(ftp * 1.05)),
        'VO2 Max': (int(ftp * 1.05), int(ftp * 1.20)),
        'Anaerobic': (int(ftp * 1.20), int(ftp * 1.50))
    }

def calculate_power_zone_distribution(activities_df, ftp):
    """Calculate time spent in each power zone"""
    if activities_df.empty or not ftp:
        return None

    cycling_df = activities_df[
        (activities_df['activity_type'].str.contains('cycling|biking', case=False, na=False, regex=True)) &
        (activities_df['avg_power'].notna())
    ].copy()

    if cycling_df.empty:
        return None

    zones = get_power_zones(ftp)
    zone_times = {zone: 0 for zone in zones.keys()}

    for _, activity in cycling_df.iterrows():
        power = activity['avg_power']
        duration = activity['duration_minutes']

        for zone_name, (low, high) in zones.items():
            if low <= power < high:
                zone_times[zone_name] += duration
                break

    return zone_times

def calculate_hr_zone_distribution(activities_df):
    """Calculate time spent in each HR zone from activities data"""
    if activities_df.empty:
        return None

    # Sum up time in each HR zone across all activities
    zone_cols = ['hr_zone_1_minutes', 'hr_zone_2_minutes', 'hr_zone_3_minutes',
                 'hr_zone_4_minutes', 'hr_zone_5_minutes']

    zone_times = {}
    for i, col in enumerate(zone_cols, 1):
        if col in activities_df.columns:
            total_time = activities_df[col].sum()
            if pd.notna(total_time):
                zone_times[f'Zone {i}'] = total_time

    return zone_times if zone_times else None

def analyze_polarized_training(zone_times):
    """Analyze if training follows 80/20 polarized model"""
    if not zone_times:
        return None

    # Polarized training: 80% in zones 1-2 (easy), 20% in zones 4-5 (hard), minimal zone 3
    total_time = sum(zone_times.values())
    if total_time == 0:
        return None

    easy = zone_times.get('Zone 1', 0) + zone_times.get('Zone 2', 0)
    moderate = zone_times.get('Zone 3', 0)
    hard = zone_times.get('Zone 4', 0) + zone_times.get('Zone 5', 0)

    return {
        'easy_pct': (easy / total_time) * 100,
        'moderate_pct': (moderate / total_time) * 100,
        'hard_pct': (hard / total_time) * 100,
        'total_time': total_time,
        'is_polarized': (easy / total_time) >= 0.75 and (hard / total_time) >= 0.15
    }

def get_recovery_recommendation(tsb, hrv, avg_hrv):
    """Generate smart recovery recommendations based on TSB and HRV"""
    recommendations = []

    # TSB-based recommendations
    if tsb is not None and pd.notna(tsb):
        if tsb > 10:
            recommendations.append("✅ **Fresh & Ready**: Great time for hard workouts or testing FTP")
        elif tsb > -10:
            recommendations.append("⚖️ **Balanced**: Maintain current training load")
        elif tsb > -30:
            recommendations.append("⚠️ **Fatigued**: Consider reducing volume or intensity")
        else:
            recommendations.append("🔴 **Very Fatigued**: Recovery week strongly recommended")

    # HRV-based recommendations
    if hrv is not None and avg_hrv is not None and pd.notna(hrv) and pd.notna(avg_hrv):
        hrv_ratio = hrv / avg_hrv
        if hrv_ratio > 1.1:
            recommendations.append("💚 **HRV High**: Body is well-recovered")
        elif hrv_ratio > 0.9:
            recommendations.append("💛 **HRV Normal**: Recovery adequate")
        else:
            recommendations.append("❤️ **HRV Low**: Extra recovery needed")

    if not recommendations:
        recommendations.append("📊 Need more data for personalized recommendations")

    return recommendations

def create_sparkline(data, color='#3b82f6', dates=None, unit=''):
    """Create a mini sparkline chart for KPIs with minimal date labels"""
    if data is None or len(data) < 2:
        return None

    # Format hover text with dates if available
    hover_text = []
    if dates and len(dates) == len(data):
        for i, (date, value) in enumerate(zip(dates, data)):
            date_str = date.strftime('%b %d, %Y') if hasattr(date, 'strftime') else str(date)
            hover_text.append(f"{date_str}<br>{value}{unit}")
    else:
        hover_text = [f"{value}{unit}" for value in data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
        hovertemplate='%{text}<extra></extra>',
        text=hover_text
    ))

    # Add minimal date labels if dates provided
    if dates and len(dates) >= 2:
        # Format dates as short strings (MMM 'YY)
        start_date = dates[0].strftime('%b %y') if hasattr(dates[0], 'strftime') else str(dates[0])[:7]
        end_date = dates[-1].strftime('%b %y') if hasattr(dates[-1], 'strftime') else str(dates[-1])[:7]

        # Add subtle date annotations at start and end
        fig.add_annotation(
            x=0, y=data[0],
            text=start_date,
            showarrow=False,
            font=dict(size=9, color='#9ca3af'),
            xanchor='left',
            yanchor='bottom',
            yshift=5
        )
        fig.add_annotation(
            x=len(data)-1, y=data[-1],
            text=end_date,
            showarrow=False,
            font=dict(size=9, color='#9ca3af'),
            xanchor='right',
            yanchor='bottom',
            yshift=5
        )

    fig.update_layout(
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

def get_ftp_rating(watts_per_kg):
    """Get FTP rating based on W/kg for males"""
    if watts_per_kg > 5.04:
        return "Superior", "#10b981"
    elif watts_per_kg >= 3.93:
        return "Excellent", "#3b82f6"
    elif watts_per_kg >= 2.79:
        return "Good", "#059669"
    elif watts_per_kg >= 2.23:
        return "Fair", "#f59e0b"
    else:
        return "Untrained", "#ef4444"

def get_vo2max_rating(vo2max, age=35):
    """Get VO2 Max rating based on value (for males)"""
    # These are general categories, can be adjusted by age
    if vo2max > 56:
        return "Superior", "#10b981"
    elif vo2max >= 51:
        return "Excellent", "#3b82f6"
    elif vo2max >= 43:
        return "Good", "#059669"
    elif vo2max >= 35:
        return "Fair", "#f59e0b"
    else:
        return "Poor", "#ef4444"

def main():
    # Header
    st.title("🚴 Dr. Longevity")
    st.caption("Track your workouts and fitness progress")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        days = st.selectbox(
            "Time Range",
            options=[30, 60, 90, 180, 365, 730, 1825],
            index=6,  # Default to 1825 days (5 years / all time)
            format_func=lambda x: f"Last {x} days" if x < 1825 else "All Time (5 years)"
        )

        st.subheader("🎯 Goals")
        target_ftp_wkg = st.number_input(
            "Target FTP (W/kg)",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help="Set your target FTP in watts per kilogram"
        )

        st.divider()

        if st.button("📥 Sync Garmin Data", use_container_width=True, type="primary"):
            with st.spinner("Syncing data from Garmin Connect..."):
                try:
                    import subprocess
                    result = subprocess.run(
                        ["python3", "dr_longevity_sync.py"],
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(__file__) or '.'
                    )
                    if result.returncode == 0:
                        st.success("✅ Sync complete! Refreshing app...")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Sync failed: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error running sync: {str(e)}")

        if st.button("🔄 Refresh Data", use_container_width=True, help="Clear cache and fetch latest data from database"):
            st.cache_data.clear()
            st.rerun()

        # Tech Stack Explanation
        st.divider()
        with st.expander("🛠️ Tech Stack & Architecture"):
            st.markdown("""
            **Streamlit Standalone vs Snowflake**

            This app uses **Standalone Streamlit** (open-source Python framework):
            - ✅ Self-hosted on any infrastructure (local, cloud, serverless)
            - ✅ Full control over dependencies, data sources, and deployment
            - ✅ Free and open-source - no vendor lock-in
            - ✅ Deploy anywhere: AWS, GCP, Azure, Vercel, or locally

            **Snowflake Streamlit** (Streamlit in Snowflake):
            - Native app framework inside Snowflake workspaces
            - Tightly coupled to Snowflake data warehouse
            - Managed hosting within Snowflake environment
            - Great for Snowflake-centric workflows but less flexible

            **Our Stack**:
            - **Frontend**: Streamlit (Python) - UI components & visualization
            - **Backend**: Python with Garmin Connect API integration
            - **Database**: Supabase (PostgreSQL) - open-source Firebase alternative
            - **Deployment**: Streamlit Community Cloud (free tier)
            - **Automation**: GitHub Actions for daily data sync
            - **Viz Libraries**: Plotly (interactive charts), Folium (maps)

            **Why Standalone Streamlit?**
            - Flexibility to use any database (not just Snowflake)
            - Cost-effective (free hosting options)
            - Modern Python ecosystem (pandas, plotly, etc.)
            - Easy CI/CD with GitHub Actions
            - Perfect for personal/small team dashboards
            """)


        st.divider()

        st.caption("**About**")
        st.caption("Track your workouts, training patterns, and fitness progress over time.")

    # Get Supabase client
    supabase = get_supabase_client()

    # Load data
    try:
        activities_df = get_activities_data(supabase, days)
        metrics_df = get_daily_metrics(supabase, days)

        if activities_df.empty and metrics_df.empty:
            st.warning("📊 No data available. Please sync your Garmin data.")
            return

        # Calculate key stats
        total_activities = len(activities_df)
        days_since_last = safe_int(metrics_df.iloc[0]['days_since_last_activity'] if not metrics_df.empty else None, 0)
        current_streak = safe_int(metrics_df.iloc[0]['current_streak'] if not metrics_df.empty else None, 0)

        # Calculate weekly average (last 28 days)
        recent_activities = activities_df[activities_df['date'] >= datetime.now() - timedelta(days=28)]
        weekly_avg = len(recent_activities) / 4 if not recent_activities.empty else 0

        # Calculate year-over-year metrics
        current_year = datetime.now().year
        last_year = current_year - 1

        current_year_start = datetime(current_year, 1, 1)
        last_year_start = datetime(last_year, 1, 1)
        last_year_end = datetime(last_year, 12, 31, 23, 59, 59)

        # This year's activities
        this_year_activities = activities_df[activities_df['date'] >= current_year_start]
        this_year_count = len(this_year_activities)
        this_year_hours = this_year_activities['duration_minutes'].sum() / 60 if not this_year_activities.empty else 0

        # Last year's activities
        last_year_activities = activities_df[(activities_df['date'] >= last_year_start) & (activities_df['date'] <= last_year_end)]
        last_year_count = len(last_year_activities)
        last_year_hours = last_year_activities['duration_minutes'].sum() / 60 if not last_year_activities.empty else 0

        # Calculate year-over-year deltas
        yoy_count_delta = this_year_count - last_year_count
        yoy_hours_delta = this_year_hours - last_year_hours

        # Total stats (all time)
        total_duration = safe_int(activities_df['duration_minutes'].sum() if not activities_df.empty else 0)
        total_distance = safe_float(activities_df['distance_km'].sum() if not activities_df.empty else 0)

        # Calculate training metrics for later use
        stress_metrics_df = calculate_training_stress_metrics(metrics_df)
        current_tsb = stress_metrics_df.iloc[0]['tsb'] if stress_metrics_df is not None else None
        current_ctl = stress_metrics_df.iloc[0]['ctl'] if stress_metrics_df is not None else None
        current_atl = stress_metrics_df.iloc[0]['atl'] if stress_metrics_df is not None else None
        ftp = estimate_ftp_from_activities(activities_df)
        vo2max_values = activities_df[activities_df['vo2max_estimate'].notna()]['vo2max_estimate']
        current_vo2max = vo2max_values.iloc[0] if len(vo2max_values) > 0 else None
        current_hrv = metrics_df.iloc[0]['hrv'] if not metrics_df.empty and 'hrv' in metrics_df.columns else None
        avg_hrv = metrics_df['hrv'].mean() if not metrics_df.empty and 'hrv' in metrics_df.columns else None
        hr_zones = calculate_hr_zone_distribution(activities_df)
        polarized_analysis = analyze_polarized_training(hr_zones)

        # Get weight for W/kg calculation
        # Try to pull from database first, fallback to hardcoded value
        current_weight_kg = 79.4  # Default fallback

        if not metrics_df.empty and 'weight' in metrics_df.columns:
            # Get most recent weight from daily metrics
            weight_kg = metrics_df.iloc[0]['weight']
            if pd.notna(weight_kg) and weight_kg > 0:
                current_weight_kg = float(weight_kg)
                print(f"Using weight from database: {current_weight_kg} kg")

        # ===== PRIMARY KPIs WITH TRENDS =====
        st.header("⚡ Performance KPIs")

        col1, col2 = st.columns(2)

        with col1:
            if ftp:
                # Get FTP trend (last 90 days of cycling activities)
                # Match any cycling/biking activity type
                cycling_activities = activities_df[activities_df['activity_type'].str.contains('cycling|biking', case=False, na=False, regex=True)]
                if not cycling_activities.empty and 'avg_power' in cycling_activities.columns:
                    # Calculate rolling FTP estimates over time
                    ftp_history = cycling_activities[cycling_activities['avg_power'].notna()].copy()
                    ftp_history = ftp_history.sort_values('date')
                    ftp_history['estimated_ftp'] = (ftp_history['avg_power'] * 0.95).astype(int)

                    # Show sparkline if we have data (even just 1 point)
                    if len(ftp_history) >= 1:
                        ftp_trend_data = ftp_history['estimated_ftp'].tail(10).tolist()
                        ftp_trend_dates = ftp_history['date'].tail(10).tolist()

                        # Calculate FTP delta based on sparkline data (first vs last)
                        ftp_delta = None
                        if len(ftp_trend_data) >= 2:
                            delta_value = ftp_trend_data[-1] - ftp_trend_data[0]
                            ftp_delta = f"+{delta_value}W" if delta_value > 0 else f"{delta_value}W"

                        st.metric(
                            "FTP",
                            f"{ftp}W",
                            delta=ftp_delta,
                            help="📊 Calculation: Max(Avg Power × 0.95) from recent cycling activities | Why: FTP represents the power you can sustain for ~1 hour. We estimate it from your ride average power. The sparkline shows how your power output (and estimated FTP) varies across rides over time."
                        )

                        if len(ftp_trend_data) >= 2:
                            fig = create_sparkline(ftp_trend_data, COLORS['primary'], dates=ftp_trend_dates, unit='W')
                            if fig:
                                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.caption(f"📊 {len(ftp_trend_data)} data point - need 2+ for trend")
                    else:
                        st.metric("FTP", f"{ftp}W", help="Functional Threshold Power")
                else:
                    st.metric("FTP", f"{ftp}W", help="Functional Threshold Power")

                # Show W/kg and rating if weight available
                if current_weight_kg:
                    watts_per_kg = ftp / current_weight_kg
                    rating, color = get_ftp_rating(watts_per_kg)
                    st.markdown(f"**{watts_per_kg:.2f} W/kg** • <span style='color:{color};font-weight:600'>{rating}</span>", unsafe_allow_html=True)
                    st.caption("📊 Calculation: FTP ÷ Body Weight | Why: W/kg normalizes power for body weight - key metric for climbing and comparing riders. Updates automatically when weight changes in Garmin.")

                    # Show progress toward target FTP
                    if target_ftp_wkg and target_ftp_wkg > 0:
                        target_watts = int(target_ftp_wkg * current_weight_kg)
                        watts_to_goal = target_watts - ftp
                        progress = (watts_per_kg / target_ftp_wkg) * 100

                        if watts_to_goal > 0:
                            st.caption(f"🎯 Goal: **{target_ftp_wkg:.1f} W/kg** ({target_watts}W) • **+{watts_to_goal}W** to go ({progress:.1f}%)")
                        else:
                            st.caption(f"🎯 Goal: **{target_ftp_wkg:.1f} W/kg** ({target_watts}W) • ✅ **Goal achieved!**")
                else:
                    st.caption("Weight data needed for W/kg rating")
            else:
                st.metric("FTP", "N/A", help="Need cycling power data")

        with col2:
            if current_vo2max:
                # Get VO2 max trend over time
                vo2_history = activities_df[activities_df['vo2max_estimate'].notna()].copy()
                vo2_history = vo2_history.sort_values('date')

                # Display as whole number
                vo2max_int = int(round(current_vo2max))

                # Show sparkline if we have data
                if len(vo2_history) >= 1:
                    vo2_trend_data = vo2_history['vo2max_estimate'].tail(10).tolist()
                    vo2_trend_dates = vo2_history['date'].tail(10).tolist()

                    # Calculate VO2 max delta based on sparkline data (first vs last)
                    vo2_delta = None
                    if len(vo2_trend_data) >= 2:
                        delta_val = vo2_trend_data[-1] - vo2_trend_data[0]
                        vo2_delta = f"+{int(round(delta_val))}" if delta_val > 0 else f"{int(round(delta_val))}"

                    st.metric(
                        "VO2 Max",
                        f"{vo2max_int}",
                        delta=vo2_delta,
                        help="📊 Calculation: Garmin estimates VO2 Max from heart rate, pace, and activity data | Why: VO2 Max measures your body's ability to use oxygen during exercise - higher is better. It's the gold standard for cardiovascular fitness. The sparkline shows your last 10 VO2 Max estimates over time."
                    )

                    if len(vo2_trend_data) >= 2:
                        fig = create_sparkline(vo2_trend_data, COLORS['secondary'], dates=vo2_trend_dates, unit=' ml/kg/min')
                        if fig:
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.caption(f"📊 {len(vo2_trend_data)} data point - need 2+ for trend")
                else:
                    st.metric("VO2 Max", f"{vo2max_int}", help="Cardio fitness estimate (ml/kg/min)")

                # Show rating
                rating, color = get_vo2max_rating(vo2max_int)
                st.markdown(f"<span style='color:{color};font-weight:600;font-size:1.1rem'>{rating}</span>", unsafe_allow_html=True)
            else:
                st.metric("VO2 Max", "N/A", help="Need activities with VO2 max estimates")

        st.caption("📈 Sparkline trends show last 10 activities • Ratings based on age/gender standards")
        st.divider()

        # AI-Powered Training Recommendations
        if ANTHROPIC_AVAILABLE:
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

            if anthropic_api_key and (ftp or current_vo2max):
                with st.expander("🤖 AI Training Recommendations", expanded=False):
                    st.markdown("**Get personalized recommendations to improve your metrics**")

                    if st.button("Generate Recommendations", use_container_width=True):
                        with st.spinner("Analyzing your training data..."):
                            try:
                                client = Anthropic(api_key=anthropic_api_key)

                                # Prepare training data for AI analysis
                                analysis_data = {
                                    "ftp": ftp if ftp else None,
                                    "watts_per_kg": watts_per_kg if ftp and current_weight_kg else None,
                                    "vo2_max": current_vo2max if current_vo2max else None,
                                    "recent_workouts": len(activities_df[activities_df['date'] >= (datetime.now() - timedelta(days=30))]),
                                    "total_workouts": len(activities_df),
                                    "avg_weekly_workouts": len(activities_df) / ((activities_df['date'].max() - activities_df['date'].min()).days / 7) if len(activities_df) > 0 else 0,
                                    "ftp_trend": ftp_delta if ftp and len(ftp_trend_data) >= 2 else "No trend data",
                                    "vo2_trend": vo2_delta if current_vo2max and len(vo2_trend_data) >= 2 else "No trend data"
                                }

                                # Build prompt
                                prompt = f"""You are an expert cycling coach and sports scientist. Analyze this athlete's current fitness metrics and provide specific, actionable recommendations to improve their FTP and VO2 Max.

Current Metrics:
- FTP: {analysis_data['ftp']}W ({analysis_data['watts_per_kg']:.2f} W/kg) - Trend: {analysis_data['ftp_trend']}
- VO2 Max: {analysis_data['vo2_max']} ml/kg/min - Trend: {analysis_data['vo2_trend']}
- Recent Training: {analysis_data['recent_workouts']} workouts in last 30 days
- Average: {analysis_data['avg_weekly_workouts']:.1f} workouts per week

Provide 3-5 specific, actionable recommendations to improve these metrics. For each recommendation:
1. State the specific training intervention (e.g., "Add 2x weekly 20-min threshold intervals")
2. Explain WHY it will help (physiological adaptation)
3. Provide specific implementation details (duration, intensity, frequency)

Focus on evidence-based interventions that are proven to improve FTP and VO2 Max. Keep recommendations practical and achievable."""

                                # Call Claude API
                                response = client.messages.create(
                                    model="claude-3-5-sonnet-20241022",
                                    max_tokens=1500,
                                    messages=[{"role": "user", "content": prompt}]
                                )

                                # Display recommendations
                                st.markdown("---")
                                st.markdown(response.content[0].text)
                                st.markdown("---")
                                st.caption("💡 Generated by Claude AI • Always consult with a coach or medical professional before major training changes")

                            except Exception as e:
                                st.error(f"Error generating recommendations: {str(e)}")
            elif not anthropic_api_key:
                with st.expander("🤖 AI Training Recommendations"):
                    st.info("💡 **Want personalized AI-powered training recommendations?**\n\nAdd your Anthropic API key to `.env`:\n```\nANTHROPIC_API_KEY=your_key_here\n```\n\nGet a key at: https://console.anthropic.com/")

        st.divider()

        # Monthly Summary
        st.header("📅 Monthly Summary")

        # Calculate monthly stats
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Current month activities
        current_month_activities = activities_df[activities_df['date'] >= current_month_start]
        current_month_count = len(current_month_activities)
        current_month_hours = current_month_activities['duration_minutes'].sum() / 60 if not current_month_activities.empty else 0

        # Last month activities
        last_month_activities = activities_df[(activities_df['date'] >= last_month_start) & (activities_df['date'] < current_month_start)]
        last_month_count = len(last_month_activities)
        last_month_hours = last_month_activities['duration_minutes'].sum() / 60 if not last_month_activities.empty else 0

        # Calculate deltas
        count_delta = current_month_count - last_month_count
        hours_delta = current_month_hours - last_month_hours

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "This Month: Workouts",
                current_month_count,
                delta=f"{count_delta:+d} vs last month" if last_month_count > 0 else None,
                help=f"Current: {current_month_count} | Last month: {last_month_count}"
            )

        with col2:
            st.metric(
                "This Month: Hours",
                f"{current_month_hours:.1f}h",
                delta=f"{hours_delta:+.1f}h vs last month" if last_month_hours > 0 else None,
                help=f"Current: {current_month_hours:.1f}h | Last month: {last_month_hours:.1f}h"
            )

        st.divider()

        # Activity Summary (Secondary Metrics)
        st.header("📊 Activity Summary")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            # Days since last workout - context about consistency
            context_emoji = "🔥" if days_since_last == 0 else "✅" if days_since_last <= 2 else "⚠️" if days_since_last <= 7 else "❌"
            st.metric(
                "Days Since Last Workout",
                f"{days_since_last}",
                help=f"{context_emoji} 0-2 days: Excellent | 3-7 days: Good | 7+ days: Consider getting back on the bike!"
            )

        with col2:
            # Current streak - context about momentum
            streak_status = "🔥 On fire!" if current_streak >= 7 else "💪 Building momentum" if current_streak >= 3 else "👍 Keep going"
            st.metric(
                "Current Streak",
                f"{current_streak} days",
                help=f"{streak_status} | Best practice: 3-4 workouts per week"
            )

        with col3:
            # This year workouts - year-over-year comparison
            st.metric(
                f"{current_year} Workouts",
                this_year_count,
                delta=f"{yoy_count_delta:+d} vs {last_year}" if last_year_count > 0 else None,
                help=f"This year: {this_year_count} | Last year: {last_year_count} | Goal: Maintain or increase volume"
            )

        with col4:
            # Weekly average - context about training frequency
            freq_status = "🎯 Optimal" if weekly_avg >= 3 else "📈 Room to grow" if weekly_avg >= 1 else "🚨 Too infrequent"
            st.metric(
                "Weekly Average (4wks)",
                f"{weekly_avg:.1f}",
                help=f"{freq_status} | Optimal: 3-5 workouts/week | Your current: {weekly_avg:.1f}/week"
            )

        with col5:
            # This year hours - year-over-year comparison
            st.metric(
                f"{current_year} Hours",
                f"{this_year_hours:.0f}h",
                delta=f"{yoy_hours_delta:+.0f}h vs {last_year}" if last_year_hours > 0 else None,
                help=f"This year: {this_year_hours:.0f}h | Last year: {last_year_hours:.0f}h | All-time: {total_duration / 60:.0f}h"
            )

        st.divider()

        # ===== RECENT WORKOUTS (Prominent Display) =====
        st.header("🏋️ Recent Workouts")

        if not activities_df.empty:
            # Recent activities table
            display_df = activities_df.head(15).copy()

            # Format duration as hours and minutes
            def format_duration(minutes):
                if pd.notna(minutes) and minutes > 0:
                    mins = int(minutes)
                    if mins >= 60:
                        hours = mins // 60
                        remaining_mins = mins % 60
                        return f"{hours}h {remaining_mins}m"
                    else:
                        return f"{mins}m"
                return "-"

            display_df['Date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df['Workout'] = display_df['workout_name'].apply(lambda x: str(x) if pd.notna(x) else "-")
            display_df['Duration'] = display_df['duration_minutes'].apply(format_duration)
            display_df['Distance'] = display_df['distance_km'].apply(lambda x: f"{float(x) * 0.621371:.1f} mi" if pd.notna(x) and x > 0 else "-")
            display_df['Avg HR'] = display_df['avg_hr'].apply(lambda x: f"{safe_int(x)} bpm" if pd.notna(x) else "-")
            display_df['Avg Power'] = display_df['avg_power'].apply(lambda x: f"{safe_int(x)} W" if pd.notna(x) else "-")
            display_df['Calories'] = display_df['calories'].apply(lambda x: safe_int(x))

            st.dataframe(
                display_df[['Date', 'Workout', 'activity_type', 'Duration', 'Distance', 'Avg HR', 'Avg Power', 'Calories']],
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("No activities found in the selected time range.")

        st.divider()
        # Cycling Routes Section
        st.divider()
        st.header("🗺️ Cycling Routes")

        # Check for GPS data (split into multiple files to stay under GitHub's 100MB limit)
        routes = []
        part_num = 1
        while True:
            gps_file = f'cycling_routes_part{part_num}.json' if part_num > 0 else 'cycling_routes.json'
            if os.path.exists(gps_file):
                try:
                    with open(gps_file, 'r') as f:
                        part_routes = json.load(f)
                        routes.extend(part_routes)
                    part_num += 1
                except Exception:
                    break
            else:
                break

        if routes:
            try:

                if routes and len(routes) > 0:
                    # Create heatmap
                    st.subheader("Route Heatmap")

                    # Get all coordinates and downsample for performance
                    all_coords = []
                    for route in routes:
                        all_coords.extend(route['coordinates'])

                    if all_coords:
                        # Downsample GPS points for faster rendering (take every 10th point)
                        # This reduces 1.5M points to ~150K while preserving route patterns
                        sample_rate = 10
                        sampled_coords = all_coords[::sample_rate]

                        st.info(f"⏳ Rendering heatmap with {len(sampled_coords):,} GPS points (sampled from {len(all_coords):,} total points)...")

                        # Analyze riding locations
                        from collections import defaultdict
                        location_stats = defaultdict(lambda: {'road': 0, 'gravel': 0, 'mtb': 0, 'other': 0, 'total_distance': 0})

                        for route in routes:
                            name = route.get('name', '')
                            distance = route.get('distance_km', 0)

                            # Extract location
                            location = name.split(' Road Cycling')[0].split(' Gravel')[0].split(' Cycling')[0].split(' Mountain')[0]

                            # Determine ride type
                            if 'Road Cycling' in name or 'Road Biking' in name:
                                ride_type = 'road'
                            elif 'Gravel' in name or 'Unpaved' in name:
                                ride_type = 'gravel'
                            elif 'Mountain' in name:
                                ride_type = 'mtb'
                            else:
                                ride_type = 'other'

                            location_stats[location][ride_type] += 1
                            location_stats[location]['total_distance'] += distance

                        # Create two columns: map and stats
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            # Create map centered on average location
                            avg_lat = sum(coord[0] for coord in sampled_coords) / len(sampled_coords)
                            avg_lon = sum(coord[1] for coord in sampled_coords) / len(sampled_coords)

                            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

                            # Add heatmap layer with optimized parameters
                            HeatMap(sampled_coords, radius=15, blur=25, max_zoom=13).add_to(m)

                            # Display map
                            folium_static(m, width=700, height=600)

                            st.caption(f"📍 Showing {len(routes)} routes • Sampled {len(sampled_coords):,} of {len(all_coords):,} GPS points")

                        with col2:
                            st.markdown("### 🗺️ Riding Zones")

                            # Sort locations by total rides
                            sorted_locs = sorted(
                                location_stats.items(),
                                key=lambda x: sum([x[1]['road'], x[1]['gravel'], x[1]['mtb'], x[1]['other']]),
                                reverse=True
                            )[:6]  # Top 6

                            # Fun emoji mapping
                            def get_zone_emoji(location, stats):
                                if 'Fort Worth' in location:
                                    return '🪨' if stats['gravel'] > stats['road'] else '🏙️'
                                elif 'North Richland Hills' in location:
                                    return '🏡'
                                elif 'Stillwater' in location:
                                    return '🌾'
                                elif 'Boulder' in location:
                                    return '🏔️'
                                elif 'Keller' in location:
                                    return '🛣️'
                                elif 'Bartlesville' in location:
                                    return '🌳'
                                return '🚴'

                            def get_ride_style(stats):
                                if stats['gravel'] > stats['road']:
                                    return "Gravel Hunter"
                                elif stats['road'] > stats['gravel']:
                                    return "Pavement Surfer"
                                return "Mixed Terrain"

                            # Compact table display
                            for location, stats in sorted_locs:
                                total_rides = sum([stats['road'], stats['gravel'], stats['mtb'], stats['other']])
                                emoji = get_zone_emoji(location, stats)
                                style = get_ride_style(stats)
                                total_miles = stats['total_distance'] * 0.621371  # km to miles

                                # Shorten location name if needed
                                display_loc = location.replace('Fort Worth -', 'FW').replace('North Richland Hills', 'NRH')

                                st.markdown(f"""
                                <div style='padding: 8px 0; border-bottom: 1px solid #333;'>
                                    <div style='font-size: 14px; font-weight: 600;'>{emoji} {display_loc}</div>
                                    <div style='font-size: 12px; color: #888; margin-top: 2px;'>{style} • {total_rides} rides • {total_miles:.0f}mi</div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("GPS data fetched but no coordinates available")
                else:
                    # No GPS data - show explanation
                    st.info("""
                    **🚴 GPS Route Data Not Available**

                    To load GPS route data from your Garmin Edge 1040 Solar rides:

                    Run: `python3 fetch_gps_routes.py`

                    This will download GPX files from Garmin Connect for all outdoor cycling activities
                    and create a heatmap of your routes.

                    **Note:** Peloton rides don't have GPS data (indoor workouts).
                    """)

                    # Show location breakdown from activity names
                    cycling_activities = activities_df[activities_df['activity_type'].str.contains('cycling|biking', case=False, na=False, regex=True)]
                    if not cycling_activities.empty and 'name' in cycling_activities.columns:
                        location_counts = {}
                        for name in cycling_activities['name']:
                            if 'North Richland Hills' in str(name):
                                location_counts['North Richland Hills'] = location_counts.get('North Richland Hills', 0) + 1
                            elif 'Boulder' in str(name):
                                location_counts['Boulder'] = location_counts.get('Boulder', 0) + 1
                            elif 'Cycling' in str(name) or 'Road Biking' in str(name):
                                location_counts['Other'] = location_counts.get('Other', 0) + 1

                        if location_counts:
                            st.subheader("Ride Locations")
                            cols = st.columns(len(location_counts))
                            for i, (location, count) in enumerate(location_counts.items()):
                                with cols[i]:
                                    st.metric(location, count)

            except Exception as e:
                st.error(f"Error loading route data: {e}")
        else:
            st.info("""
            **🚴 GPS Route Data Not Available**

            To load GPS route data from your Garmin Edge 1040 Solar rides:

            Run: `python3 fetch_gps_routes.py`

            This will download GPX files from Garmin Connect for all outdoor cycling activities.
            """)

        # Activity Analysis Tabs
        st.header("📊 Detailed Analysis")

        tab1, tab2, tab3, tab4 = st.tabs(["Power Zones", "HR Zones", "Polarized Training", "Nutrition"])

        # ===== POWER ZONES TAB =====
        with tab1:
            st.subheader("Power Zone Distribution")

            if ftp:
                zones = get_power_zones(ftp)

                # Display zone ranges
                st.markdown("### Training Zones")
                zone_colors = ['#3b82f6', '#10b981', '#f59e0b', '#f97316', '#ef4444', '#dc2626']

                cols = st.columns(3)
                for idx, (zone_name, (low, high)) in enumerate(zones.items()):
                    with cols[idx % 3]:
                        st.markdown(f"**{zone_name}**")
                        st.markdown(f"`{low}-{high}W` ({int(low/ftp*100)}-{int(high/ftp*100)}% FTP)")

                # Calculate and display time in zones
                zone_times = calculate_power_zone_distribution(activities_df, ftp)
                if zone_times:
                    st.markdown("### Time in Each Zone")

                    # Create horizontal bar chart
                    zone_names = list(zone_times.keys())
                    zone_hours = [zone_times[z] / 60 for z in zone_names]

                    fig_power_zones = go.Figure(go.Bar(
                        x=zone_hours,
                        y=zone_names,
                        orientation='h',
                        marker_color=zone_colors[:len(zone_names)],
                        text=[f"{h:.1f}h" for h in zone_hours],
                        textposition='auto',
                    ))

                    fig_power_zones.update_layout(
                        height=400,
                        margin=dict(l=20, r=20, t=20, b=20),
                        xaxis_title="Hours",
                        yaxis_title="",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e8eaed')
                    )

                    st.plotly_chart(fig_power_zones, use_container_width=True)

                    # Show percentages
                    total_hours = sum(zone_hours)
                    if total_hours > 0:
                        st.markdown("### Zone Distribution")
                        for zone, hours in zip(zone_names, zone_hours):
                            pct = (hours / total_hours) * 100
                            st.progress(pct / 100, text=f"**{zone}**: {pct:.1f}%")
                else:
                    st.info("No power data available for zone analysis")
            else:
                st.info("FTP not available. Need cycling activities with power data to calculate zones.")

        # ===== HR ZONES TAB =====
        with tab2:
            st.subheader("Heart Rate Zone Distribution")

            if hr_zones:
                st.markdown("### Time in Each HR Zone")

                zone_names = list(hr_zones.keys())
                zone_hours = [hr_zones[z] / 60 for z in zone_names]
                hr_zone_colors = [COLORS['zone1'], COLORS['zone2'], COLORS['zone3'], COLORS['zone4'], COLORS['zone5']]

                # Create horizontal bar chart
                fig_hr_zones = go.Figure(go.Bar(
                    x=zone_hours,
                    y=zone_names,
                    orientation='h',
                    marker_color=hr_zone_colors[:len(zone_names)],
                    text=[f"{h:.1f}h" for h in zone_hours],
                    textposition='auto',
                ))

                fig_hr_zones.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis_title="Hours",
                    yaxis_title="",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e8eaed')
                )

                st.plotly_chart(fig_hr_zones, use_container_width=True)

                # Zone descriptions
                st.markdown("### Zone Descriptions")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Zone 1**: Recovery (50-60% max HR)")
                    st.markdown("**Zone 2**: Endurance (60-70% max HR)")
                    st.markdown("**Zone 3**: Tempo (70-80% max HR)")

                with col2:
                    st.markdown("**Zone 4**: Threshold (80-90% max HR)")
                    st.markdown("**Zone 5**: VO2 Max (90-100% max HR)")

                # Show percentages
                total_hours = sum(zone_hours)
                if total_hours > 0:
                    st.markdown("### Zone Distribution")
                    for zone, hours in zip(zone_names, zone_hours):
                        pct = (hours / total_hours) * 100
                        st.progress(pct / 100, text=f"**{zone}**: {pct:.1f}%")
            else:
                st.info("No heart rate zone data available")

        # ===== POLARIZED TRAINING TAB =====
        with tab3:
            st.subheader("Polarized Training Analysis (80/20 Rule)")

            if polarized_analysis:
                st.markdown("""
                ### What is Polarized Training?

                The **80/20 Rule** suggests that elite endurance athletes spend approximately:
                - **80%** of training time at low intensity (Zone 1-2)
                - **20%** at high intensity (Zone 4-5)
                - Minimal time in the "gray zone" (Zone 3)

                This approach maximizes aerobic development while allowing adequate recovery for high-quality hard sessions.
                """)

                # Create pie chart
                fig_polarized = go.Figure(data=[go.Pie(
                    labels=['Easy (Z1-2)', 'Moderate (Z3)', 'Hard (Z4-5)'],
                    values=[polarized_analysis['easy_pct'], polarized_analysis['moderate_pct'], polarized_analysis['hard_pct']],
                    marker_colors=[COLORS['secondary'], COLORS['warning'], COLORS['danger']],
                    hole=0.4,
                    textinfo='label+percent',
                    textfont=dict(size=14, color='white')
                )])

                fig_polarized.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e8eaed')
                )

                st.plotly_chart(fig_polarized, use_container_width=True)

                # Analysis
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Easy Intensity", f"{polarized_analysis['easy_pct']:.1f}%",
                             help="Zone 1-2: Target 75-80%")

                with col2:
                    st.metric("Moderate Intensity", f"{polarized_analysis['moderate_pct']:.1f}%",
                             help="Zone 3: Keep minimal")

                with col3:
                    st.metric("Hard Intensity", f"{polarized_analysis['hard_pct']:.1f}%",
                             help="Zone 4-5: Target 15-20%")

                # Recommendations
                st.markdown("### Your Training Distribution")
                if polarized_analysis['is_polarized']:
                    st.success("✅ **Excellent!** Your training follows the polarized model. Keep it up!")
                else:
                    st.warning("⚠️ **Not Optimal**: Your training isn't polarized. Here's how to adjust:")
                    if polarized_analysis['easy_pct'] < 75:
                        st.markdown("- 🐌 **Do more easy workouts**: Slow down your easy days to Zone 1-2")
                    if polarized_analysis['moderate_pct'] > 15:
                        st.markdown("- ⚠️ **Avoid the gray zone**: Zone 3 is too hard to recover from but not hard enough for adaptation")
                    if polarized_analysis['hard_pct'] < 15:
                        st.markdown("- 🚀 **Add intensity**: Include 1-2 hard interval sessions per week")

                st.markdown(f"**Total training time analyzed**: {polarized_analysis['total_time'] / 60:.1f} hours")
            else:
                st.info("Need heart rate zone data to perform polarized training analysis")

        # ===== NUTRITION TAB =====
        with tab4:
            st.subheader("Nutrition Tracking")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🍎 Food Log")
                with st.form("food_log_form"):
                    food_date = st.date_input("Date", datetime.now())
                    food_time = st.time_input("Time", datetime.now().time())
                    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
                    food_name = st.text_input("Food Name")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        calories = st.number_input("Calories", min_value=0, step=10)
                        protein = st.number_input("Protein (g)", min_value=0.0, step=0.5)
                    with col_b:
                        carbs = st.number_input("Carbs (g)", min_value=0.0, step=0.5)
                        fat = st.number_input("Fat (g)", min_value=0.0, step=0.5)
                    notes = st.text_area("Notes")

                    if st.form_submit_button("Log Food"):
                        try:
                            supabase = get_supabase_client()
                            data = {
                                'date': str(food_date),
                                'time': f"{food_date} {food_time}",
                                'meal_type': meal_type,
                                'food_name': food_name,
                                'calories': calories,
                                'protein_g': protein,
                                'carbs_g': carbs,
                                'fat_g': fat,
                                'notes': notes
                            }
                            supabase.table('food_log').insert(data).execute()
                            st.success("✅ Food logged successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error logging food: {str(e)}")

            with col2:
                st.markdown("### 💧 Water Log")
                with st.form("water_log_form"):
                    water_date = st.date_input("Date", datetime.now(), key="water_date")
                    water_time = st.time_input("Time", datetime.now().time(), key="water_time")
                    amount_oz = st.number_input("Amount (oz)", min_value=0.0, step=1.0, value=8.0)
                    with_electrolytes = st.checkbox("With Electrolytes")

                    if st.form_submit_button("Log Water"):
                        try:
                            supabase = get_supabase_client()
                            data = {
                                'date': str(water_date),
                                'time': f"{water_date} {water_time}",
                                'amount_oz': amount_oz,
                                'with_electrolytes': with_electrolytes
                            }
                            supabase.table('water_log').insert(data).execute()
                            st.success("✅ Water logged successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error logging water: {str(e)}")

            # Display recent logs
            st.divider()
            st.subheader("Recent Logs")

            try:
                supabase = get_supabase_client()

                col_a, col_b = st.columns(2)

                with col_a:
                    food_logs = supabase.table('food_log').select('*').order('date', desc=True).limit(10).execute()
                    if food_logs.data:
                        st.markdown("**Recent Food**")
                        food_df = pd.DataFrame(food_logs.data)
                        st.dataframe(food_df[['date', 'meal_type', 'food_name', 'calories']], use_container_width=True, hide_index=True)
                    else:
                        st.info("No food logs yet")

                with col_b:
                    water_logs = supabase.table('water_log').select('*').order('date', desc=True).limit(10).execute()
                    if water_logs.data:
                        st.markdown("**Recent Water**")
                        water_df = pd.DataFrame(water_logs.data)
                        st.dataframe(water_df[['date', 'amount_oz', 'with_electrolytes']], use_container_width=True, hide_index=True)
                    else:
                        st.info("No water logs yet")
            except:
                st.info("Start logging to see your nutrition history!")


        # Footer
        st.divider()
        latest_date = activities_df.iloc[0]['date'].strftime('%B %d, %Y') if not activities_df.empty else "N/A"
        st.caption(f"📊 Showing data from last {days} days | Last activity: {latest_date}")

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.caption("Please check your database and try again.")

if __name__ == "__main__":
    main()
