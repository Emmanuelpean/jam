import React, { createContext, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi, GenericResponse, LoginResponse, UpdateCurrentUserResponse } from "../services/api/Users";
import { ApiResponse } from "../services/api/Base";
import { DEFAULT_THEME } from "../utils/Theme";
import { UserData, UserDataUpdate } from "../services/schemas/Core";
import { handleApiError } from "../services/api/ApiError";

export interface CurrentUser extends UserData {
	token: string | null;
}

export interface AuthContextType {
	currentUser: CurrentUser | null;
	token: string | null;
	login: (email: string, password: string, rememberMe?: boolean) => Promise<GenericResponse>;
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
		return localStorage.getItem("token") || sessionStorage.getItem("token");
	});
	const [userFetched, setUserFetched] = useState<boolean>(false);
	const hadTokenOnMount = useRef<boolean>(!!(localStorage.getItem("token") || sessionStorage.getItem("token")));
	const navigate = useNavigate();

	const fetchUserInfo = useCallback(
		async (authToken: string): Promise<void> => {
			try {
				const userData: ApiResponse<UserData> = await authApi.getCurrentUser(authToken);

				setCurrentUser({
					token: authToken,
					...userData.data,
				});
			} catch (error) {
				console.error("Failed to fetch user info:", error);

				const { status } = handleApiError(error);

				// Invalid token — log out user
				if (status === 401 || status === 403) {
					localStorage.removeItem("token");
					setToken(null);
					setCurrentUser(null);
				} else {
					setCurrentUser(null);
				}
			} finally {
				setUserFetched(true);
			}
		},
		[token, setToken, setCurrentUser, setUserFetched]
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
		setCurrentUser((prev: CurrentUser | null): CurrentUser | null =>
			prev ? { ...prev, ...userResponse.data } : prev
		);
		return response;
	};

	useEffect((): void => {
		document.documentElement.setAttribute("data-theme", currentUser?.preferences.theme || DEFAULT_THEME);
	}, [currentUser]);

	// Check if token exists on load and fetch user info
	useEffect((): void => {
		// Only fetch user info if we have a token and haven't fetched yet
		if (token && !userFetched) {
			fetchUserInfo(token).then(() => null);
		}
	}, [token, userFetched, fetchUserInfo]);

	// Record last login only for returning users (token already in localStorage on mount)
	useEffect((): void => {
		if (hadTokenOnMount.current && token) {
			authApi.heartbeat(token).catch(() => null);
		}
	}, []);

	const login = async (email: string, password: string, rememberMe: boolean = false): Promise<GenericResponse> => {
		const data: ApiResponse<LoginResponse> = await authApi.login(email, password);
		if (data.data.access_token) {
			if (rememberMe) {
				localStorage.setItem("token", data.data.access_token);
			} else {
				sessionStorage.setItem("token", data.data.access_token);
			}
			setToken(data.data.access_token);
			setUserFetched(false);
			await fetchUserInfo(data.data.access_token);
		}
		return { success: true, message: "Login successful", error_code: null };
	};

	const logout = (): void => {
		// Fire-and-forget demo cleanup if this is a demo user
		if (currentUser?.is_demo && token) {
			authApi.demoCleanup(token).catch(() => null);
		}

		localStorage.removeItem("token");
		sessionStorage.removeItem("token");
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
