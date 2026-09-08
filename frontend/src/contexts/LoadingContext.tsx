import React, { JSX, ReactNode, useState } from "react";
import { LoadingContext, LoadingContextType } from "./LoadingContext.context";

export { useLoading } from "./LoadingContext.context";
export type { LoadingContextType } from "./LoadingContext.context";

interface LoadingProviderProps {
	children: ReactNode;
}

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
