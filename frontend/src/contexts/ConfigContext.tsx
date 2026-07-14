import React, { createContext, JSX, ReactNode, useContext, useEffect, useState } from "react";
import { Config } from "../services/schemas/Base";
import { configApi } from "../services/api/Others";

export interface ConfigContextValue {
	config: Config | null;
	isLoading: boolean;
	error: Error | null;
}

const ConfigContext = createContext<ConfigContextValue | undefined>(undefined);

export const ConfigProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const [config, setConfig] = useState<Config | null>(null);
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const [error, setError] = useState<Error | null>(null);

	useEffect(() => {
		const fetchConfig = async (): Promise<void> => {
			try {
				const config: Config = await configApi.get();
				setConfig(config);
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
	const context: ConfigContextValue | undefined = useContext(ConfigContext);
	if (!context) throw new Error("useConfig must be used within a ConfigProvider");
	return context;
};
