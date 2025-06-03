import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import JobsPage from './pages/JobsPage';
import LocationsPage from './pages/LocationsPage';
import CompaniesPage from './pages/ComapniesPage';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/locations" element={<LocationsPage />} />
          <Route path="/companies" element={<CompaniesPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
