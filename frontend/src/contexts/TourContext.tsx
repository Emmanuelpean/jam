import React, { createContext, JSX, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useAuth } from "./AuthContext";
import { useDataContext } from "./DataContext";

interface TourContextType {
	startTour: (tourId: string) => void;
	endTour: (completed: boolean) => Promise<void>;
	activeTourId: string | null;
	isTourActive: boolean;
	isCleaningUp: boolean;
	completedTourIds: Set<string>;
	isTourSelectOpen: boolean;
	openTourSelect: () => void;
	closeTourSelect: () => void;
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
	const [activeTourId, setActiveTourId] = useState<string | null>(null);
	const [isTourSelectOpen, setIsTourSelectOpen] = useState<boolean>(false);
	const [isCleaningUp, setIsCleaningUp] = useState<boolean>(false);
	const [completedTourIds, setCompletedTourIds] = useState<Set<string>>(new Set());
	const { currentUser, updateCurrentUser } = useAuth();
	const { jobs, companies, deleteEntity } = useDataContext();

	const isTourActive: boolean = activeTourId !== null;

	// Snapshot of IDs that existed before the tour started
	const preInteractiveJobIds = useRef<Set<number>>(new Set());
	const preInteractiveCompanyIds = useRef<Set<number>>(new Set());

	// Seed completed tours from preferences
	useEffect((): void => {
		if (!currentUser) return;
		const ids = new Set<string>(currentUser.preferences?.completed_tours ?? []);
		setCompletedTourIds(ids);
	}, [currentUser]);

	const startTour = useCallback(
		(tourId: string): void => {
			preInteractiveJobIds.current = new Set(jobs.map((j) => j.id));
			preInteractiveCompanyIds.current = new Set(companies.map((c) => c.id));
			setIsTourSelectOpen(false);
			setActiveTourId(tourId);
		},
		[jobs, companies]
	);

	const endTour = useCallback(
		async (completed: boolean): Promise<void> => {
			const tourId = activeTourId;
			setActiveTourId(null);

			if (completed && tourId) {
				if (!completedTourIds.has(tourId)) {
					const newIds = [...completedTourIds, tourId];
					setCompletedTourIds(new Set(newIds));
					void updateCurrentUser({ preferences: { completed_tours: newIds } });
				}

				// Clean up test data created during the first-job tour
				if (tourId === "first-job") {
					const newJobIds = jobs.map((j) => j.id).filter((id) => !preInteractiveJobIds.current.has(id));
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
			}
		},
		[activeTourId, completedTourIds, currentUser, updateCurrentUser, jobs, companies, deleteEntity]
	);

	const openTourSelect = useCallback((): void => setIsTourSelectOpen(true), []);
	const closeTourSelect = useCallback((): void => setIsTourSelectOpen(false), []);

	return (
		<TourContext.Provider
			value={{
				startTour,
				endTour,
				activeTourId,
				isTourActive,
				isCleaningUp,
				completedTourIds,
				isTourSelectOpen,
				openTourSelect,
				closeTourSelect,
			}}
		>
			{children}
		</TourContext.Provider>
	);
}
