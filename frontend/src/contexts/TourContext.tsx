import React, { createContext, JSX, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { TourSnapshot, useDataContext } from "./DataContext";
import { scrapedJobApi } from "../services/api/Services";
import { useGlobalToast } from "../hooks/useNotificationToast";

interface TourContextType {
	startTour: (tourId: string) => Promise<void>;
	endTour: (completed: boolean, keepUserData?: boolean) => Promise<void>;
	endTourAndContinue: (nextTourId: string, keepUserData?: boolean) => void;
	activeTourId: string | null;
	isTourActive: boolean;
	isCleaningUp: boolean;
	completedTourIds: Set<string>;
	isTourSelectOpen: boolean;
	openTourSelect: () => void;
	closeTourSelect: () => void;
	toggleTourSelect: () => void;
	/** True when the user has created entities during the tour that can meaningfully be kept */
	hasUserCreatedData: boolean;
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

	// IDs of entities JAM created automatically during tour setup — always cleaned up regardless
	// of whether the user chooses to keep their own data.
	const jamCreatedIds = useRef<TourSnapshot>(emptySnapshot());

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

	// True whenever the user has created at least one top-level entity during the tour
	// that can meaningfully be kept (not a child of a JAM-created entity that will be deleted).
	const hasUserCreatedData = useMemo((): boolean => {
		if (!isTourActive) return false;
		const snapshot = preInteractiveSnapshot.current;
		const jamIds = jamCreatedIds.current;
		return (
			jobs.some((j) => !snapshot.jobIds.has(j.id) && !jamIds.jobIds.has(j.id)) ||
			companies.some((c) => !snapshot.companyIds.has(c.id) && !jamIds.companyIds.has(c.id)) ||
			persons.some((p) => !snapshot.personIds.has(p.id) && !jamIds.personIds.has(p.id)) ||
			scrapingFilters.some((f) => !snapshot.scrapingFilterIds.has(f.id) && !jamIds.scrapingFilterIds.has(f.id)) ||
			speculativeApplications.some(
				(s) =>
					!snapshot.speculativeApplicationIds.has(s.id) &&
					!jamIds.speculativeApplicationIds.has(s.id) &&
					!jamIds.companyIds.has(s.company_id),
			)
		);
	}, [isTourActive, jobs, companies, persons, scrapingFilters, speculativeApplications]);

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
				jamCreatedIds.current = emptySnapshot();

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
					const interviewResult = await addEntity("interview", {
						job_id: jobId,
						type: "video",
						date: new Date().toISOString(),
						location: null,
						note: null,
						attendance_type: "remote",
						interviewers: [interviewerId],
					});

					jamCreatedIds.current.personIds.add(personId);
					jamCreatedIds.current.personIds.add(interviewerId);
					jamCreatedIds.current.jobIds.add(jobId);
					jamCreatedIds.current.interviewIds.add(interviewResult.data.id);
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
					jamCreatedIds.current.jobIds.add(jobResult.data.id);
				}

				if (tourId === "speculative-applications") {
					const [companyResult1, companyResult2] = await Promise.all([
						addEntity("company", { name: "Anthropic", website: null, note: null, location: null }),
						addEntity("company", { name: "DeepMind", website: null, note: null, location: null }),
					]);
					jamCreatedIds.current.companyIds.add(companyResult1.data.id);
					jamCreatedIds.current.companyIds.add(companyResult2.data.id);
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
					jamCreatedIds.current.jobIds.add(jobResult.data.id);
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
		async (completed: boolean, keepUserData?: boolean): Promise<void> => {
			const tourId = activeTourId;
			setActiveTourId(null);
			setTourSnapshot(null);

			document.querySelectorAll<HTMLElement>('.modal.show').forEach((modal) => {
				const cancelBtn = modal.querySelector<HTMLElement>('[id$="-cancel-button"]');
				(cancelBtn ?? modal.querySelector<HTMLElement>('.btn-close'))?.click();
			});

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

			const snapshot = preInteractiveSnapshot.current;
			const jamIds = jamCreatedIds.current;

			// Compute all new IDs created since the tour started
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

			// User-created speculative applications whose company is also user-created can be kept.
			// Those whose company is JAM-created will be cascade-deleted when that company is removed,
			// so they are always cleaned up to keep frontend state consistent.
			const userSAIds = newSpeculativeApplicationIds.filter((id) => !jamIds.speculativeApplicationIds.has(id));
			const keepableSAIds = userSAIds.filter((id) => {
				const sa = speculativeApplications.find((s) => s.id === id);
				return !sa || !jamIds.companyIds.has(sa.company_id);
			});
			const cascadedSAIds = userSAIds.filter((id) => !keepableSAIds.includes(id));

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
					// Round 1: delete child entities (interviews, job app updates) — always cleaned up
					// regardless of keep/delete choice, since they depend on jobs that may be removed.
					await Promise.all([
						...newInterviewIds.map((id) => deleteEntity("interview", id)),
						...newJobApplicationUpdateIds.map((id) => deleteEntity("jobApplicationUpdate", id)),
					]);
					// Round 2: delete jobs — only JAM-created ones when user chose to keep their data
					const jobsToDelete = keepUserData
						? newJobIds.filter((id) => jamIds.jobIds.has(id))
						: newJobIds;
					await Promise.all(jobsToDelete.map((id) => deleteEntity("job", id)));
					// Round 3: delete speculative applications before companies (company_id FK has CASCADE)
					const sAsToDelete = [
						...newSpeculativeApplicationIds.filter((id) => jamIds.speculativeApplicationIds.has(id)),
						...cascadedSAIds,
						...(keepUserData ? [] : keepableSAIds),
					];
					await Promise.all(sAsToDelete.map((id) => deleteEntity("speculativeApplication", id)));
					// Round 4: delete base entities — only JAM-created ones when user chose to keep their data
					const companiesToDelete = keepUserData
						? newCompanyIds.filter((id) => jamIds.companyIds.has(id))
						: newCompanyIds;
					const personsToDelete = keepUserData
						? newPersonIds.filter((id) => jamIds.personIds.has(id))
						: newPersonIds;
					const filtersToDelete = keepUserData
						? newScrapingFilterIds.filter((id) => jamIds.scrapingFilterIds.has(id))
						: newScrapingFilterIds;
					await Promise.all([
						...companiesToDelete.map((id) => deleteEntity("company", id)),
						...personsToDelete.map((id) => deleteEntity("person", id)),
						...filtersToDelete.map((id) => deleteEntity("scrapingFilter", id)),
					]);
				} finally {
					setIsCleaningUp(false);
					preInteractiveSnapshot.current = emptySnapshot();
					jamCreatedIds.current = emptySnapshot();
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

	const endTourAndContinue = useCallback((nextTourId: string, keepUserData?: boolean): void => {
		// Clear origin path so endTour doesn't navigate away before Tour B starts.
		originPathRef.current = null;
		setPendingNextTourId(nextTourId);
		void endTour(true, keepUserData ?? false);
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
				hasUserCreatedData,
				demoJobId,
				demoScrapedJobId,
				demoScrapingFilterId,
			}}
		>
			{children}
		</TourContext.Provider>
	);
}
