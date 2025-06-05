import React from 'react';
import {BrowserRouter, Navigate, Route, Routes} from 'react-router-dom';
import {AuthProvider} from './contexts/AuthContext';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import LocationsPage from './pages/LocationsPage';
import StyleShowcase from './pages/TestPage';
import 'bootstrap/dist/css/bootstrap.min.css'; // Bootstrap first
import './App.css';


function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/login" element={<Login/>}/>
                    <Route path="/register" element={<Register/>}/>
                    <Route path="/" element={<Navigate to="/login"/>}/>
                    <Route path="/locations" element={<LocationsPage/>}/>
                    <Route path="/showcase" element={<StyleShowcase/>}/>
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
}

export default App;
