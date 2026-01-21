import React, { createContext, JSX, ReactNode, useContext, useState } from "react";

interface LoadingContextType {
	isLoading: boolean;
	loadingMessage: string;
	progress: number | undefined;
	showLoading: (message?: string, progress?: number) => void;
	hideLoading: () => void;
	updateProgress: (progress: number, message?: string) => void;
}

interface LoadingProviderProps {
	children: ReactNode;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const useLoading = (): LoadingContextType => {
	const context: LoadingContextType | undefined = useContext(LoadingContext);
	if (!context) {
		throw new Error("useLoading must be used within a LoadingProvider");
	}
	return context;
};

export const LoadingProvider = ({ children }: LoadingProviderProps): JSX.Element => {
	const [isLoading, setIsLoading] = useState<boolean>(false);
	const [loadingMessage, setLoadingMessage] = useState<string>("Loading...");
	const [progress, setProgress] = useState<number | undefined>(undefined);

	const showLoading = (message: string = "Loading...", initialProgress: number = 0): void => {
		if (message) {
			setLoadingMessage(message);
		}
		setProgress(initialProgress);
		setIsLoading(true);
	};

	const hideLoading = (): void => {
		setIsLoading(false);
		setProgress(0);
	};

	const updateProgress = (newProgress: number, message?: string): void => {
		if (message) {
			setLoadingMessage(message);
		}
		setProgress(newProgress);
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
