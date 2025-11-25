import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import ActivityGapAlert from '../components/ActivityGapAlert';
import StreakCounter from '../components/StreakCounter';
import { getDailyMetrics, getWeeklySummaries, syncDaily, getTodayWater } from '../services/api';

const CommandCenter = () => {
  const [dailyMetrics, setDailyMetrics] = useState([]);
  const [weeklySummaries, setWeeklySummaries] = useState([]);
  const [todayMetrics, setTodayMetrics] = useState(null);
  const [todayWater, setTodayWater] = useState(0);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, summariesRes, waterRes] = await Promise.all([
        getDailyMetrics(90),
        getWeeklySummaries(12),
        getTodayWater()
      ]);

      setDailyMetrics(metricsRes.data.reverse()); // Oldest to newest for charts
      setWeeklySummaries(summariesRes.data.reverse());
      setTodayWater(waterRes.data.total_oz);

      // Get today's metrics (first in original response, since it was desc)
      if (metricsRes.data.length > 0) {
        setTodayMetrics(metricsRes.data[metricsRes.data.length - 1]);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncDaily();
      await fetchData();
      alert('Sync complete!');
    } catch (error) {
      alert('Sync failed: ' + error.message);
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  const getStatusColor = (value, target, inverse = false) => {
    if (!value) return '#888';
    if (inverse) {
      return value <= target ? '#00ff88' : '#ff5252';
    }
    return value >= target ? '#00ff88' : value >= target * 0.8 ? '#ffc107' : '#ff5252';
  };

  const getWaterColor = (amount) => {
    if (amount >= 130 && amount <= 150) return '#00ff88'; // Green
    if (amount >= 100) return '#ffc107'; // Yellow
    return '#ff5252'; // Red
  };

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Command Center</h1>
        <button onClick={handleSync} disabled={syncing}>
          {syncing ? 'Syncing...' : 'Sync Garmin'}
        </button>
      </div>

      {/* CRITICAL: Activity Gap Alert */}
      <ActivityGapAlert />

      {/* Streak Counter */}
      <StreakCounter />

      {/* Today's Metrics */}
      {todayMetrics && (
        <div className="card">
          <h2>Today's Metrics</h2>
          <div className="grid grid-3">
            <div className="metric">
              <div className="metric-value" style={{ color: getStatusColor(todayMetrics.resting_hr, 60, true) }}>
                {todayMetrics.resting_hr || '--'}
              </div>
              <div className="metric-label">Resting HR (bpm)</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Target: &lt;60
              </div>
            </div>

            <div className="metric">
              <div className="metric-value" style={{ color: getStatusColor(todayMetrics.stress_score, 25, true) }}>
                {todayMetrics.stress_score || '--'}
              </div>
              <div className="metric-label">Stress Score</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Target: &lt;25
              </div>
            </div>

            <div className="metric">
              <div className="metric-value" style={{ color: getWaterColor(todayWater) }}>
                {todayWater > 0 ? `${todayWater} oz` : '--'}
              </div>
              <div className="metric-label">💧 Water Intake</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                {todayWater > 0 ? `${Math.round(todayWater / 140 * 100)}% of 140 oz goal` : 'Target: 140 oz'}
              </div>
            </div>

            <div className="metric">
              <div className="metric-value">
                {todayMetrics.sleep_hours ? todayMetrics.sleep_hours.toFixed(1) : '--'}
              </div>
              <div className="metric-label">Sleep (hours)</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Score: {todayMetrics.sleep_score || '--'}
              </div>
            </div>

            <div className="metric">
              <div className="metric-value" style={{ color: getStatusColor(todayMetrics.steps, 8000) }}>
                {todayMetrics.steps ? todayMetrics.steps.toLocaleString() : '--'}
              </div>
              <div className="metric-label">Steps</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Target: &gt;8,000
              </div>
            </div>

            <div className="metric">
              <div className="metric-value">
                {todayMetrics.weight ? todayMetrics.weight.toFixed(1) : '--'}
              </div>
              <div className="metric-label">Weight (lbs)</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Target: 173-177
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Trend Charts */}
      <div className="card">
        <h2>Resting Heart Rate Trend (90 days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyMetrics}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="date"
              stroke="#888"
              tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis stroke="#888" domain={[50, 80]} />
            <Tooltip
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
            />
            <Line type="monotone" dataKey="resting_hr" stroke="#00ff88" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ textAlign: 'center', marginTop: '1rem', color: '#888', fontSize: '0.9rem' }}>
          Target: &lt;60 bpm (lower is better for longevity)
        </div>
      </div>

      <div className="card">
        <h2>Stress Score Trend</h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={dailyMetrics}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="date"
              stroke="#888"
              tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis stroke="#888" domain={[0, 100]} />
            <Tooltip
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
            />
            <Line type="monotone" dataKey="stress_score" stroke="#ff5252" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* This Week Summary */}
      {weeklySummaries.length > 0 && (
        <div className="card">
          <h2>This Week's Performance</h2>
          <div className="grid grid-3">
            <div className="metric">
              <div className="metric-value" style={{ color: weeklySummaries[weeklySummaries.length - 1].zone2_sessions >= 3 ? '#00ff88' : '#ff5252' }}>
                {weeklySummaries[weeklySummaries.length - 1].zone2_sessions}
              </div>
              <div className="metric-label">Zone 2 Sessions</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Target: 3-4/week
              </div>
            </div>

            <div className="metric">
              <div className="metric-value" style={{ color: weeklySummaries[weeklySummaries.length - 1].strength_sessions >= 3 ? '#00ff88' : '#ff5252' }}>
                {weeklySummaries[weeklySummaries.length - 1].strength_sessions}
              </div>
              <div className="metric-label">Strength Sessions</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Target: 3/week
              </div>
            </div>

            <div className="metric">
              <div className="metric-value" style={{ color: (weeklySummaries[weeklySummaries.length - 1].longest_gap_days || 0) <= 2 ? '#00ff88' : '#ff5252' }}>
                {(weeklySummaries[weeklySummaries.length - 1].longest_gap_days || 0).toFixed(1)}
              </div>
              <div className="metric-label">Longest Gap (days)</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Target: &lt;2 days
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommandCenter;
