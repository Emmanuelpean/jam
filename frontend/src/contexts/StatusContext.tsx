import React, { createContext, JSX, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { Status } from "../services/schemas/Base";
import { configApi } from "../services/api/Others";

export interface StatusContextValue extends Status {
	isLoading: boolean;
}

const STATUS_POLL_INTERVAL_MS = 30_000;
const TEST_MODE_POLL_INTERVAL_MS = 2_000;

const StatusContext = createContext<StatusContextValue | undefined>(undefined);

export const StatusProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const [status, setStatus] = useState<Status>({ maintenance_scheduled_at: null, test_mode: false });
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const [pollInterval, setPollInterval] = useState<number>(STATUS_POLL_INTERVAL_MS);

	const fetchStatus = useCallback(async (): Promise<void> => {
		try {
			const status: Status = await configApi.getStatus();
			if (status.test_mode) {
				setPollInterval(TEST_MODE_POLL_INTERVAL_MS);
			}
			setStatus(status);
		} catch {
			// Silently ignore — keep last known status
		} finally {
			setIsLoading(false);
		}
	}, []);

	useEffect((): void => {
		void fetchStatus();
	}, [fetchStatus]);

	useEffect(() => {
		const interval = setInterval(fetchStatus, pollInterval);
		return () => clearInterval(interval);
	}, [fetchStatus, pollInterval]);

	return <StatusContext.Provider value={{ ...status, isLoading }}>{children}</StatusContext.Provider>;
};

export const useStatus = (): StatusContextValue => {
	const context: StatusContextValue | undefined = useContext(StatusContext);
	if (!context) throw new Error("useStatus must be used within a StatusProvider");
	return context;
};
