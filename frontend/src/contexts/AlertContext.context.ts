import { createContext, ReactNode, useContext } from "react";
import { AlertState } from "../components/AlertModal/AlertModal";

export interface AlertConfig {
	title?: string;
	message: string | ReactNode;
	type?: "info" | "success" | "danger" | "warning" | "primary";
	confirmText?: string;
	cancelText?: string | null;
	icon?: string | null;
	size?: "sm" | "md" | "lg" | "xl";
	id?: string | null;
	onSuccess?: (() => void | Promise<void>) | null;
}

export interface AlertContextType {
	alertState: AlertState;
	showAlert: (config: AlertConfig) => Promise<boolean>;
	hideAlert: () => void;
	showSuccess: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showError: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showWarning: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showInfo: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showConfirm: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showDelete: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showLogout: (config?: Partial<AlertConfig>) => Promise<boolean>;
}

export const AlertContext = createContext<AlertContextType | null>(null);

export const useAlert = (): AlertContextType => {
	const context: AlertContextType | null = useContext(AlertContext);
	if (!context) {
		throw new Error("useAlert must be used within AlertProvider");
	}
	return context;
};
