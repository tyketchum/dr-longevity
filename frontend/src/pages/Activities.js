import React, { useEffect, useState } from 'react';
import { getActivities, createActivity } from '../services/api';

const Activities = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    activity_type: 'strength',
    workout_name: '',
    duration_minutes: 60,
    perceived_effort: 7,
    notes: ''
  });

  useEffect(() => {
    fetchActivities();
  }, []);

  const fetchActivities = async () => {
    try {
      const response = await getActivities(90);
      setActivities(response.data);
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createActivity(formData);
      setShowForm(false);
      fetchActivities();
      alert('Activity added!');
    } catch (error) {
      alert('Error adding activity: ' + error.message);
    }
  };

  const getClassificationColor = (classification) => {
    switch (classification) {
      case 'zone2': return '#00ff88';
      case 'vo2max': return '#ff5252';
      case 'strength': return '#ffc107';
      default: return '#888';
    }
  };

  const getGapColor = (days) => {
    if (!days) return '#888';
    if (days < 1.5) return '#00ff88';
    if (days < 2) return '#ffc107';
    return '#ff5252';
  };

  if (loading) {
    return <div className="loading">Loading activities...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Activity Log</h1>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add CrossFit Workout'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2>Add CrossFit Workout</h2>
          <form onSubmit={handleSubmit}>
            <label>Date</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />

            <label>Workout Name (optional)</label>
            <input
              type="text"
              placeholder="e.g., Murph, Heavy DT, etc."
              value={formData.workout_name}
              onChange={(e) => setFormData({ ...formData, workout_name: e.target.value })}
            />

            <label>Duration (minutes)</label>
            <input
              type="number"
              value={formData.duration_minutes}
              onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
              required
            />

            <label>Perceived Effort (1-10)</label>
            <input
              type="number"
              min="1"
              max="10"
              value={formData.perceived_effort}
              onChange={(e) => setFormData({ ...formData, perceived_effort: parseInt(e.target.value) })}
            />

            <label>Notes (optional)</label>
            <textarea
              rows="3"
              placeholder="Movements, loads, PRs, etc."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />

            <button type="submit">Add Workout</button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Past 90 Days ({activities.length} activities)</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Duration</th>
              <th>Distance</th>
              <th>Avg Speed</th>
              <th>Avg HR</th>
              <th>Avg Power</th>
              <th>Elevation</th>
              <th>TSS</th>
              <th>Gap</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {activities.map((activity) => {
              const isCycling = activity.activity_type?.includes('cycling') || activity.activity_type?.includes('biking');
              const avgSpeed = activity.distance_km && activity.duration_minutes
                ? (activity.distance_km / (activity.duration_minutes / 60)).toFixed(1)
                : null;
              const tss = activity.aerobic_training_effect ? Math.round(activity.aerobic_training_effect * 30) : null;

              return (
                <tr key={activity.id}>
                  <td>{new Date(activity.date).toLocaleDateString()}</td>
                  <td>
                    {activity.workout_name || activity.activity_type}
                  </td>
                  <td>{Math.round(activity.duration_minutes)}min</td>
                  <td>{activity.distance_km ? `${activity.distance_km.toFixed(1)} km` : '--'}</td>
                  <td>{avgSpeed ? `${avgSpeed} km/h` : '--'}</td>
                  <td>{activity.avg_hr || '--'}</td>
                  <td>{activity.avg_power ? `${activity.avg_power}W` : '--'}</td>
                  <td>{activity.elevation_gain ? `${Math.round(activity.elevation_gain)}m` : '--'}</td>
                  <td>{tss || '--'}</td>
                  <td>
                    <span style={{ color: getGapColor(activity.days_since_previous) }}>
                      {activity.days_since_previous ? `${activity.days_since_previous.toFixed(1)}d` : '--'}
                    </span>
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>{activity.source}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Activities;
