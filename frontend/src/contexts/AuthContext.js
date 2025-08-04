import React, { createContext, useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { authApi, apiHelpers } from "../services/api";

const AuthContext = createContext(undefined);

export function useAuth() {
	return useContext(AuthContext);
}

export function AuthProvider({ children }) {
	const [currentUser, setCurrentUser] = useState(null);
	const [token, setToken] = useState(localStorage.getItem("token") || null);
	const [loading, setLoading] = useState(true);
	const navigate = useNavigate();

	// Check if token exists on load
	useEffect(() => {
		const storedToken = localStorage.getItem("token");
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
			const data = await authApi.login(email, password);
			localStorage.setItem("token", data.access_token);
			setToken(data.access_token);
			setCurrentUser({ isLoggedIn: true });
			return { success: true };
		} catch (error) {
			return apiHelpers.handleError(error, "Login failed");
		}
	};

	// Register function
	const register = async (email, password) => {
		try {
			await authApi.register(email, password);
			return { success: true };
		} catch (error) {
			return apiHelpers.handleError(error, "Registration failed");
		}
	};

	// Logout function
	const logout = () => {
		localStorage.removeItem("token");
		setToken(null);
		setCurrentUser(null);
		navigate("/login");
	};

	const value = {
		currentUser,
		token,
		login,
		register,
		logout,
		isAuthenticated: !!token,
	};

	return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>;
}
