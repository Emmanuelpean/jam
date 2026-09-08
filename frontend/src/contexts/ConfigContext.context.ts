import { createContext, useContext } from "react";
import { Config } from "../services/schemas/Base";

export interface ConfigContextValue {
	config: Config | null;
	isLoading: boolean;
	error: Error | null;
}

export const ConfigContext = createContext<ConfigContextValue | undefined>(undefined);

export const useConfig = (): ConfigContextValue => {
	const context: ConfigContextValue | undefined = useContext(ConfigContext);
	if (!context) throw new Error("useConfig must be used within a ConfigProvider");
	return context;
};
