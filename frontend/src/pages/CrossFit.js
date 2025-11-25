import React, { useEffect, useState } from 'react';
import { getActivities, createActivity } from '../services/api';

const CrossFit = () => {
  const [wods, setWods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    workout_name: '',
    duration_minutes: 60,
    notes: '',
    movements: [{ name: '', reps: '', weight: '' }]
  });

  useEffect(() => {
    fetchWods();
  }, []);

  const fetchWods = async () => {
    try {
      const response = await getActivities(90);
      // Filter for CrossFit workouts only
      const crossfitWods = response.data.filter(a => a.source === 'crossfit');
      setWods(crossfitWods);
    } catch (error) {
      console.error('Error fetching WODs:', error);
    } finally {
      setLoading(false);
    }
  };

  const addMovement = () => {
    setFormData({
      ...formData,
      movements: [...formData.movements, { name: '', reps: '', weight: '' }]
    });
  };

  const removeMovement = (index) => {
    const newMovements = formData.movements.filter((_, i) => i !== index);
    setFormData({ ...formData, movements: newMovements });
  };

  const updateMovement = (index, field, value) => {
    const newMovements = [...formData.movements];
    newMovements[index][field] = value;
    setFormData({ ...formData, movements: newMovements });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Format movements into notes
    const movementsText = formData.movements
      .filter(m => m.name)
      .map(m => {
        let text = `• ${m.name}`;
        if (m.reps) text += ` - ${m.reps} reps`;
        if (m.weight) text += ` @ ${m.weight} lbs`;
        return text;
      })
      .join('\n');

    const fullNotes = `${formData.notes}\n\nMovements:\n${movementsText}`;

    try {
      await createActivity({
        date: formData.date,
        source: 'crossfit',
        activity_type: 'crossfit',
        workout_name: formData.workout_name,
        duration_minutes: formData.duration_minutes,
        perceived_effort: 8,
        notes: fullNotes
      });

      setShowForm(false);
      fetchWods();
      alert('WOD logged! ✅');

      // Reset form
      setFormData({
        date: new Date().toISOString().split('T')[0],
        workout_name: '',
        duration_minutes: 60,
        notes: '',
        movements: [{ name: '', reps: '', weight: '' }]
      });
    } catch (error) {
      alert('Error logging WOD: ' + error.message);
    }
  };

  if (loading) {
    return <div className="loading">Loading WODs...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>CrossFit WODs 🏋️</h1>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Log WOD'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '2rem', background: 'rgba(102, 51, 255, 0.1)', borderColor: '#6633ff' }}>
          <h2>Log Today's WOD</h2>
          <form onSubmit={handleSubmit}>
            <label>Date</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />

            <label>WOD Name (optional)</label>
            <input
              type="text"
              placeholder="e.g., Murph, Fran, Cindy, etc."
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

            <label>Movements & Reps</label>
            {formData.movements.map((movement, index) => (
              <div key={index} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <input
                  type="text"
                  placeholder="Movement (e.g., Back Squat)"
                  value={movement.name}
                  onChange={(e) => updateMovement(index, 'name', e.target.value)}
                  style={{ marginBottom: 0 }}
                />
                <input
                  type="text"
                  placeholder="Reps"
                  value={movement.reps}
                  onChange={(e) => updateMovement(index, 'reps', e.target.value)}
                  style={{ marginBottom: 0 }}
                />
                <input
                  type="text"
                  placeholder="Weight (lbs)"
                  value={movement.weight}
                  onChange={(e) => updateMovement(index, 'weight', e.target.value)}
                  style={{ marginBottom: 0 }}
                />
                {index > 0 && (
                  <button
                    type="button"
                    onClick={() => removeMovement(index)}
                    style={{ padding: '0.5rem', background: '#ff5252' }}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button type="button" onClick={addMovement} style={{ marginBottom: '1rem', background: 'rgba(23, 229, 199, 0.2)', color: '#17e5c7' }}>
              + Add Movement
            </button>

            <label>Notes (optional)</label>
            <textarea
              rows="3"
              placeholder="How did it feel? PRs? Modifications?"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />

            <button type="submit">Log WOD</button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Past WODs ({wods.length} workouts)</h2>
        {wods.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏋️</div>
            <div>No WODs logged yet. Click "+ Log WOD" to get started!</div>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {wods.map((wod) => (
              <div key={wod.id} style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '1.5rem',
                borderRadius: '12px',
                borderLeft: '4px solid #17e5c7'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#17e5c7', marginBottom: '0.5rem' }}>
                      {wod.workout_name || 'CrossFit WOD'}
                    </div>
                    <div style={{ color: '#888', fontSize: '0.9rem' }}>
                      {new Date(wod.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{Math.round(wod.duration_minutes)} min</div>
                    <div style={{ color: '#888', fontSize: '0.85rem' }}>Duration</div>
                  </div>
                </div>

                {wod.notes && (
                  <div style={{
                    background: 'rgba(0, 0, 0, 0.2)',
                    padding: '1rem',
                    borderRadius: '8px',
                    whiteSpace: 'pre-wrap',
                    fontSize: '0.95rem',
                    lineHeight: '1.6'
                  }}>
                    {wod.notes}
                  </div>
                )}

                {wod.days_since_previous && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#888' }}>
                    Gap since previous: <span style={{ color: wod.days_since_previous <= 2 ? '#17e5c7' : '#ff5252', fontWeight: 600 }}>
                      {wod.days_since_previous.toFixed(1)} days
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CrossFit;
