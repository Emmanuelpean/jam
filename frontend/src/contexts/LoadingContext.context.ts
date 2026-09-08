import { createContext, useContext } from "react";

export interface LoadingContextType {
	isLoading: boolean;
	loadingMessage: string;
	progress: number | undefined;
	showLoading: (message?: string, progress?: number) => void;
	hideLoading: () => void;
	updateProgress: (progress: number, message?: string) => void;
}

export const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const useLoading = (): LoadingContextType => {
	const context: LoadingContextType | undefined = useContext(LoadingContext);
	if (!context) {
		throw new Error("useLoading must be used within a LoadingProvider");
	}
	return context;
};
