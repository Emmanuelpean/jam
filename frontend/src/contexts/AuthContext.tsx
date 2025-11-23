import React, { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, authApi } from "../services/Api";
import { UserData } from "../services/Schemas";

export interface CurrentUser extends UserData {
	token: string | null;
}

export interface AuthResponse {
	success: boolean;
	status?: number;
	error?: string;
}

export interface LoginResponse {
	access_token?: string;
}

export interface AuthContextType {
	currentUser: CurrentUser | null;
	token: string | null;
	login: (email: string, password: string) => Promise<AuthResponse>;
	register: (email: string, password: string) => Promise<AuthResponse>;
	updateCurrentUser: (userData: Partial<UserData>) => Promise<any>;
	logout: () => void;
	isAuthenticated: boolean;
}

export interface AuthProviderProps {
	children: ReactNode;
}

export interface FormData {
	email: string;
	password: string;
	confirmPassword: string;
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
	const [userFetched, setUserFetched] = useState<boolean>(false);
	const navigate = useNavigate();

	const fetchUserInfo = useCallback(
		async (authToken: string): Promise<void> => {
			// Don't fetch if we already have user data and the token hasn't changed
			if (userFetched && currentUser && token === authToken) {
				return;
			}

			try {
				const userData: UserData = await authApi.getCurrentUser(authToken);
				setCurrentUser({
					token: token,
					...userData,
				});
				setUserFetched(true);
			} catch (error) {
				const apiError = error as ApiError;
				console.error("Failed to fetch user info:", apiError);

				// If token is invalid, clear it
				if (apiError.status === 401 || apiError.status === 403) {
					localStorage.removeItem("token");
					setToken(null);
					setCurrentUser(null);
				} else {
					// If it's a network error, set basic auth state without admin
					// We can't create a valid CurrentUser without email, so set to null
					// The user will remain logged in via the token, but without user data
					setCurrentUser(null);
					setUserFetched(true);
				}
			}
		},
		[userFetched, currentUser, token],
	);

	const updateCurrentUser = async (userData: Partial<UserData>) => {
		if (!token) return null;
		const response = await authApi.updateCurrentUser(userData, token);
		setCurrentUser((prev: CurrentUser | null) => (prev ? { ...prev, ...userData } : prev));
		return response;
	};

	// Check if token exists on load and fetch user info
	useEffect(() => {
		const storedToken = localStorage.getItem("token");
		if (storedToken && !userFetched) {
			// Only fetch if not already fetched
			setToken(storedToken);
			fetchUserInfo(storedToken).then(() => null);
		}
	}, []);

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
				error: apiError.message,
				status: apiError.status,
			};
		}
	};

	const register = async (email: string, password: string): Promise<AuthResponse> => {
		try {
			await authApi.register(email, password);
			return { success: true };
		} catch (error) {
			const apiError = error as ApiError;
			return {
				success: false,
				error: apiError.message,
				status: apiError.status,
			};
		}
	};

	const logout = (): void => {
		localStorage.removeItem("token");
		setToken(null);
		setCurrentUser(null);
		setUserFetched(false);
		navigate("/login");
	};

	const value: AuthContextType = {
		currentUser,
		token,
		login,
		register,
		logout,
		updateCurrentUser,
		isAuthenticated: !!token,
	};

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
