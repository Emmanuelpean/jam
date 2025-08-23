import React, { createContext, useContext, useState, ReactNode } from "react";

// Define the loading context value type
interface LoadingContextType {
	isLoading: boolean;
	loadingMessage: string;
	showLoading: (message?: string) => void;
	hideLoading: () => void;
}

// Define props for LoadingProvider
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

export const LoadingProvider = ({ children }: LoadingProviderProps): JSX.Element => {
	const [isLoading, setIsLoading] = useState<boolean>(false);
	const [loadingMessage, setLoadingMessage] = useState<string>("Loading...");

	const showLoading = (message: string = "Loading..."): void => {
		setLoadingMessage(message);
		setIsLoading(true);
	};

	const hideLoading = (): void => {
		setIsLoading(false);
	};

	const value: LoadingContextType = {
		isLoading,
		loadingMessage,
		showLoading,
		hideLoading,
	};

	return <LoadingContext.Provider value={value}>{children}</LoadingContext.Provider>;
};
