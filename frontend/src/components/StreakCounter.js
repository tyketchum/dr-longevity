import React, { useEffect, useState } from 'react';
import { getDailyMetrics } from '../services/api';

const StreakCounter = () => {
  const [streak, setStreak] = useState(0);
  const [loading, setLoading] = useState(true);
  const [milestone, setMilestone] = useState(false);

  useEffect(() => {
    fetchStreak();
  }, []);

  const fetchStreak = async () => {
    try {
      const response = await getDailyMetrics(1);
      if (response.data.length > 0) {
        const newStreak = response.data[0].current_streak || 0;

        // Check for milestone (7, 14, 30, 60, 90 days)
        const milestones = [7, 14, 30, 60, 90, 180, 365];
        if (milestones.includes(newStreak)) {
          setMilestone(true);
          setTimeout(() => setMilestone(false), 3000);
        }

        setStreak(newStreak);
      }
    } catch (error) {
      console.error('Error fetching streak:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return null;
  }

  const getStreakEmoji = () => {
    if (streak === 0) return '😢';
    if (streak >= 365) return '🏆';
    if (streak >= 180) return '💎';
    if (streak >= 90) return '⚡';
    if (streak >= 60) return '🔥🔥🔥';
    if (streak >= 30) return '🔥🔥';
    if (streak >= 14) return '🔥';
    if (streak >= 7) return '✨';
    return '💪';
  };

  const getStreakMessage = () => {
    if (streak === 0) return 'Start your streak today!';
    if (streak === 1) return 'Great start!';
    if (streak < 7) return 'Keep it going!';
    if (streak < 30) return 'Building consistency!';
    if (streak < 60) return 'Unstoppable!';
    if (streak < 90) return 'This is your lifestyle now!';
    if (streak < 180) return 'Medicine 3.0 Champion!';
    if (streak < 365) return 'Longevity Legend!';
    return 'You are immortal!';
  };

  return (
    <div className="card">
      <h2>Activity Streak</h2>
      <div className={`streak ${milestone ? 'milestone' : ''}`}>
        {getStreakEmoji()} {streak} Days
      </div>
      <p style={{ textAlign: 'center', fontSize: '1.2rem', color: '#888' }}>
        {getStreakMessage()}
      </p>
      {milestone && (
        <p style={{ textAlign: 'center', fontSize: '1.5rem', marginTop: '1rem', animation: 'pulse 1s infinite' }}>
          🎉 MILESTONE ACHIEVED! 🎉
        </p>
      )}
      <div style={{ marginTop: '1.5rem', fontSize: '0.9rem', color: '#666', textAlign: 'center' }}>
        Streak continues as long as you don't go more than 2 days without activity
      </div>
    </div>
  );
};

export default StreakCounter;
