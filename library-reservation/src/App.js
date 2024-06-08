import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import ReservationList from './components/ReservationList';
import ReservationForm from './components/ReservationForm';
import ReservationDetail from './components/ReservationDetail';
import ReservationUpdate from './components/ReservationUpdate';

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/new">Make Reservation</Link></li>
            <li><Link to="/reservations">Reservation Catalog</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<Navigate to="/reservations" />} /> 
          <Route path="/new" element={<ReservationForm />} />
          <Route path="/reservations" element={<ReservationList />} />
          <Route path="/reservations/:book_id" element={<ReservationDetail />} />
          <Route path="/reservations/update/:book_id" element={<ReservationUpdate />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
