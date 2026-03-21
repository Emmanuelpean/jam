import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { ApiResponse, baseApi } from "../services/api/Base";

export interface ConfigContextValue {
	config: any;
	isLoading: boolean;
	error: Error | null;
}

export interface Config {
	scraper_email: string;
	support_email: string;
	platform_sender_emails: Record<string, string>;
	min_password_length: number;
	app_demo_username: string;
	scrape_max_retry: number;
}

const ConfigContext = createContext<ConfigContextValue | undefined>(undefined);

export const ConfigProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
	const [config, setConfig] = useState<Config | null>(null);
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState<Error | null>(null);

	useEffect(() => {
		const fetchConfig = async () => {
			try {
				const response: ApiResponse<Config> = await baseApi.get("config/", null);
				setConfig(response.data);
			} catch (e: any) {
				setError(e);
			} finally {
				setIsLoading(false);
			}
		};

		fetchConfig().then();
	}, []);

	return <ConfigContext.Provider value={{ config, isLoading, error }}>{children}</ConfigContext.Provider>;
};

export const useConfig = (): ConfigContextValue => {
	const context = useContext(ConfigContext);
	if (!context) throw new Error("useConfig must be used within a ConfigProvider");
	return context;
};
