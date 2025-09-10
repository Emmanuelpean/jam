import React, { createContext, useCallback, useContext, useEffect, useState, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../services/Api";
import { UserData, Response } from "../services/Schemas";

interface CurrentUser extends UserData {
	isLoggedIn: boolean;
}

interface LoginResponse extends Response {
	access_token?: string;
}

// Define the auth context value type
interface AuthContextType {
	currentUser: CurrentUser | null;
	token: string | null;
	is_admin: boolean;
	login: (email: string, password: string) => Promise<Response>;
	register: (email: string, password: string) => Promise<Response>;
	logout: () => void;
	isAuthenticated: boolean;
}

// Define props for AuthProvider
interface AuthProviderProps {
	children: ReactNode;
}

// Define API error type (should match your Api.ts file)
interface ApiError extends Error {
	status?: number;
	data?: any;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return context;
}

export function AuthProvider({ children }: AuthProviderProps) {
	const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
	const [token, setToken] = useState<string | null>(localStorage.getItem("token") || null);
	const [is_admin, setIsAdmin] = useState<boolean>(false);
	const [loading, setLoading] = useState<boolean>(true);
	const [userFetched, setUserFetched] = useState<boolean>(false); // Add this flag
	const navigate = useNavigate();

	// Memoize fetchUserInfo to prevent unnecessary re-creation
	const fetchUserInfo = useCallback(
		async (authToken: string): Promise<void> => {
			// Don't fetch if we already have user data and the token hasn't changed
			if (userFetched && currentUser && token === authToken) {
				setLoading(false);
				return;
			}

			try {
				const userData: UserData = await authApi.getCurrentUser(authToken);
				setCurrentUser({ isLoggedIn: true, ...userData });
				setIsAdmin(userData.is_admin || false);
				setUserFetched(true);
			} catch (error) {
				const apiError = error as ApiError;
				console.error("Failed to fetch user info:", apiError);

				// If token is invalid, clear it
				if (apiError.status === 401 || apiError.status === 403) {
					localStorage.removeItem("token");
					setToken(null);
					setCurrentUser(null);
					setIsAdmin(false);
				} else {
					// If it's a network error, set basic auth state without admin
					// We can't create a valid CurrentUser without email, so set to null
					// The user will remain logged in via the token, but without user data
					setCurrentUser(null);
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
			fetchUserInfo(storedToken).then(() => null);
		} else {
			setLoading(false);
		}
	}, []); // Remove fetchUserInfo from dependencies to prevent re-runs

	const login = async (email: string, password: string): Promise<Response> => {
		try {
			const data: LoginResponse = await authApi.login(email, password);
			if (data.access_token) {
				localStorage.setItem("token", data.access_token);
				setToken(data.access_token);
				setUserFetched(false);

				// Fetch user info after successful login
				await fetchUserInfo(data.access_token);
			}

			return { success: true };
		} catch (error) {
			const apiError = error as ApiError;
			return {
				success: false,
				error: "Login failed. Please check your credentials and try again.",
				status: apiError.status,
			};
		}
	};

	// Register function
	const register = async (email: string, password: string): Promise<Response> => {
		try {
			await authApi.register(email, password);
			return { success: true };
		} catch (error) {
			const apiError = error as ApiError;
			return {
				success: false,
				error: "Registration failed. Please try again later.",
				status: apiError.status,
			};
		}
	};

	// Logout function
	const logout = (): void => {
		localStorage.removeItem("token");
		setToken(null);
		setCurrentUser(null);
		setIsAdmin(false);
		setUserFetched(false); // Reset the flag
		navigate("/login");
	};

	const value: AuthContextType = {
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
