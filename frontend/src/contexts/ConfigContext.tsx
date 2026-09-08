import React, { JSX, ReactNode, useEffect, useState } from "react";
import { Config } from "../services/schemas/Base";
import { configApi } from "../services/api/Others";
import { ConfigContext } from "./ConfigContext.context";

export { useConfig } from "./ConfigContext.context";
export type { ConfigContextValue } from "./ConfigContext.context";

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
