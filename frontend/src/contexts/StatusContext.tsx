import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { baseApi } from "../services/api/Base";

interface StatusData {
	maintenanceMode: boolean;
	maintenanceScheduledAt: string | null;
}

interface StatusContextValue extends StatusData {
	isLoading: boolean;
}

const STATUS_POLL_INTERVAL_MS = 30_000;

function isMaintenanceActive(scheduledAt: string | null): boolean {
	if (!scheduledAt) return false;
	const time = new Date(scheduledAt).getTime();
	return !isNaN(time) && time <= Date.now();
}

const StatusContext = createContext<StatusContextValue | undefined>(undefined);

export const StatusProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
	const [status, setStatus] = useState<StatusData>({
		maintenanceMode: false,
		maintenanceScheduledAt: null,
	});
	const [isLoading, setIsLoading] = useState(true);

	const fetchStatus = useCallback(async () => {
		try {
			const response = await baseApi.get("config/status", null);
			const scheduledAt: string | null = response.data.maintenance_scheduled_at || null;
			setStatus({
				maintenanceMode: isMaintenanceActive(scheduledAt),
				maintenanceScheduledAt: scheduledAt,
			});
		} catch {
			// Silently ignore — keep last known status
		} finally {
			setIsLoading(false);
		}
	}, []);

	useEffect(() => {
		fetchStatus();
		const interval = setInterval(fetchStatus, STATUS_POLL_INTERVAL_MS);
		return () => clearInterval(interval);
	}, [fetchStatus]);

	return (
		<StatusContext.Provider value={{ ...status, isLoading }}>
			{children}
		</StatusContext.Provider>
	);
};

export const useStatus = (): StatusContextValue => {
	const context = useContext(StatusContext);
	if (!context) throw new Error("useStatus must be used within a StatusProvider");
	return context;
};
