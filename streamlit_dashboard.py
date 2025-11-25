"""
Longevity Dashboard - Streamlit Edition
A simple, beautiful dashboard for tracking health metrics from Garmin
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Longevity Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better design
st.markdown("""
<style>
    /* Clean, modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }

    /* Better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Card-like sections */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    /* Clean headers */
    h1 {
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    h2 {
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    h3 {
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Color palette (color-blind friendly)
COLORS = {
    'primary': '#0066CC',      # Blue
    'secondary': '#FF6B35',    # Orange
    'success': '#059669',      # Green
    'warning': '#F59E0B',      # Amber
    'info': '#8B5CF6',         # Purple
    'neutral': '#6B7280'       # Gray
}

# Database connection
@st.cache_resource
def get_database_connection():
    """Get database connection with caching"""
    # Use relative path that works both locally and in cloud
    db_path = Path(__file__).parent / "longevity_dashboard.db"
    return sqlite3.connect(db_path, check_same_thread=False)

def get_data(days=30):
    """Fetch data from database"""
    conn = get_database_connection()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Get daily metrics
    metrics_query = """
    SELECT
        dm.date,
        dm.steps,
        dm.resting_hr as resting_heart_rate,
        dm.stress_score as avg_stress,
        dm.body_battery,
        dm.sleep_score,
        dm.sleep_deep_hours * 3600 as deep_sleep_seconds,
        dm.sleep_light_hours * 3600 as light_sleep_seconds,
        dm.sleep_rem_hours * 3600 as rem_sleep_seconds,
        dm.sleep_awake_hours * 3600 as awake_seconds,
        dm.intensity_minutes as active_minutes,
        dm.hrv,
        dm.training_load
    FROM daily_metrics dm
    WHERE dm.date >= ?
    ORDER BY dm.date DESC
    """

    df_metrics = pd.read_sql_query(metrics_query, conn, params=(start_date.date(),))

    # Get aggregated activity data per day
    activities_query = """
    SELECT
        date,
        SUM(distance_km) * 1000 as distance_meters,
        SUM(calories) as calories,
        MAX(max_hr) as max_heart_rate,
        AVG(avg_hr) as avg_heart_rate
    FROM activities
    WHERE date >= ?
    GROUP BY date
    """

    df_activities = pd.read_sql_query(activities_query, conn, params=(start_date.date(),))

    # Merge the dataframes
    df = pd.merge(df_metrics, df_activities, on='date', how='left')
    df['date'] = pd.to_datetime(df['date'])

    # Fill NaN values for days without activities
    df['distance_meters'] = df['distance_meters'].fillna(0)
    df['calories'] = df['calories'].fillna(0)
    df['max_heart_rate'] = df['max_heart_rate'].fillna(0)

    return df

def format_duration(seconds):
    """Format seconds into human-readable duration"""
    if pd.isna(seconds):
        return "N/A"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create a styled metric display"""
    return st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def main():
    # Header
    st.title("🏃 Longevity Dashboard")
    st.caption("Track your health metrics from Garmin Connect")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Date range selector
        days = st.selectbox(
            "Time Range",
            options=[7, 14, 30, 60, 90],
            index=2,  # Default to 30 days
            format_func=lambda x: f"Last {x} days"
        )

        st.divider()

        # Sync Garmin data button
        if st.button("📥 Sync Garmin Data", use_container_width=True, type="primary"):
            with st.spinner("Syncing data from Garmin Connect..."):
                try:
                    import subprocess
                    result = subprocess.run(
                        ["python3", "garmin_sync.py"],
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent
                    )
                    if result.returncode == 0:
                        st.success("✅ Sync complete! Refreshing dashboard...")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Sync failed: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error running sync: {str(e)}")

        # Refresh data button
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # Info section
        st.caption("**About**")
        st.caption("This dashboard displays your health and fitness metrics from Garmin Connect, helping you track your wellness journey.")
        st.caption("")
        st.caption("💡 **Tip**: Click 'Sync Garmin Data' to fetch the latest data from your Garmin account.")

    # Load data
    try:
        df = get_data(days)

        if df.empty:
            st.warning("📊 No data available. Please sync your Garmin data first.")
            return

        # Latest values (most recent day)
        latest = df.iloc[0]

        # Key Metrics Section
        st.header("📊 Today's Snapshot")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            steps_val = f"{int(latest['steps']):,}" if pd.notna(latest['steps']) else "N/A"
            steps_pct = ((latest['steps'] - df['steps'].mean()) / df['steps'].mean() * 100) if pd.notna(latest['steps']) else None
            create_metric_card(
                "Steps",
                steps_val,
                delta=f"{steps_pct:+.0f}% vs avg" if steps_pct else None
            )

        with col2:
            sleep_total = (latest['deep_sleep_seconds'] + latest['light_sleep_seconds'] +
                          latest['rem_sleep_seconds']) / 3600
            sleep_val = f"{sleep_total:.1f}h" if sleep_total > 0 else "N/A"
            create_metric_card(
                "Sleep",
                sleep_val,
                delta=f"{int(latest['sleep_score'])} score" if pd.notna(latest['sleep_score']) else None
            )

        with col3:
            rhr_val = f"{int(latest['resting_heart_rate'])} bpm" if pd.notna(latest['resting_heart_rate']) else "N/A"
            create_metric_card(
                "Resting HR",
                rhr_val
            )

        with col4:
            bb_val = f"{int(latest['body_battery'])}" if pd.notna(latest['body_battery']) else "N/A"
            create_metric_card(
                "Body Battery",
                bb_val
            )

        st.divider()

        # Trends Section
        st.header("📈 Trends")

        tab1, tab2, tab3, tab4 = st.tabs(["Activity", "Heart Health", "Sleep", "Recovery"])

        with tab1:
            # Activity trends
            st.subheader("Daily Steps")

            fig_steps = go.Figure()
            fig_steps.add_trace(go.Scatter(
                x=df['date'],
                y=df['steps'],
                mode='lines+markers',
                name='Steps',
                line=dict(color=COLORS['primary'], width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor=f"rgba(0, 102, 204, 0.1)"
            ))

            # Add goal line at 10,000 steps
            fig_steps.add_hline(
                y=10000,
                line_dash="dash",
                line_color=COLORS['neutral'],
                annotation_text="Goal: 10,000",
                annotation_position="right"
            )

            fig_steps.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode='x unified',
                showlegend=False,
                xaxis_title="",
                yaxis_title="Steps",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )

            st.plotly_chart(fig_steps, use_container_width=True)

            # Additional activity metrics
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Average Steps",
                    f"{int(df['steps'].mean()):,}",
                    delta=f"{int(df['steps'].std())} std dev"
                )

            with col2:
                st.metric(
                    "Active Minutes/Day",
                    f"{int(df['active_minutes'].mean())} min",
                    delta=f"{int(df['active_minutes'].max())} max"
                )

        with tab2:
            # Heart health trends
            st.subheader("Resting Heart Rate")

            fig_hr = go.Figure()
            fig_hr.add_trace(go.Scatter(
                x=df['date'],
                y=df['resting_heart_rate'],
                mode='lines+markers',
                name='Resting HR',
                line=dict(color=COLORS['secondary'], width=2),
                marker=dict(size=6)
            ))

            fig_hr.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode='x unified',
                showlegend=False,
                xaxis_title="",
                yaxis_title="BPM",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )

            st.plotly_chart(fig_hr, use_container_width=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Avg Resting HR", f"{int(df['resting_heart_rate'].mean())} bpm")

            with col2:
                st.metric("Avg Stress", f"{int(df['avg_stress'].mean())}")

            with col3:
                st.metric("Avg Max HR", f"{int(df['max_heart_rate'].mean())} bpm")

        with tab3:
            # Sleep analysis
            st.subheader("Sleep Duration")

            # Calculate total sleep in hours
            df_sleep = df.copy()
            df_sleep['total_sleep_hours'] = (
                df_sleep['deep_sleep_seconds'] +
                df_sleep['light_sleep_seconds'] +
                df_sleep['rem_sleep_seconds']
            ) / 3600

            fig_sleep = go.Figure()
            fig_sleep.add_trace(go.Bar(
                x=df_sleep['date'],
                y=df_sleep['total_sleep_hours'],
                name='Sleep',
                marker_color=COLORS['info']
            ))

            # Add goal line at 8 hours
            fig_sleep.add_hline(
                y=8,
                line_dash="dash",
                line_color=COLORS['neutral'],
                annotation_text="Goal: 8h",
                annotation_position="right"
            )

            fig_sleep.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode='x unified',
                showlegend=False,
                xaxis_title="",
                yaxis_title="Hours",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )

            st.plotly_chart(fig_sleep, use_container_width=True)

            # Sleep stage breakdown
            st.subheader("Sleep Stages (Average)")

            avg_deep = df['deep_sleep_seconds'].mean() / 60
            avg_light = df['light_sleep_seconds'].mean() / 60
            avg_rem = df['rem_sleep_seconds'].mean() / 60

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Deep Sleep", f"{int(avg_deep)} min")

            with col2:
                st.metric("Light Sleep", f"{int(avg_light)} min")

            with col3:
                st.metric("REM Sleep", f"{int(avg_rem)} min")

        with tab4:
            # Recovery metrics
            st.subheader("Body Battery & Recovery")

            fig_battery = go.Figure()
            fig_battery.add_trace(go.Scatter(
                x=df['date'],
                y=df['body_battery'],
                mode='lines+markers',
                name='Body Battery',
                line=dict(color=COLORS['success'], width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor=f"rgba(5, 150, 105, 0.1)"
            ))

            fig_battery.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode='x unified',
                showlegend=False,
                xaxis_title="",
                yaxis_title="Body Battery",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )

            st.plotly_chart(fig_battery, use_container_width=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Avg Body Battery",
                    f"{int(df['body_battery'].mean())}"
                )

            with col2:
                st.metric(
                    "Avg Sleep Score",
                    f"{int(df['sleep_score'].mean())}"
                )

            with col3:
                if 'hrv' in df.columns and df['hrv'].notna().any():
                    st.metric(
                        "Avg HRV",
                        f"{int(df['hrv'].mean())}"
                    )

        # Footer
        st.divider()
        st.caption(f"📊 Showing data from last {days} days | Last updated: {latest['date'].strftime('%B %d, %Y')}")

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.caption("Please check your database connection and try again.")

if __name__ == "__main__":
    main()
