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
    'info': '#8B5CF6',
    'neutral': '#6B7280'
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

def get_activities_data(supabase: Client, days=90):
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

def get_daily_metrics(supabase: Client, days=90):
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

def main():
    # Header
    st.title("🏃 Dr. Longevity App")
    st.caption("Track your workouts and fitness progress")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        days = st.selectbox(
            "Time Range",
            options=[30, 60, 90, 180, 365],
            index=1,  # Default to 60 days
            format_func=lambda x: f"Last {x} days"
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

        if st.button("🔄 Refresh App", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

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

        # Calculate weekly average
        recent_activities = activities_df[activities_df['date'] >= datetime.now() - timedelta(days=28)]
        weekly_avg = len(recent_activities) / 4 if not recent_activities.empty else 0

        # Total stats
        total_duration = safe_int(activities_df['duration_minutes'].sum() if not activities_df.empty else 0)
        total_distance = safe_float(activities_df['distance_km'].sum() if not activities_df.empty else 0)

        # Key Metrics Section
        st.header("📊 Activity Summary")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Days Since Last Workout", f"{days_since_last}")

        with col2:
            st.metric("Current Streak", f"{current_streak} days")

        with col3:
            st.metric("Total Workouts", f"{total_activities}")

        with col4:
            st.metric("Weekly Average", f"{weekly_avg:.1f}")

        with col5:
            st.metric("Total Hours", f"{total_duration / 60:.0f}h")

        st.divider()

        # Activity Analysis
        st.header("📈 Activity Analysis")

        tab1, tab2, tab3 = st.tabs(["Workout History", "Training Patterns", "Performance"])

        with tab1:
            if not activities_df.empty:
                st.subheader("Recent Workouts")

                # Activity timeline
                fig_timeline = go.Figure()

                for activity_type in activities_df['activity_type'].unique():
                    data = activities_df[activities_df['activity_type'] == activity_type]
                    fig_timeline.add_trace(go.Scatter(
                        x=data['date'],
                        y=data['duration_minutes'],
                        mode='markers',
                        name=activity_type,
                        marker=dict(size=10),
                        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Duration: %{y} min<extra></extra>'
                    ))

                fig_timeline.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                    hovermode='closest',
                    xaxis_title="Date",
                    yaxis_title="Duration (minutes)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )

                st.plotly_chart(fig_timeline, use_container_width=True)

                # Recent activities table
                st.subheader("Workout Log")
                display_df = activities_df.head(10).copy()

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

                display_df['Duration'] = display_df['duration_minutes'].apply(format_duration)
                display_df['Distance'] = display_df['distance_km'].apply(lambda x: f"{safe_float(x)} km" if pd.notna(x) and x > 0 else "-")
                display_df['Avg HR'] = display_df['avg_hr'].apply(lambda x: f"{safe_int(x)} bpm" if pd.notna(x) else "-")
                display_df['Avg Power'] = display_df['avg_power'].apply(lambda x: f"{safe_int(x)} W" if pd.notna(x) else "-")
                display_df['Calories'] = display_df['calories'].apply(lambda x: safe_int(x))

                st.dataframe(
                    display_df[['date', 'activity_type', 'Duration', 'Distance', 'Avg HR', 'Avg Power', 'Calories']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No activities found in the selected time range.")

        with tab2:
            if not activities_df.empty:
                st.subheader("Activity Frequency")

                col1, col2 = st.columns(2)

                with col1:
                    # Activities by type
                    activity_counts = activities_df['activity_type'].value_counts()
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=activity_counts.index,
                        values=activity_counts.values,
                        hole=.4
                    )])
                    fig_pie.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                        title="Workouts by Type"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col2:
                    # Weekly volume
                    activities_df['week'] = activities_df['date'].dt.to_period('W').astype(str)
                    weekly_duration = activities_df.groupby('week')['duration_minutes'].sum().reset_index()
                    weekly_duration['hours'] = weekly_duration['duration_minutes'] / 60

                    fig_weekly = go.Figure(data=[go.Bar(
                        x=weekly_duration['week'],
                        y=weekly_duration['hours'],
                        marker_color=COLORS['primary']
                    )])
                    fig_weekly.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                        title="Weekly Training Volume",
                        xaxis_title="Week",
                        yaxis_title="Hours",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    )
                    st.plotly_chart(fig_weekly, use_container_width=True)

                # Activity metrics
                st.subheader("Training Metrics")
                col1, col2, col3 = st.columns(3)

                with col1:
                    avg_duration = activities_df['duration_minutes'].mean()
                    st.metric("Avg Workout Duration", f"{safe_int(avg_duration)} min")

                with col2:
                    avg_hr = activities_df['avg_hr'].mean()
                    st.metric("Avg Heart Rate", f"{safe_int(avg_hr)} bpm" if pd.notna(avg_hr) else "N/A")

                with col3:
                    total_cal = activities_df['calories'].sum()
                    st.metric("Total Calories", f"{safe_int(total_cal):,}")

        with tab3:
            if not activities_df.empty:
                st.subheader("Performance Trends")

                # Heart rate zones distribution
                activities_with_hr = activities_df[activities_df['avg_hr'].notna()]
                if not activities_with_hr.empty:
                    fig_hr = go.Figure()
                    fig_hr.add_trace(go.Scatter(
                        x=activities_with_hr['date'],
                        y=activities_with_hr['avg_hr'],
                        mode='lines+markers',
                        name='Avg HR',
                        line=dict(color=COLORS['secondary'], width=2),
                        marker=dict(size=6)
                    ))

                    fig_hr.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=20, b=20),
                        hovermode='x unified',
                        xaxis_title="",
                        yaxis_title="Heart Rate (bpm)",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    )

                    st.plotly_chart(fig_hr, use_container_width=True)

                # Power/Performance metrics
                activities_with_power = activities_df[activities_df['avg_power'].notna()]
                if not activities_with_power.empty:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        avg_power = activities_with_power['avg_power'].mean()
                        st.metric("Avg Power", f"{safe_int(avg_power)} W")

                    with col2:
                        max_power = activities_with_power['max_power'].max()
                        st.metric("Max Power", f"{safe_int(max_power)} W")

                    with col3:
                        total_dist = activities_df['distance_km'].sum()
                        st.metric("Total Distance", f"{safe_float(total_dist)} km")

        # Footer
        st.divider()
        latest_date = activities_df.iloc[0]['date'].strftime('%B %d, %Y') if not activities_df.empty else "N/A"
        st.caption(f"📊 Showing data from last {days} days | Last activity: {latest_date}")

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.caption("Please check your database and try again.")

if __name__ == "__main__":
    main()
