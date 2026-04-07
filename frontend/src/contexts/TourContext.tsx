import React, { createContext, JSX, ReactNode, useCallback, useContext, useRef, useState } from "react";
import { useAuth } from "./AuthContext";
import { useDataContext } from "./DataContext";

interface TourContextType {
	startTour: () => void;
	endTour: (completed: boolean) => Promise<void>;
	isTourActive: boolean;
	isCleaningUp: boolean;
}

const TourContext = createContext<TourContextType | undefined>(undefined);

export function useTour(): TourContextType {
	const context = useContext(TourContext);
	if (context === undefined) {
		throw new Error("useTour must be used within a TourProvider");
	}
	return context;
}

interface TourProviderProps {
	children: ReactNode;
}

export function TourProvider({ children }: TourProviderProps): JSX.Element {
	const [isTourActive, setIsTourActive] = useState<boolean>(false);
	const [isCleaningUp, setIsCleaningUp] = useState<boolean>(false);
	const { currentUser, updateCurrentUser } = useAuth();
	const { jobs, companies, deleteEntity } = useDataContext();

	// Snapshot of IDs that existed before the tour started
	const preInteractiveJobIds = useRef<Set<number>>(new Set());
	const preInteractiveCompanyIds = useRef<Set<number>>(new Set());

	const startTour = useCallback((): void => {
		// Snapshot current IDs so we can diff at cleanup time
		preInteractiveJobIds.current = new Set(jobs.map((j) => j.id));
		preInteractiveCompanyIds.current = new Set(companies.map((c) => c.id));
		setIsTourActive(true);
	}, [jobs, companies]);

	const endTour = useCallback(
		async (completed: boolean): Promise<void> => {
			setIsTourActive(false);

			if (completed) {
				// Persist tour_completed preference
				if (currentUser && !currentUser.preferences?.tour_completed) {
					void updateCurrentUser({ preferences: { tour_completed: true } });
				}

				// Delete any jobs/companies created during the tour
				const newJobIds = jobs
					.map((j) => j.id)
					.filter((id) => !preInteractiveJobIds.current.has(id));
				const newCompanyIds = companies
					.map((c) => c.id)
					.filter((id) => !preInteractiveCompanyIds.current.has(id));

				if (newJobIds.length > 0 || newCompanyIds.length > 0) {
					setIsCleaningUp(true);
					try {
						await Promise.all([
							...newJobIds.map((id) => deleteEntity("job", id)),
							...newCompanyIds.map((id) => deleteEntity("company", id)),
						]);
					} finally {
						setIsCleaningUp(false);
					}
				}
			}
		},
		[currentUser, updateCurrentUser, jobs, companies, deleteEntity]
	);

	return (
		<TourContext.Provider value={{ startTour, endTour, isTourActive, isCleaningUp }}>
			{children}
		</TourContext.Provider>
	);
}
