// contexts/LoadingContext.js
import React, { createContext, useContext, useState } from "react";

const LoadingContext = createContext();

export const useLoading = () => {
	const context = useContext(LoadingContext);
	if (!context) {
		throw new Error("useLoading must be used within a LoadingProvider");
	}
	return context;
};

export const LoadingProvider = ({ children }) => {
	const [isLoading, setIsLoading] = useState(false);
	const [loadingMessage, setLoadingMessage] = useState("Loading...");

	const showLoading = (message = "Loading...") => {
		setLoadingMessage(message);
		setIsLoading(true);
	};

	const hideLoading = () => {
		setIsLoading(false);
	};

	return (
		<LoadingContext.Provider
			value={{
				isLoading,
				loadingMessage,
				showLoading,
				hideLoading,
			}}
		>
			{children}
		</LoadingContext.Provider>
	);
};
