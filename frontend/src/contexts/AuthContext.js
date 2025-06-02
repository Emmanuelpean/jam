import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  // Check if token exists on load
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      // You could fetch user details here if needed
      setCurrentUser({ isLoggedIn: true });
    }
    setLoading(false);
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setCurrentUser({ isLoggedIn: true });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

// Register function
const register = async (email, password) => {
  try {
    const response = await fetch('http://localhost:8000/users/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      // Extract the specific error message or provide a default
      const errorMessage = errorData.detail ||
                          (typeof errorData === 'object' ? JSON.stringify(errorData) : 'Registration failed');
      throw new Error(errorMessage);
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
};


  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    token,
    login,
    register,
    logout,
    isAuthenticated: !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
