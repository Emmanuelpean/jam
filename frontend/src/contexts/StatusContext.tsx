import React, { JSX, ReactNode, useCallback, useEffect, useState } from "react";
import { Status } from "../services/schemas/Base";
import { configApi } from "../services/api/Others";
import { StatusContext } from "./StatusContext.context";

export { useStatus } from "./StatusContext.context";
export type { StatusContextValue } from "./StatusContext.context";

const STATUS_POLL_INTERVAL_MS = 30_000;
const TEST_MODE_POLL_INTERVAL_MS = 2_000;

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
