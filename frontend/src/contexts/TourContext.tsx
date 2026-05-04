import React, { createContext, JSX, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { TourSnapshot, useDataContext } from "./DataContext";
import { scrapedJobApi } from "../services/api/Services";
import { useGlobalToast } from "../hooks/useNotificationToast";

interface TourContextType {
	startTour: (tourId: string) => Promise<void>;
	endTour: (completed: boolean) => Promise<void>;
	endTourAndContinue: (nextTourId: string) => void;
	activeTourId: string | null;
	isTourActive: boolean;
	isCleaningUp: boolean;
	completedTourIds: Set<string>;
	isTourSelectOpen: boolean;
	openTourSelect: () => void;
	closeTourSelect: () => void;
	toggleTourSelect: () => void;
	/** ID of the demo job created for the follow-up-email tour, null otherwise */
	demoJobId: number | null;
	/** ID of the demo scraped job created for the import-scraped-job tour, null otherwise */
	demoScrapedJobId: number | null;
	/** ID of the scraping filter created during the scraping-filters tour, null otherwise */
	demoScrapingFilterId: number | null;
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

function emptySnapshot(): TourSnapshot {
	return {
		jobIds: new Set(),
		companyIds: new Set(),
		personIds: new Set(),
		interviewIds: new Set(),
		jobApplicationUpdateIds: new Set(),
		scrapingFilterIds: new Set(),
		aggregatorIds: new Set(),
		keywordIds: new Set(),
		speculativeApplicationIds: new Set(),
	};
}

export function TourProvider({ children }: TourProviderProps): JSX.Element {
	const [activeTourId, setActiveTourId] = useState<string | null>(null);
	const [isTourSelectOpen, setIsTourSelectOpen] = useState<boolean>(false);
	const [isCleaningUp, setIsCleaningUp] = useState<boolean>(false);
	const [completedTourIds, setCompletedTourIds] = useState<Set<string>>(new Set());
	const [demoJobId, setDemoJobId] = useState<number | null>(null);
	const [demoScrapedJobId, setDemoScrapedJobId] = useState<number | null>(null);
	const [demoScrapingFilterId, setDemoScrapingFilterId] = useState<number | null>(null);
	const [pendingNextTourId, setPendingNextTourId] = useState<string | null>(null);
	const { currentUser, updateCurrentUser, token } = useAuth();
	const {
		jobs,
		companies,
		persons,
		interviews,
		jobApplicationUpdates,
		aggregators,
		keywords,
		scrapingFilters,
		speculativeApplications,
		addEntity,
		deleteEntity,
		setTourSnapshot,
	} = useDataContext();
	const { showToastError } = useGlobalToast();

	const navigate = useNavigate();
	const location = useLocation();
	const originPathRef = useRef<string | null>(null);

	const isTourActive: boolean = activeTourId !== null;

	// Snapshot of all entity IDs that existed before the tour started.
	// At cleanup time we diff against this to find (and delete) everything created during the tour.
	const preInteractiveSnapshot = useRef<TourSnapshot>(emptySnapshot());

	// Seed completed tours from preferences
	useEffect((): void => {
		if (!currentUser) return;
		const ids = new Set<string>(currentUser.preferences?.completed_tours ?? []);
		setCompletedTourIds(ids);
	}, [currentUser]);

	// Detect the scraping filter created during the scraping-filters tour
	useEffect((): void => {
		if (activeTourId !== "scraping-filters") return;
		if (demoScrapingFilterId !== null) return;
		const snapshot = preInteractiveSnapshot.current;
		const newFilter = scrapingFilters.find((f) => !snapshot.scrapingFilterIds.has(f.id));
		if (newFilter) setDemoScrapingFilterId(newFilter.id);
	}, [activeTourId, scrapingFilters, demoScrapingFilterId]);

	// Detect the job created by the user during the first-job tour
	useEffect((): void => {
		if (activeTourId !== "first-job") return;
		if (demoJobId !== null) return;
		const newJob = jobs.find((j) => !preInteractiveSnapshot.current.jobIds.has(j.id));
		if (newJob) setDemoJobId(newJob.id);
	}, [activeTourId, jobs, demoJobId]);

	const startTour = useCallback(
		async (tourId: string): Promise<void> => {
			try {
				originPathRef.current = location.pathname;

				// Capture a snapshot of every tracked entity that exists right now.
				// endTour will delete anything created after this point.
				preInteractiveSnapshot.current = {
					jobIds: new Set(jobs.map((j) => j.id)),
					companyIds: new Set(companies.map((c) => c.id)),
					personIds: new Set(persons.map((p) => p.id)),
					interviewIds: new Set(interviews.map((i) => i.id)),
					jobApplicationUpdateIds: new Set(jobApplicationUpdates.map((u) => u.id)),
					scrapingFilterIds: new Set(scrapingFilters.map((f) => f.id)),
					aggregatorIds: new Set(aggregators.map((a) => a.id)),
					keywordIds: new Set(keywords.map((k) => k.id)),
					speculativeApplicationIds: new Set(speculativeApplications.map((s) => s.id)),
				};

				if (tourId === "follow-up-email") {
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
						location: null,
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
					setDemoJobId(jobId);
					await addEntity("interview", {
						job_id: jobId,
						type: "video",
						date: new Date().toISOString(),
						location: null,
						note: null,
						attendance_type: "remote",
						interviewers: [interviewerId],
					});
				}

				if (tourId === "import-scraped-job") {
					const result = await scrapedJobApi.createTourDemo(token!);
					setDemoScrapedJobId(result.data.id);
				}

				if (tourId === "log-interview" || tourId === "log-update") {
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
						location: null,
						application_date: new Date().toISOString(),
						application_status: "applied",
						applied_via: null,
						application_note: null,
						application_aggregator_id: null,
						application_url: null,
						attendance_type: null,
						keywords: [],
						contacts: [],
					});
					setDemoJobId(jobResult.data.id);
				}

				if (tourId === "log-application") {
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
						location: null,
						application_date: null,
						application_status: null,
						applied_via: null,
						application_note: null,
						application_aggregator_id: null,
						application_url: null,
						attendance_type: null,
						keywords: [],
						contacts: [],
					});
					setDemoJobId(jobResult.data.id);
				}

				const ISOLATED_TOURS = new Set([
					"first-job",
					"follow-up-email",
					"scraping-filters",
					"log-interview",
					"log-update",
					"log-application",
					"add-contact",
					"speculative-applications",
				]);
				if (ISOLATED_TOURS.has(tourId)) setTourSnapshot(preInteractiveSnapshot.current);
				setIsTourSelectOpen(false);
				setActiveTourId(tourId);
			} catch (err: any) {
				showToastError(`Failed to start tour: ${err?.message ?? "Unknown error"}`);
			}
		},
		[
			jobs,
			companies,
			persons,
			interviews,
			jobApplicationUpdates,
			aggregators,
			keywords,
			scrapingFilters,
			speculativeApplications,
			addEntity,
			setTourSnapshot,
			token,
			location.pathname,
			showToastError,
		]
	);

	const endTour = useCallback(
		async (completed: boolean): Promise<void> => {
			const tourId = activeTourId;
			setActiveTourId(null);
			setTourSnapshot(null);

			document.querySelectorAll<HTMLElement>('.modal.show .btn-close').forEach(btn => btn.click());

			if (tourId === "follow-up-email" || tourId === "first-job" || tourId === "log-interview" || tourId === "log-update" || tourId === "log-application") {
				setDemoJobId(null);
			}

			if (tourId === "scraping-filters") {
				setDemoScrapingFilterId(null);
			}

			if (completed && tourId && !completedTourIds.has(tourId)) {
				const newIds = [...completedTourIds, tourId];
				setCompletedTourIds(new Set(newIds));
				void updateCurrentUser({ preferences: { completed_tours: newIds } });
			}

			// Generic cleanup: delete every entity created after the tour started.
			// Diff the current arrays against the pre-tour snapshot to find new IDs,
			// then delete in dependency order so foreign-key constraints are not violated.
			const snapshot = preInteractiveSnapshot.current;
			const newInterviewIds = interviews.map((i) => i.id).filter((id) => !snapshot.interviewIds.has(id));
			const newJobApplicationUpdateIds = jobApplicationUpdates
				.map((u) => u.id)
				.filter((id) => !snapshot.jobApplicationUpdateIds.has(id));
			const newJobIds = jobs.map((j) => j.id).filter((id) => !snapshot.jobIds.has(id));
			const newCompanyIds = companies.map((c) => c.id).filter((id) => !snapshot.companyIds.has(id));
			const newPersonIds = persons.map((p) => p.id).filter((id) => !snapshot.personIds.has(id));
			const newScrapingFilterIds = scrapingFilters
				.map((f) => f.id)
				.filter((id) => !snapshot.scrapingFilterIds.has(id));
			const newSpeculativeApplicationIds = speculativeApplications
				.map((s) => s.id)
				.filter((id) => !snapshot.speculativeApplicationIds.has(id));

			const hasNewEntities = [
				newInterviewIds,
				newJobApplicationUpdateIds,
				newJobIds,
				newCompanyIds,
				newPersonIds,
				newScrapingFilterIds,
				newSpeculativeApplicationIds,
			].some((arr) => arr.length > 0);

			if (hasNewEntities) {
				setIsCleaningUp(true);
				try {
					// Round 1: delete child entities first (interviews, updates depend on jobs)
					await Promise.all([
						...newInterviewIds.map((id) => deleteEntity("interview", id)),
						...newJobApplicationUpdateIds.map((id) => deleteEntity("jobApplicationUpdate", id)),
					]);
					// Round 2: delete jobs (depend on companies, locations, persons)
					await Promise.all(newJobIds.map((id) => deleteEntity("job", id)));
					// Round 3: delete base entities in parallel
					await Promise.all([
						...newCompanyIds.map((id) => deleteEntity("company", id)),
						...newPersonIds.map((id) => deleteEntity("person", id)),
						...newScrapingFilterIds.map((id) => deleteEntity("scrapingFilter", id)),
						...newSpeculativeApplicationIds.map((id) => deleteEntity("speculativeApplication", id)),
					]);
				} finally {
					setIsCleaningUp(false);
					preInteractiveSnapshot.current = emptySnapshot();
				}
			}

			// Delete the demo scraped job — not tracked in DataContext so handled separately
			if (tourId === "import-scraped-job") {
				const scrapedId = demoScrapedJobId;
				setDemoScrapedJobId(null);
				if (scrapedId !== null) {
					try {
						await scrapedJobApi.deleteTourDemo(scrapedId, token!);
					} catch {
						// Best-effort: the record may have already been deleted
					}
				}
			}

			if (originPathRef.current) {
				navigate(originPathRef.current);
				originPathRef.current = null;
			}
		},
		[
			activeTourId,
			completedTourIds,
			updateCurrentUser,
			jobs,
			companies,
			persons,
			interviews,
			jobApplicationUpdates,
			scrapingFilters,
			speculativeApplications,
			deleteEntity,
			setTourSnapshot,
			demoScrapedJobId,
			token,
			navigate,
		]
	);

	// Always points to the latest startTour so the pending-next-tour effect uses fresh state.
	const startTourRef = useRef(startTour);
	startTourRef.current = startTour;

	// After endTour cleanup completes, start the next tour with fresh entity state.
	// Using an effect (rather than Promise chaining) ensures startTour reads the correct
	// post-cleanup visibleData snapshot instead of stale filtered data from Tour A.
	useEffect((): void => {
		if (!isTourActive && !isCleaningUp && pendingNextTourId !== null) {
			const nextId = pendingNextTourId;
			setPendingNextTourId(null);
			void startTourRef.current(nextId);
		}
	}, [isTourActive, isCleaningUp, pendingNextTourId]);

	const endTourAndContinue = useCallback((nextTourId: string): void => {
		// Clear origin path so endTour doesn't navigate away before Tour B starts.
		originPathRef.current = null;
		setPendingNextTourId(nextTourId);
		void endTour(true);
	}, [endTour]);

	const openTourSelect = useCallback((): void => setIsTourSelectOpen(true), []);
	const closeTourSelect = useCallback((): void => setIsTourSelectOpen(false), []);
	const toggleTourSelect = useCallback((): void => setIsTourSelectOpen((prev) => !prev), []);

	return (
		<TourContext.Provider
			value={{
				startTour,
				endTour,
				endTourAndContinue,
				activeTourId,
				isTourActive,
				isCleaningUp,
				completedTourIds,
				isTourSelectOpen,
				openTourSelect,
				closeTourSelect,
				toggleTourSelect,
				demoJobId,
				demoScrapedJobId,
				demoScrapingFilterId,
			}}
		>
			{children}
		</TourContext.Provider>
	);
}
