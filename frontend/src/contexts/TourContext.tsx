import React, { createContext, JSX, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { useDataContext } from "./DataContext";

interface TourContextType {
	startTour: (tourId: string) => Promise<void>;
	endTour: (completed: boolean) => Promise<void>;
	activeTourId: string | null;
	isTourActive: boolean;
	isCleaningUp: boolean;
	completedTourIds: Set<string>;
	isTourSelectOpen: boolean;
	openTourSelect: () => void;
	closeTourSelect: () => void;
	/** ID of the demo job created for the follow-up-email tour, null otherwise */
	demoJobId: number | null;
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
	const [demoJobId, setDemoJobId] = useState<number | null>(null);
	const { currentUser, updateCurrentUser } = useAuth();
	const { jobs, companies, addEntity, deleteEntity, setDemoFilter } = useDataContext();

	const navigate = useNavigate();
	const location = useLocation();
	const originPathRef = useRef<string | null>(null);

	const isTourActive: boolean = activeTourId !== null;

	// Snapshot of IDs that existed before the first-job tour started
	const preInteractiveJobIds = useRef<Set<number>>(new Set());
	const preInteractiveCompanyIds = useRef<Set<number>>(new Set());

	// IDs of entities created for the follow-up-email tour demo data
	const demoEntityIds = useRef<{ personIds: number[]; jobId: number | null; interviewId: number | null }>({
		personIds: [],
		jobId: null,
		interviewId: null,
	});

	// Seed completed tours from preferences
	useEffect((): void => {
		if (!currentUser) return;
		const ids = new Set<string>(currentUser.preferences?.completed_tours ?? []);
		setCompletedTourIds(ids);
	}, [currentUser]);

	const startTour = useCallback(
		async (tourId: string): Promise<void> => {
			originPathRef.current = location.pathname;
			preInteractiveJobIds.current = new Set(jobs.map((j) => j.id));
			preInteractiveCompanyIds.current = new Set(companies.map((c) => c.id));

			if (tourId === "follow-up-email") {
				demoEntityIds.current = { personIds: [], jobId: null, interviewId: null };

				const [personResult, interviewerResult] = await Promise.all([
					addEntity("person", {
						first_name: "Alex",
						last_name: "Johnson",
						email: "alex.johnson@example.com",
						phone: null,
						role: "Hiring Manager",
						linkedin_url: null,
						company_id: null,
						is_recruiter: false,
					}),
					addEntity("person", {
						first_name: "Sarah",
						last_name: "Mitchell",
						email: "sarah.mitchell@example.com",
						phone: null,
						role: "Engineering Manager",
						linkedin_url: null,
						company_id: null,
						is_recruiter: false,
					}),
				]);

				const personId: number = personResult.data.id;
				const interviewerId: number = interviewerResult.data.id;
				demoEntityIds.current.personIds = [personId, interviewerId];

				const jobResult = await addEntity("job", {
					title: "Software Engineer",
					is_favourite: false,
					description: null,
					note: null,
					url: null,
					salary_min: null,
					salary_max: null,
					salary_currency: null,
					personal_rating: null,
					deadline: null,
					company_id: null,
					source_aggregator_id: null,
					source_type: null,
					recruiter_id: null,
					recruitment_company_id: null,
					location_id: null,
					application_date: new Date().toISOString(),
					application_status: "applied",
					applied_via: null,
					application_note: null,
					application_aggregator_id: null,
					application_url: null,
					attendance_type: null,
					keywords: [],
					contacts: [personId],
				});

				const jobId: number = jobResult.data.id;
				demoEntityIds.current.jobId = jobId;
				setDemoJobId(jobId);
				setDemoFilter({ jobIds: [jobId], personIds: [personId, interviewerId] });

				const interviewResult = await addEntity("interview", {
					job_id: jobId,
					type: "video",
					date: new Date().toISOString(),
					location_id: null,
					note: null,
					attendance_type: "remote",
					interviewers: [interviewerId],
				});

				demoEntityIds.current.interviewId = interviewResult.data.id;
			}

			setIsTourSelectOpen(false);
			setActiveTourId(tourId);
		},
		[jobs, companies, addEntity, setDemoFilter, location.pathname]
	);

	const endTour = useCallback(
		async (completed: boolean): Promise<void> => {
			const tourId = activeTourId;
			setActiveTourId(null);

			// Always clear the demo filter when the tour ends (completed or skipped)
			if (tourId === "follow-up-email") setDemoFilter(null);

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

				// Delete demo entities created for the follow-up-email tour
				if (tourId === "follow-up-email") {
					const { personIds, jobId, interviewId } = demoEntityIds.current;
					setIsCleaningUp(true);
					try {
						const deletions: Promise<void>[] = [];
						if (interviewId !== null) deletions.push(deleteEntity("interview", interviewId));
						if (jobId !== null) deletions.push(deleteEntity("job", jobId));
						await Promise.all(deletions);
						await Promise.all(personIds.map((id) => deleteEntity("person", id)));
					} finally {
						setIsCleaningUp(false);
						demoEntityIds.current = { personIds: [], jobId: null, interviewId: null };
						setDemoJobId(null);
						setDemoFilter(null);
					}
				}
			}

			if (originPathRef.current) {
				navigate(originPathRef.current);
				originPathRef.current = null;
			}
		},
		[activeTourId, completedTourIds, currentUser, updateCurrentUser, jobs, companies, deleteEntity, setDemoFilter, navigate]
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
				demoJobId,
			}}
		>
			{children}
		</TourContext.Provider>
	);
}
