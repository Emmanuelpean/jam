import React, { createContext, useState, useEffect, useContext, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { authApi, apiHelpers } from "../services/Api";

const AuthContext = createContext(undefined);

export function useAuth() {
	return useContext(AuthContext);
}

export function AuthProvider({ children }) {
	const [currentUser, setCurrentUser] = useState(null);
	const [token, setToken] = useState(localStorage.getItem("token") || null);
	const [is_admin, setIsAdmin] = useState(false);
	const [loading, setLoading] = useState(true);
	const [userFetched, setUserFetched] = useState(false); // Add this flag
	const navigate = useNavigate();

	// Memoize fetchUserInfo to prevent unnecessary re-creation
	const fetchUserInfo = useCallback(
		async (authToken) => {
			// Don't fetch if we already have user data and the token hasn't changed
			if (userFetched && currentUser && token === authToken) {
				setLoading(false);
				return;
			}

			try {
				const userData = await authApi.getCurrentUser(authToken);
				setCurrentUser({ isLoggedIn: true, ...userData });
				setIsAdmin(userData.is_admin || false);
				setUserFetched(true); // Mark as fetched
				console.log("User data fetched:", userData);
			} catch (error) {
				console.error("Failed to fetch user info:", error);

				// If token is invalid, clear it
				if (error.status === 401 || error.status === 403) {
					localStorage.removeItem("token");
					setToken(null);
					setCurrentUser(null);
					setIsAdmin(false);
				} else {
					// If it's a network error, set basic auth state without admin
					setCurrentUser({ isLoggedIn: true });
					setIsAdmin(false);
					setUserFetched(true);
				}
			} finally {
				setLoading(false);
			}
		},
		[userFetched, currentUser, token],
	);

	// Check if token exists on load and fetch user info
	useEffect(() => {
		const storedToken = localStorage.getItem("token");
		if (storedToken && !userFetched) {
			// Only fetch if not already fetched
			setToken(storedToken);
			fetchUserInfo(storedToken);
		} else {
			setLoading(false);
		}
	}, []); // Remove fetchUserInfo from dependencies to prevent re-runs

	const login = async (email, password) => {
		try {
			const data = await authApi.login(email, password);
			localStorage.setItem("token", data.access_token);
			setToken(data.access_token);
			setUserFetched(false);

			// Fetch user info after successful login
			await fetchUserInfo(data.access_token);

			return { success: true };
		} catch (error) {
			return {
				success: false,
				error: "Login failed. Please check your credentials and try again.",
				status: error.status,
			};
		}
	};

	// Register function
	const register = async (email, password) => {
		try {
			await authApi.register(email, password);
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error: "Registration failed. Please try again later.",
				status: error.status,
			};
		}
	};

	// Logout function
	const logout = () => {
		localStorage.removeItem("token");
		setToken(null);
		setCurrentUser(null);
		setIsAdmin(false);
		setUserFetched(false); // Reset the flag
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
