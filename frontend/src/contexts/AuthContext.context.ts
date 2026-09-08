import { createContext, ReactNode, useContext } from "react";
import { GenericResponse } from "../services/api/Users";
import { ApiResponse } from "../services/api/Base";
import { UserData, UserDataUpdate } from "../services/schemas/Core";
import { UpdateCurrentUserResponse } from "../services/api/Users";

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

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return context;
}
