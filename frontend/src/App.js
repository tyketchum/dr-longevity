import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import CommandCenter from './pages/CommandCenter';
import Activities from './pages/Activities';
import WeeklyLog from './pages/WeeklyLog';
import Calendar from './pages/Calendar';
import Labs from './pages/Labs';
import CrossFit from './pages/CrossFit';
import FoodJournal from './pages/FoodJournal';

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          <ul>
            <li>
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
                Command Center
              </NavLink>
            </li>
            <li>
              <NavLink to="/activities" className={({ isActive }) => isActive ? 'active' : ''}>
                Activities
              </NavLink>
            </li>
            <li>
              <NavLink to="/weekly" className={({ isActive }) => isActive ? 'active' : ''}>
                Weekly Log
              </NavLink>
            </li>
            <li>
              <NavLink to="/calendar" className={({ isActive }) => isActive ? 'active' : ''}>
                Calendar
              </NavLink>
            </li>
            <li>
              <NavLink to="/crossfit" className={({ isActive }) => isActive ? 'active' : ''}>
                CrossFit WODs
              </NavLink>
            </li>
            <li>
              <NavLink to="/food" className={({ isActive }) => isActive ? 'active' : ''}>
                Food Journal
              </NavLink>
            </li>
            <li>
              <NavLink to="/labs" className={({ isActive }) => isActive ? 'active' : ''}>
                Labs & Strength
              </NavLink>
            </li>
          </ul>
        </nav>

        <Routes>
          <Route path="/" element={<CommandCenter />} />
          <Route path="/activities" element={<Activities />} />
          <Route path="/weekly" element={<WeeklyLog />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/crossfit" element={<CrossFit />} />
          <Route path="/food" element={<FoodJournal />} />
          <Route path="/labs" element={<Labs />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
