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
	const [is_admin, setIsAdmin] = useState(false);
	const [loading, setLoading] = useState(true);
	const navigate = useNavigate();

	// Check if token exists on load and fetch user info
	useEffect(() => {
		const storedToken = localStorage.getItem("token");
		if (storedToken) {
			setToken(storedToken);
			fetchUserInfo(storedToken);
		} else {
			setLoading(false);
		}
	}, []);

	// Fetch user information including admin status
	const fetchUserInfo = async (authToken) => {
		try {
			// Assuming you have an endpoint to get current user info
			const userData = await authApi.getCurrentUser(authToken);
			setCurrentUser({ isLoggedIn: true, ...userData });
			setIsAdmin(userData.is_admin || false);
		} catch (error) {
			console.error("Failed to fetch user info:", error);
			// If fetching user info fails, still set as logged in but not admin
			setCurrentUser({ isLoggedIn: true });
			setIsAdmin(false);
		} finally {
			setLoading(false);
		}
	};

	// Login function
	const login = async (email, password) => {
		try {
			const data = await authApi.login(email, password);
			localStorage.setItem("token", data.access_token);
			setToken(data.access_token);

			// Fetch user info after successful login
			await fetchUserInfo(data.access_token);

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
		setIsAdmin(false);
		navigate("/login");
	};

	const value = {
		currentUser,
		token,
		is_admin,
		login,
		register,
		logout,
		isAuthenticated: !!token,
	};

	return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>;
}
