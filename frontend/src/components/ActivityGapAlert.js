import React, { useEffect, useState } from 'react';
import { getStatus } from '../services/api';

const ActivityGapAlert = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
    // Refresh every 5 minutes
    const interval = setInterval(fetchStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await getStatus();
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading status...</div>;
  }

  if (!status) {
    return null;
  }

  const { days_since_last_activity, alert_level, last_activity_type, last_activity_date } = status;

  const getAlertMessage = () => {
    if (alert_level === 'green') {
      return '✓ ACTIVE';
    } else if (alert_level === 'yellow') {
      return '⚠ REST DAY ENDING';
    } else {
      return '🚨 GET MOVING NOW!';
    }
  };

  const getDetailMessage = () => {
    const days = Math.floor(days_since_last_activity);
    const hours = Math.round((days_since_last_activity - days) * 24);

    if (days === 0) {
      return `Last activity: ${hours}h ago (${last_activity_type})`;
    } else if (days === 1) {
      return `Last activity: 1 day ago (${last_activity_type})`;
    } else {
      return `Last activity: ${days} days ago (${last_activity_type})`;
    }
  };

  return (
    <div className={`alert alert-${alert_level}`}>
      <h1>{days_since_last_activity.toFixed(1)} DAYS</h1>
      <h2>{getAlertMessage()}</h2>
      <p style={{ marginTop: '1rem', fontSize: '1.1rem', opacity: 0.8 }}>
        {getDetailMessage()}
      </p>
      {last_activity_date && (
        <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', opacity: 0.6 }}>
          {new Date(last_activity_date).toLocaleDateString()}
        </p>
      )}
    </div>
  );
};

export default ActivityGapAlert;
