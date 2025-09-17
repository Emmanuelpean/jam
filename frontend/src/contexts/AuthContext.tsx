import React, { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi, ApiError } from "../services/Api";
import { UserData } from "../services/Schemas";

export interface CurrentUser extends UserData {
	isLoggedIn: boolean;
}

export interface AuthResponse {
	success: boolean;
	status?: number;
	error?: string;
	userMessage?: string;
}

export interface LoginResponse {
	access_token?: string;
}

export interface AuthContextType {
	currentUser: CurrentUser | null;
	token: string | null;
	is_admin: boolean;
	login: (email: string, password: string) => Promise<AuthResponse>;
	register: (email: string, password: string) => Promise<AuthResponse>;
	logout: () => void;
	isAuthenticated: boolean;
}

export interface AuthProviderProps {
	children: ReactNode;
}

export type AuthAction = "login" | "register";

export interface FormData {
	email: string;
	password: string;
	confirmPassword: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getErrorMessage = (status: number | undefined, action: AuthAction): string => {
	switch (status) {
		case 400:
			return action === "register" ? "Email already registered" : "Invalid request. Please check your input.";
		case 401:
			return action === "register"
				? "Sorry, you are not allowed to sign up for now."
				: "Incorrect email or password";
		case 403:
			return "Incorrect email or password";
		case 422:
			return "Invalid input data. Please check your information.";
		case 500:
			return "Server error. Please try again later.";
		default:
			return action === "register"
				? "Registration failed. Please try again later."
				: "Login failed. Please check your credentials and try again.";
	}
};

const getUserMessage = (status: number | undefined, action: AuthAction): string => {
	switch (status) {
		case 400:
			return action === "register" ? "Registration Failed" : "Login Failed";
		case 401:
		case 403:
		case 404:
			return action === "register" ? "Registration Failed" : "Login Failed";
		default:
			return action === "register" ? "Registration Error" : "Login Error";
	}
};

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
	const [userFetched, setUserFetched] = useState<boolean>(false);
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

	const login = async (email: string, password: string): Promise<AuthResponse> => {
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
				error: getErrorMessage(apiError.status, "login"),
				userMessage: getUserMessage(apiError.status, "login"),
				status: apiError.status,
			};
		}
	};

	// Register function
	const register = async (email: string, password: string): Promise<AuthResponse> => {
		try {
			await authApi.register(email, password);
			return { success: true };
		} catch (error) {
			const apiError = error as ApiError;
			return {
				success: false,
				error: getErrorMessage(apiError.status, "register"),
				userMessage: getUserMessage(apiError.status, "register"),
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
		setUserFetched(false);
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
