import React, { useEffect, useState } from 'react';
import { getCalendar } from '../services/api';

const Calendar = () => {
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [calendarData, setCalendarData] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState(null);

  useEffect(() => {
    fetchCalendar();
  }, [year, month]);

  const fetchCalendar = async () => {
    try {
      const response = await getCalendar(year, month);
      setCalendarData(response.data);
    } catch (error) {
      console.error('Error fetching calendar:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (year, month) => {
    return new Date(year, month, 0).getDate();
  };

  const getFirstDayOfMonth = (year, month) => {
    return new Date(year, month - 1, 1).getDay();
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    const days = [];

    // Empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day day-empty"></div>);
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const hasActivity = calendarData[dateStr] && calendarData[dateStr].length > 0;
      const activities = calendarData[dateStr] || [];

      // Determine day class based on activity
      let dayClass = 'day-empty';
      if (hasActivity) {
        dayClass = 'day-active';
      }

      // Get unique activity types for this day
      const activityTypes = hasActivity
        ? [...new Set(activities.map(a => a.type.split('_')[0]))]
        : [];

      days.push(
        <div
          key={day}
          className={`calendar-day ${dayClass}`}
          onClick={() => hasActivity && setSelectedDay({ date: dateStr, activities })}
          style={{ cursor: hasActivity ? 'pointer' : 'default', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
        >
          <div style={{ fontWeight: 600, fontSize: '1.1rem', marginBottom: '8px' }}>{day}</div>
          {hasActivity && (
            <div style={{ fontSize: '0.65rem', opacity: 0.8, textAlign: 'center' }}>
              <div style={{ marginBottom: '2px' }}>
                {activities.length} {activities.length === 1 ? 'workout' : 'workouts'}
              </div>
              <div style={{ fontSize: '0.6rem', opacity: 0.7 }}>
                {activityTypes.slice(0, 2).join(', ')}
              </div>
            </div>
          )}
        </div>
      );
    }

    return days;
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const changeMonth = (delta) => {
    let newMonth = month + delta;
    let newYear = year;

    if (newMonth > 12) {
      newMonth = 1;
      newYear++;
    } else if (newMonth < 1) {
      newMonth = 12;
      newYear--;
    }

    setMonth(newMonth);
    setYear(newYear);
    setSelectedDay(null);
  };

  if (loading) {
    return <div className="loading">Loading calendar...</div>;
  }

  return (
    <div className="container">
      <h1>Activity Calendar</h1>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <button onClick={() => changeMonth(-1)}>← Previous</button>
          <h2>{monthNames[month - 1]} {year}</h2>
          <button onClick={() => changeMonth(1)}>Next →</button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px', marginBottom: '1rem' }}>
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} style={{ textAlign: 'center', fontWeight: 600, color: '#888', padding: '0.5rem' }}>
              {day}
            </div>
          ))}
        </div>

        <div className="calendar">
          {renderCalendar()}
        </div>

        <div style={{ marginTop: '2rem', display: 'flex', gap: '2rem', justifyContent: 'center', fontSize: '0.9rem' }}>
          <div><span className="calendar-day day-active" style={{ display: 'inline-block', width: '20px', height: '20px', marginRight: '8px' }}></span> Activity Logged</div>
          <div><span className="calendar-day day-empty" style={{ display: 'inline-block', width: '20px', height: '20px', marginRight: '8px' }}></span> Rest Day</div>
        </div>
      </div>

      {/* Activity Details Modal */}
      {selectedDay && (
        <div className="card" style={{ marginTop: '1rem', background: 'rgba(102, 51, 255, 0.1)', borderColor: '#6633ff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2>Activities on {new Date(selectedDay.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</h2>
            <button onClick={() => setSelectedDay(null)}>Close</button>
          </div>
          {selectedDay.activities.map((activity, idx) => (
            <div key={idx} style={{
              background: 'rgba(0,0,0,0.3)',
              padding: '1rem',
              borderRadius: '8px',
              marginBottom: '0.5rem',
              borderLeft: '4px solid #17e5c7'
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div>
                  <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Type</div>
                  <div style={{ fontWeight: 600 }}>{activity.type}</div>
                </div>
                <div>
                  <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Duration</div>
                  <div style={{ fontWeight: 600 }}>{Math.round(activity.duration)} min</div>
                </div>
                <div>
                  <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Classification</div>
                  <div style={{ fontWeight: 600, textTransform: 'uppercase', color: '#17e5c7' }}>{activity.classification}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Calendar;
