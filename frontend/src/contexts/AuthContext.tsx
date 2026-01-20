import React, { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi, GenericResponse, LoginResponse, UpdateCurrentUserResponse } from "../services/api/Users";
import { ApiError, ApiResponse } from "../services/api/Base";
import { DEFAULT_THEME } from "../utils/Theme";
import { UserData, UserDataUpdate } from "../services/schemas/Core";

export interface CurrentUser extends UserData {
	token: string | null;
}

export interface AuthContextType {
	currentUser: CurrentUser | null;
	token: string | null;
	login: (email: string, password: string) => Promise<GenericResponse>;
	updateCurrentUser: (userData: UserDataUpdate) => Promise<ApiResponse<UpdateCurrentUserResponse> | null>;
	fetchUserInfo: (authToken: string) => Promise<void>;
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
	firstName: string;
	lastName: string;
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
	const [token, setToken] = useState<string | null>(() => {
		return localStorage.getItem("token");
	});
	const [userFetched, setUserFetched] = useState<boolean>(false);
	const navigate = useNavigate();

	const fetchUserInfo = useCallback(
		async (authToken: string): Promise<void> => {
			try {
				const userData: ApiResponse<UserData> = await authApi.getCurrentUser(authToken);
				setCurrentUser({
					token: token,
					...userData.data,
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
		[userFetched, currentUser, token]
	);

	const updateCurrentUser = async (
		userData: UserDataUpdate
	): Promise<ApiResponse<UpdateCurrentUserResponse> | null> => {
		if (!token) return null;
		const response: ApiResponse<UpdateCurrentUserResponse> = await authApi.updateCurrentUser(userData, token);
		if (response.data.logged_out) {
			logout();
			return response;
		}
		const userResponse: ApiResponse<UserData> = await authApi.getCurrentUser(token);
		setCurrentUser((prev: CurrentUser | null) => (prev ? { ...prev, ...userResponse.data } : prev));
		return response;
	};

	useEffect(() => {
		document.documentElement.setAttribute("data-theme", currentUser?.preferences.theme || DEFAULT_THEME);
	}, [currentUser]);

	// Check if token exists on load and fetch user info
	useEffect(() => {
		// Only fetch user info if we have a token and haven't fetched yet
		if (token && !userFetched) {
			fetchUserInfo(token).then(() => null);
		}
	}, [token, userFetched, fetchUserInfo]);

	const login = async (email: string, password: string): Promise<GenericResponse> => {
		const data: ApiResponse<LoginResponse> = await authApi.login(email, password);
		if (data.data.access_token) {
			localStorage.setItem("token", data.data.access_token);
			setToken(data.data.access_token);
			setUserFetched(false);

			// Fetch user info after successful login
			await fetchUserInfo(data.data.access_token);
		}
		return { success: true, message: "Login successful", error_code: null };
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
		fetchUserInfo,
		token,
		login,
		logout,
		updateCurrentUser,
		isAuthenticated: !!token,
	};

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
