import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStatus = () => api.get('/status');
export const getDailyMetrics = (days = 90) => api.get(`/daily-metrics?days=${days}`);
export const getActivities = (days = 90) => api.get(`/activities?days=${days}`);
export const getWeeklySummaries = (weeks = 12) => api.get(`/weekly-summaries?weeks=${weeks}`);
export const getLabs = () => api.get('/labs');
export const getCalendar = (year, month) => api.get(`/calendar?year=${year}&month=${month}`);

export const createActivity = (activity) => api.post('/activities', activity);
export const createLabEntry = (lab) => api.post('/labs', lab);

export const getFoodLog = (days = 7) => api.get(`/food?days=${days}`);
export const logFood = (food) => api.post('/food', food);
export const getWaterLog = (days = 7) => api.get(`/water?days=${days}`);
export const logWater = (water) => api.post('/water', water);
export const getTodayWater = () => api.get('/water/today');

export const syncDaily = () => api.post('/sync/daily');
export const syncHistorical = (days = 90) => api.post(`/sync/historical?days=${days}`);

export default api;
