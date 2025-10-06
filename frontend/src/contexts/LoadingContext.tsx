import React, { createContext, useContext, useState, ReactNode } from "react";

interface LoadingContextType {
	isLoading: boolean;
	loadingMessage: string;
	progress: number;
	showLoading: (message?: string, progress?: number) => void;
	hideLoading: () => void;
	updateProgress: (progress: number, message?: string) => void;
}

interface LoadingProviderProps {
	children: ReactNode;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const useLoading = (): LoadingContextType => {
	const context = useContext(LoadingContext);
	if (!context) {
		throw new Error("useLoading must be used within a LoadingProvider");
	}
	return context;
};

export const LoadingProvider = ({ children }: LoadingProviderProps) => {
	const [isLoading, setIsLoading] = useState<boolean>(false);
	const [loadingMessage, setLoadingMessage] = useState<string>("Loading...");
	const [progress, setProgress] = useState<number>(0);

	const showLoading = (message: string = "Loading...", initialProgress: number = 0): void => {
		setLoadingMessage(message);
		setProgress(initialProgress);
		setIsLoading(true);
	};

	const hideLoading = (): void => {
		setIsLoading(false);
		setProgress(0);
	};

	const updateProgress = (newProgress: number, message?: string): void => {
		setProgress(newProgress);
		if (message) {
			setLoadingMessage(message);
		}
	};

	const value: LoadingContextType = {
		isLoading,
		loadingMessage,
		progress,
		showLoading,
		hideLoading,
		updateProgress,
	};

	return <LoadingContext.Provider value={value}>{children}</LoadingContext.Provider>;
};
