import React, { useEffect, useState } from 'react';
import { getWeeklySummaries } from '../services/api';

const WeeklyLog = () => {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummaries();
  }, []);

  const fetchSummaries = async () => {
    try {
      const response = await getWeeklySummaries(12);
      setSummaries(response.data);
    } catch (error) {
      console.error('Error fetching summaries:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading weekly summaries...</div>;
  }

  return (
    <div className="container">
      <h1>Weekly Performance Log</h1>

      <div className="card">
        <h2>Past 12 Weeks</h2>
        <table>
          <thead>
            <tr>
              <th>Week</th>
              <th>RHR</th>
              <th>Zone 2</th>
              <th>Strength</th>
              <th>VO2 Max</th>
              <th>Total Activities</th>
              <th>Longest Gap</th>
              <th>Steps/Day</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {summaries.map((week) => {
              const isPerfect = week.perfect_week === 1;
              const hasLongGap = (week.longest_gap_days || 0) > 2;

              return (
                <tr
                  key={week.week_start}
                  style={{
                    background: isPerfect ? 'rgba(0, 255, 136, 0.1)' : hasLongGap ? 'rgba(255, 82, 82, 0.1)' : 'transparent'
                  }}
                >
                  <td>
                    {new Date(week.week_start).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </td>
                  <td>{week.avg_resting_hr ? Math.round(week.avg_resting_hr) : '--'}</td>
                  <td>
                    <span style={{ color: week.hit_zone2_target ? '#00ff88' : '#ff5252' }}>
                      {week.zone2_sessions}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: week.hit_strength_target ? '#00ff88' : '#ff5252' }}>
                      {week.strength_sessions}
                    </span>
                  </td>
                  <td>{week.vo2max_sessions}</td>
                  <td>{week.total_activities}</td>
                  <td>
                    <span style={{ color: hasLongGap ? '#ff5252' : '#00ff88' }}>
                      {week.longest_gap_days ? week.longest_gap_days.toFixed(1) : '--'}
                    </span>
                  </td>
                  <td>{week.avg_daily_steps ? week.avg_daily_steps.toLocaleString() : '--'}</td>
                  <td>
                    {isPerfect && <span style={{ color: '#00ff88' }}>✓ Perfect</span>}
                    {hasLongGap && <span style={{ color: '#ff5252' }}>⚠ Gap</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <div style={{ marginTop: '2rem', padding: '1rem', background: '#0a0a0a', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '1rem' }}>Targets</h3>
          <ul style={{ listStyle: 'none', lineHeight: '1.8' }}>
            <li><span style={{ color: '#00ff88' }}>✓</span> Zone 2: 3-4 sessions/week, 45-60min, HR 120-140</li>
            <li><span style={{ color: '#00ff88' }}>✓</span> Strength/CrossFit: 3 sessions/week</li>
            <li><span style={{ color: '#00ff88' }}>✓</span> VO2 Max: 1 session/week, HR &gt;170</li>
            <li><span style={{ color: '#00ff88' }}>✓</span> No gaps &gt;2 days between activities</li>
            <li><span style={{ color: '#00ff88' }}>✓</span> Steps: &gt;8,000/day average</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default WeeklyLog;
