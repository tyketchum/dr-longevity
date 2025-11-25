import React, { useEffect, useState } from 'react';
import { getLabs, createLabEntry } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const Labs = () => {
  const [labs, setLabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    entry_type: 'lab',
    apob: '',
    hba1c: '',
    bp_systolic: '',
    bp_diastolic: '',
    vo2max: '',
    body_fat_percent: '',
    waist_circumference: '',
    back_squat_1rm: '',
    deadlift_1rm: '',
    ohp_1rm: '',
    notes: ''
  });

  useEffect(() => {
    fetchLabs();
  }, []);

  const fetchLabs = async () => {
    try {
      const response = await getLabs();
      setLabs(response.data);
    } catch (error) {
      console.error('Error fetching labs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Convert empty strings to null
      const data = { ...formData };
      Object.keys(data).forEach(key => {
        if (data[key] === '') data[key] = null;
        else if (key !== 'date' && key !== 'entry_type' && key !== 'notes') {
          data[key] = parseFloat(data[key]);
        }
      });

      await createLabEntry(data);
      setShowForm(false);
      fetchLabs();
      alert('Lab entry added!');

      // Reset form
      setFormData({
        date: new Date().toISOString().split('T')[0],
        entry_type: 'lab',
        apob: '',
        hba1c: '',
        bp_systolic: '',
        bp_diastolic: '',
        vo2max: '',
        body_fat_percent: '',
        waist_circumference: '',
        back_squat_1rm: '',
        deadlift_1rm: '',
        ohp_1rm: '',
        notes: ''
      });
    } catch (error) {
      alert('Error adding lab entry: ' + error.message);
    }
  };

  // Prepare data for charts
  const strengthData = labs
    .filter(l => l.back_squat_1rm || l.deadlift_1rm || l.ohp_1rm)
    .reverse();

  const labData = labs
    .filter(l => l.apob || l.hba1c)
    .reverse();

  if (loading) {
    return <div className="loading">Loading lab results...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Lab Results & Measurements</h1>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Entry'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2>Add Lab Entry</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div>
                <label>Date</label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  required
                />

                <label>Entry Type</label>
                <select
                  value={formData.entry_type}
                  onChange={(e) => setFormData({ ...formData, entry_type: e.target.value })}
                >
                  <option value="lab">Lab Results</option>
                  <option value="measurement">Body Measurement</option>
                  <option value="strength">Strength Test</option>
                </select>

                <label>ApoB (mg/dL) - Target: &lt;60</label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="e.g., 55"
                  value={formData.apob}
                  onChange={(e) => setFormData({ ...formData, apob: e.target.value })}
                />

                <label>HbA1c (%) - Target: &lt;5.2</label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="e.g., 5.0"
                  value={formData.hba1c}
                  onChange={(e) => setFormData({ ...formData, hba1c: e.target.value })}
                />

                <label>Blood Pressure (Systolic)</label>
                <input
                  type="number"
                  placeholder="e.g., 110"
                  value={formData.bp_systolic}
                  onChange={(e) => setFormData({ ...formData, bp_systolic: e.target.value })}
                />

                <label>Blood Pressure (Diastolic)</label>
                <input
                  type="number"
                  placeholder="e.g., 70"
                  value={formData.bp_diastolic}
                  onChange={(e) => setFormData({ ...formData, bp_diastolic: e.target.value })}
                />
              </div>

              <div>
                <label>VO2 Max (ml/kg/min)</label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="e.g., 50"
                  value={formData.vo2max}
                  onChange={(e) => setFormData({ ...formData, vo2max: e.target.value })}
                />

                <label>Body Fat %</label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="e.g., 15.5"
                  value={formData.body_fat_percent}
                  onChange={(e) => setFormData({ ...formData, body_fat_percent: e.target.value })}
                />

                <label>Waist Circumference (inches)</label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="e.g., 32"
                  value={formData.waist_circumference}
                  onChange={(e) => setFormData({ ...formData, waist_circumference: e.target.value })}
                />

                <label>Back Squat 1RM (lbs)</label>
                <input
                  type="number"
                  placeholder="e.g., 315"
                  value={formData.back_squat_1rm}
                  onChange={(e) => setFormData({ ...formData, back_squat_1rm: e.target.value })}
                />

                <label>Deadlift 1RM (lbs)</label>
                <input
                  type="number"
                  placeholder="e.g., 405"
                  value={formData.deadlift_1rm}
                  onChange={(e) => setFormData({ ...formData, deadlift_1rm: e.target.value })}
                />

                <label>Strict OHP 1RM (lbs)</label>
                <input
                  type="number"
                  placeholder="e.g., 185"
                  value={formData.ohp_1rm}
                  onChange={(e) => setFormData({ ...formData, ohp_1rm: e.target.value })}
                />
              </div>
            </div>

            <label>Notes</label>
            <textarea
              rows="2"
              placeholder="Any additional notes..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />

            <button type="submit">Add Entry</button>
          </form>
        </div>
      )}

      {/* Strength Progress Chart */}
      {strengthData.length > 0 && (
        <div className="card">
          <h2>Strength Progress (1RM)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={strengthData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                dataKey="date"
                stroke="#888"
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Line type="monotone" dataKey="back_squat_1rm" stroke="#00ff88" name="Back Squat" strokeWidth={2} />
              <Line type="monotone" dataKey="deadlift_1rm" stroke="#ffc107" name="Deadlift" strokeWidth={2} />
              <Line type="monotone" dataKey="ohp_1rm" stroke="#ff5252" name="Overhead Press" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Lab Results Table */}
      <div className="card">
        <h2>All Entries</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>ApoB</th>
              <th>HbA1c</th>
              <th>BP</th>
              <th>VO2 Max</th>
              <th>Body Fat %</th>
              <th>Waist</th>
              <th>Squat</th>
              <th>Deadlift</th>
              <th>OHP</th>
            </tr>
          </thead>
          <tbody>
            {labs.map((lab) => (
              <tr key={lab.id}>
                <td>{new Date(lab.date).toLocaleDateString()}</td>
                <td style={{ textTransform: 'capitalize' }}>{lab.entry_type}</td>
                <td style={{ color: lab.apob && lab.apob < 60 ? '#00ff88' : lab.apob ? '#ffc107' : '#888' }}>
                  {lab.apob || '--'}
                </td>
                <td style={{ color: lab.hba1c && lab.hba1c < 5.2 ? '#00ff88' : lab.hba1c ? '#ffc107' : '#888' }}>
                  {lab.hba1c || '--'}
                </td>
                <td>
                  {lab.bp_systolic && lab.bp_diastolic ? `${lab.bp_systolic}/${lab.bp_diastolic}` : '--'}
                </td>
                <td>{lab.vo2max || '--'}</td>
                <td>{lab.body_fat_percent || '--'}</td>
                <td>{lab.waist_circumference || '--'}</td>
                <td>{lab.back_squat_1rm || '--'}</td>
                <td>{lab.deadlift_1rm || '--'}</td>
                <td>{lab.ohp_1rm || '--'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Labs;
