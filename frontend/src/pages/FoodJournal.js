import React, { useEffect, useState } from 'react';
import { getFoodLog, logFood, getWaterLog, logWater } from '../services/api';

const FoodJournal = () => {
  const [foodEntries, setFoodEntries] = useState([]);
  const [waterEntries, setWaterEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showFoodForm, setShowFoodForm] = useState(false);
  const [customWaterAmount, setCustomWaterAmount] = useState('');
  const [withElectrolytes, setWithElectrolytes] = useState(false);
  const [foodForm, setFoodForm] = useState({
    date: new Date().toISOString().split('T')[0],
    meal_type: 'breakfast',
    food_name: '',
    portion_size: '',
    calories: '',
    protein_g: '',
    carbs_g: '',
    fat_g: '',
    notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [foodRes, waterRes] = await Promise.all([
        getFoodLog(7),
        getWaterLog(7)
      ]);
      setFoodEntries(foodRes.data);
      setWaterEntries(waterRes.data);
    } catch (error) {
      console.error('Error fetching food log:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFoodSubmit = async (e) => {
    e.preventDefault();
    try {
      // Only send non-empty fields
      const data = {
        date: foodForm.date,
        meal_type: foodForm.meal_type,
        food_name: foodForm.food_name,
        portion_size: foodForm.portion_size || null,
        calories: foodForm.calories ? parseInt(foodForm.calories) : null,
        protein_g: foodForm.protein_g ? parseFloat(foodForm.protein_g) : null,
        carbs_g: foodForm.carbs_g ? parseFloat(foodForm.carbs_g) : null,
        fat_g: foodForm.fat_g ? parseFloat(foodForm.fat_g) : null,
        notes: foodForm.notes || null
      };

      await logFood(data);
      setShowFoodForm(false);
      setFoodForm({
        date: new Date().toISOString().split('T')[0],
        meal_type: 'breakfast',
        food_name: '',
        portion_size: '',
        calories: '',
        protein_g: '',
        carbs_g: '',
        fat_g: '',
        notes: ''
      });
      fetchData();
    } catch (error) {
      alert('Error logging food: ' + error.message);
    }
  };

  const handleQuickWater = async (ounces) => {
    try {
      await logWater({
        date: new Date().toISOString().split('T')[0],
        amount_oz: ounces,
        with_electrolytes: withElectrolytes
      });
      fetchData();
    } catch (error) {
      alert('Error logging water: ' + error.message);
    }
  };

  const handleCustomWater = async (e) => {
    e.preventDefault();
    const amount = parseFloat(customWaterAmount);
    if (!amount || amount <= 0) {
      alert('Please enter a valid amount');
      return;
    }
    try {
      await logWater({
        date: new Date().toISOString().split('T')[0],
        amount_oz: amount,
        with_electrolytes: withElectrolytes
      });
      setCustomWaterAmount('');
      fetchData();
    } catch (error) {
      alert('Error logging water: ' + error.message);
    }
  };

  const getTodayWaterTotal = () => {
    const today = new Date().toISOString().split('T')[0];
    return waterEntries
      .filter(entry => entry.date === today)
      .reduce((sum, entry) => sum + entry.amount_oz, 0);
  };

  const groupEntriesByDate = () => {
    const grouped = {};
    foodEntries.forEach(entry => {
      if (!grouped[entry.date]) {
        grouped[entry.date] = {
          breakfast: [],
          lunch: [],
          dinner: [],
          snack: []
        };
      }
      grouped[entry.date][entry.meal_type].push(entry);
    });
    return grouped;
  };

  if (loading) {
    return <div className="loading">Loading food journal...</div>;
  }

  const groupedEntries = groupEntriesByDate();
  const dates = Object.keys(groupedEntries).sort().reverse();
  const todayWater = getTodayWaterTotal();

  return (
    <div className="container">
      <h1>Food Journal</h1>

      {/* Water Tracking */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2>💧 Water Intake</h2>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#17e5c7' }}>
              {todayWater} oz
            </div>
            <div style={{ fontSize: '0.9rem', opacity: 0.7 }}>
              Today's total ({(todayWater / 140 * 100).toFixed(0)}% of 140 oz goal)
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button onClick={() => handleQuickWater(8)} style={{ padding: '0.5rem 1rem' }}>
              + 8 oz
            </button>
            <button onClick={() => handleQuickWater(16)} style={{ padding: '0.5rem 1rem' }}>
              + 16 oz
            </button>
            <button onClick={() => handleQuickWater(32)} style={{ padding: '0.5rem 1rem' }}>
              + 32 oz
            </button>
            <button onClick={() => handleQuickWater(40)} style={{ padding: '0.5rem 1rem' }}>
              + 40 oz
            </button>
            <form onSubmit={handleCustomWater} style={{ display: 'flex', gap: '0.5rem', margin: 0 }}>
              <input
                type="number"
                step="0.1"
                placeholder="oz"
                value={customWaterAmount}
                onChange={(e) => setCustomWaterAmount(e.target.value)}
                style={{ width: '60px', padding: '0.5rem' }}
              />
              <button type="submit" style={{ padding: '0.5rem 1rem' }}>
                Add
              </button>
            </form>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
          <input
            type="checkbox"
            id="electrolytes"
            checked={withElectrolytes}
            onChange={(e) => setWithElectrolytes(e.target.checked)}
            style={{ width: '18px', height: '18px', cursor: 'pointer' }}
          />
          <label htmlFor="electrolytes" style={{ cursor: 'pointer', fontSize: '0.95rem' }}>
            ⚡ With electrolytes (prevents overhydration)
          </label>
        </div>
      </div>

      {/* Quick Food Entry */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Meals</h2>
        <button onClick={() => setShowFoodForm(!showFoodForm)}>
          {showFoodForm ? 'Cancel' : '+ Log Food'}
        </button>
      </div>

      {showFoodForm && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3>Quick Food Entry</h3>
          <form onSubmit={handleFoodSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label>Date</label>
                <input
                  type="date"
                  value={foodForm.date}
                  onChange={(e) => setFoodForm({ ...foodForm, date: e.target.value })}
                  required
                />
              </div>
              <div>
                <label>Meal</label>
                <select
                  value={foodForm.meal_type}
                  onChange={(e) => setFoodForm({ ...foodForm, meal_type: e.target.value })}
                  required
                >
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                </select>
              </div>
            </div>

            <label>Food / Meal Name *</label>
            <input
              type="text"
              placeholder="e.g., Oatmeal with berries, Chicken salad, etc."
              value={foodForm.food_name}
              onChange={(e) => setFoodForm({ ...foodForm, food_name: e.target.value })}
              required
            />

            <label>Portion Size (optional)</label>
            <input
              type="text"
              placeholder="e.g., 1 cup, 2 oz, 1 serving"
              value={foodForm.portion_size}
              onChange={(e) => setFoodForm({ ...foodForm, portion_size: e.target.value })}
            />

            <details style={{ marginTop: '1rem', marginBottom: '1rem' }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                📊 Optional: Add Macros
              </summary>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                <div>
                  <label>Calories</label>
                  <input
                    type="number"
                    placeholder="300"
                    value={foodForm.calories}
                    onChange={(e) => setFoodForm({ ...foodForm, calories: e.target.value })}
                  />
                </div>
                <div>
                  <label>Protein (g)</label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="20"
                    value={foodForm.protein_g}
                    onChange={(e) => setFoodForm({ ...foodForm, protein_g: e.target.value })}
                  />
                </div>
                <div>
                  <label>Carbs (g)</label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="40"
                    value={foodForm.carbs_g}
                    onChange={(e) => setFoodForm({ ...foodForm, carbs_g: e.target.value })}
                  />
                </div>
                <div>
                  <label>Fat (g)</label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="10"
                    value={foodForm.fat_g}
                    onChange={(e) => setFoodForm({ ...foodForm, fat_g: e.target.value })}
                  />
                </div>
              </div>
            </details>

            <label>Notes (optional)</label>
            <textarea
              rows="2"
              placeholder="Any additional details..."
              value={foodForm.notes}
              onChange={(e) => setFoodForm({ ...foodForm, notes: e.target.value })}
            />

            <button type="submit">Log Food</button>
          </form>
        </div>
      )}

      {/* Food Log */}
      {dates.length === 0 ? (
        <div className="card">
          <p style={{ textAlign: 'center', opacity: 0.7 }}>
            No food entries yet. Start logging your meals!
          </p>
        </div>
      ) : (
        dates.map(date => {
          const dayEntries = groupedEntries[date];
          const dayTotal = foodEntries
            .filter(e => e.date === date && e.calories)
            .reduce((sum, e) => sum + e.calories, 0);
          const dayProtein = foodEntries
            .filter(e => e.date === date && e.protein_g)
            .reduce((sum, e) => sum + e.protein_g, 0);

          return (
            <div key={date} className="card" style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3>{new Date(date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</h3>
                {dayTotal > 0 && (
                  <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                    {dayTotal} cal {dayProtein > 0 && `• ${Math.round(dayProtein)}g protein`}
                  </div>
                )}
              </div>

              {['breakfast', 'lunch', 'dinner', 'snack'].map(mealType => {
                if (dayEntries[mealType].length === 0) return null;
                return (
                  <div key={mealType} style={{ marginBottom: '1rem' }}>
                    <div style={{
                      fontWeight: 'bold',
                      textTransform: 'capitalize',
                      fontSize: '0.9rem',
                      opacity: 0.7,
                      marginBottom: '0.5rem'
                    }}>
                      {mealType}
                    </div>
                    {dayEntries[mealType].map(entry => (
                      <div
                        key={entry.id}
                        style={{
                          background: 'rgba(255, 255, 255, 0.03)',
                          padding: '0.75rem',
                          borderRadius: '8px',
                          marginBottom: '0.5rem',
                          borderLeft: '3px solid #6633ff'
                        }}
                      >
                        <div style={{ fontWeight: 'bold' }}>
                          {entry.food_name}
                          {entry.portion_size && <span style={{ opacity: 0.7, fontWeight: 'normal' }}> • {entry.portion_size}</span>}
                        </div>
                        {(entry.calories || entry.protein_g || entry.carbs_g || entry.fat_g) && (
                          <div style={{ fontSize: '0.85rem', opacity: 0.7, marginTop: '0.25rem' }}>
                            {entry.calories && `${entry.calories} cal`}
                            {entry.protein_g && ` • ${entry.protein_g}g P`}
                            {entry.carbs_g && ` • ${entry.carbs_g}g C`}
                            {entry.fat_g && ` • ${entry.fat_g}g F`}
                          </div>
                        )}
                        {entry.notes && (
                          <div style={{ fontSize: '0.85rem', opacity: 0.6, marginTop: '0.25rem', fontStyle: 'italic' }}>
                            {entry.notes}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          );
        })
      )}
    </div>
  );
};

export default FoodJournal;
