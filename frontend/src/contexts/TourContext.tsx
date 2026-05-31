import React, {
	createContext,
	JSX,
	ReactNode,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useRef,
	useState,
} from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { useDataContext } from "./DataContext";
import { useProgressOverlay } from "./useProgressOverlayContext";
import { scrapedJobApi } from "../services/api/Services";
import { useGlobalToast } from "../hooks/useNotificationToast";
import { tourApi } from "../services/api/Others";
import { EnrichedJobData, SpeculativeApplicationData } from "../services/schemas/DataTables";
import { ScrapingFilterData } from "../services/schemas/Services";

export interface TourSnapshot {
	jobIds: Set<number>;
	companyIds: Set<number>;
	personIds: Set<number>;
	interviewIds: Set<number>;
	jobApplicationUpdateIds: Set<number>;
	scrapingFilterIds: Set<number>;
	aggregatorIds: Set<number>;
	keywordIds: Set<number>;
	speculativeApplicationIds: Set<number>;
}

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
	/** ID of the demo job email for the import-scraped-job tour, null otherwise */
	demoJobEmailId: number | null;
	/** ID of the scraping filter created during the scraping-filters tour, null otherwise */
	demoScrapingFilterId: number | null;
	/** When set, the context menu should only show these actions on tour-targeted rows */
	allowedContextMenuActions: string[] | null;
	setAllowedContextMenuActions: (actions: string[] | null) => void;
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
	const [demoJobEmailId, setDemoJobEmailId] = useState<number | null>(null);
	const [demoScrapingFilterId, setDemoScrapingFilterId] = useState<number | null>(null);
	const [pendingNextTourId, setPendingNextTourId] = useState<string | null>(null);
	const [allowedContextMenuActions, setAllowedContextMenuActions] = useState<string[] | null>(null);
	const { currentUser, updateCurrentUser, token } = useAuth();
	const {
		jobs,
		companies,
		persons,
		interviews,
		jobApplicationUpdates,
		aggregators,
		keywords,
		scrapingExclusionFilters,
		speculativeApplications,
		addEntity,
		updateEntity,
		deleteEntity,
		setIsInTour,
	} = useDataContext();
	const { showToastError } = useGlobalToast();
	const { showProgress, hideProgress } = useProgressOverlay();

	const navigate = useNavigate();
	const location = useLocation();
	const originPathRef = useRef<string | null>(null);

	const isTourActive: boolean = activeTourId !== null;

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
		const newFilter: ScrapingFilterData | undefined = scrapingExclusionFilters.find(
			(f: ScrapingFilterData): boolean => !jamCreatedIds.current.scrapingFilterIds.has(f.id)
		);
		if (newFilter) setDemoScrapingFilterId(newFilter.id);
	}, [activeTourId, scrapingExclusionFilters, demoScrapingFilterId]);

	// Detect the job created by the user during the first-job tour
	useEffect((): void => {
		if (activeTourId !== "first-job") return;
		if (demoJobId !== null) return;
		const newJob: EnrichedJobData | undefined = jobs.find(
			(j: EnrichedJobData): boolean => !jamCreatedIds.current.jobIds.has(j.id)
		);
		if (newJob) setDemoJobId(newJob.id);
	}, [activeTourId, jobs, demoJobId]);

	// True whenever the user has created at least one top-level entity during the tour
	// that can meaningfully be kept (not a child of a JAM-created entity that will be deleted).
	// During a tour, all visible entities have is_tour=true, so we just check against jamCreatedIds.
	const hasUserCreatedData = useMemo((): boolean => {
		if (!isTourActive) return false;
		const jamIds = jamCreatedIds.current;
		return (
			jobs.some((j) => !jamIds.jobIds.has(j.id)) ||
			companies.some((c) => !jamIds.companyIds.has(c.id)) ||
			persons.some((p) => !jamIds.personIds.has(p.id)) ||
			keywords.some((k) => !jamIds.keywordIds.has(k.id)) ||
			scrapingExclusionFilters.some((f) => !jamIds.scrapingFilterIds.has(f.id)) ||
			speculativeApplications.some(
				(s) => !jamIds.speculativeApplicationIds.has(s.id) && !jamIds.companyIds.has(s.company_id)
			)
		);
	}, [isTourActive, jobs, companies, persons, keywords, scrapingExclusionFilters, speculativeApplications]);

	const startTour = useCallback(
		async (tourId: string): Promise<void> => {
			try {
				originPathRef.current = location.pathname;
				await tourApi.clearAll(token!);

				jamCreatedIds.current = emptySnapshot();

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
				if (ISOLATED_TOURS.has(tourId)) setIsInTour(true);

				showProgress("Setting up tour...");
				try {
					if (tourId === "follow-up-email") {
						const [personResult, interviewerResult] = await Promise.all([
							addEntity("person", {
								first_name: "Alex",
								last_name: "Johnson",
								email: "alex.johnson@novatech.io",
								phone: "+44 7911 123456",
								role: "Hiring Manager",
								linkedin_url: "https://www.linkedin.com/in/alex-johnson",
								is_tour: true,
							}),
							addEntity("person", {
								first_name: "Sarah",
								last_name: "Mitchell",
								email: "sarah.mitchell@novatech.io",
								phone: "+44 7911 234567",
								role: "Engineering Manager",
								linkedin_url: "https://www.linkedin.com/in/sarah-mitchell",
								is_tour: true,
							}),
						]);

						const personId: number = personResult.data.id;
						const interviewerId: number = interviewerResult.data.id;

						const jobResult = await addEntity("job", {
							title: "Software Engineer",
							url: "https://www.novatech.io/careers/software-engineer",
							application_date: new Date().toISOString(),
							application_status: "applied",
							is_tour: true,
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
							is_tour: true,
						});

						jamCreatedIds.current.personIds.add(personId);
						jamCreatedIds.current.personIds.add(interviewerId);
						jamCreatedIds.current.jobIds.add(jobId);
						jamCreatedIds.current.interviewIds.add(interviewResult.data.id);
					}

					if (tourId === "import-scraped-job") {
						const scrapedResult = await scrapedJobApi.createTourDemo(token!);
						setDemoScrapedJobId(scrapedResult.data.id);
						setDemoJobEmailId(scrapedResult.data.emails[0] ?? null);
					}

					if (tourId === "log-interview" || tourId === "log-update") {
						const companyResult = await addEntity("company", {
							name: "Meridian Labs",
							website: "https://www.meridianlabs.com",
							note: "Product-led growth startup specialising in data analytics. ~80 employees.",
							location: null,
							is_tour: true,
						});
						const companyId: number = companyResult.data.id;
						jamCreatedIds.current.companyIds.add(companyId);

						const jobResult = await addEntity("job", {
							title: "Software Engineer",
							is_favourite: false,
							is_tour: true,
							description: null,
							note: null,
							url: "https://www.meridianlabs.com/jobs/software-engineer",
							salary_min: 65000,
							salary_max: 85000,
							salary_currency: null,
							personal_rating: null,
							deadline: null,
							company_id: companyId,
							source_aggregator_id: null,
							source_type: null,
							recruiter_id: null,
							recruitment_company_id: null,
							location: "London, UK",
							application_date: new Date().toISOString(),
							application_status: "applied",
							applied_via: null,
							application_note: null,
							application_aggregator_id: null,
							application_url: null,
							attendance_type: "hybrid",
							keywords: [],
							contacts: [],
						});
						setDemoJobId(jobResult.data.id);
						jamCreatedIds.current.jobIds.add(jobResult.data.id);
					}

					if (tourId === "first-job") {
						const [c1, c2] = await Promise.all([
							addEntity("company", {
								name: "Acme Corp",
								url: "https://www.acmecorp.com",
								description:
									"B2B SaaS company building HR tooling. Series B, ~200 employees, offices in London and Manchester.",
								is_tour: true,
							}),
							addEntity("company", {
								name: "Globex Inc",
								url: "https://www.globexinc.com",
								description:
									"Enterprise software solutions provider. Clients across finance and logistics in the UK and Europe.",
								is_tour: true,
							}),
						]);
						jamCreatedIds.current.companyIds.add(c1.data.id);
						jamCreatedIds.current.companyIds.add(c2.data.id);

						const [p1, p2, k1, k2, a1, a2] = await Promise.all([
							addEntity("person", {
								first_name: "Emma",
								last_name: "Williams",
								email: "emma.williams@acmecorp.com",
								phone: "+44 7700 900123",
								role: "Recruiter",
								linkedin_url: "https://www.linkedin.com/in/emma-williams",
								company_id: c1.data.id,
								is_recruiter: true,
								is_tour: true,
							}),
							addEntity("person", {
								first_name: "David",
								last_name: "Chen",
								email: "david.chen@acmecorp.com",
								phone: "+44 7700 900456",
								role: "Hiring Manager",
								linkedin_url: "https://www.linkedin.com/in/david-chen",
								company_id: c1.data.id,
								is_recruiter: false,
								is_tour: true,
							}),
							addEntity("keyword", { name: "TypeScript", is_tour: true }),
							addEntity("keyword", { name: "React.js", is_tour: true }),
							addEntity("aggregator", {
								name: "LinkedIn Jobs",
								url: "https://www.linkedin.com/jobs/jam-tour",
								is_tour: true,
							}),
							addEntity("aggregator", {
								name: "Indeed",
								url: "https://www.indeed.com/jam-tour",
								is_tour: true,
							}),
						]);
						jamCreatedIds.current.personIds.add(p1.data.id);
						jamCreatedIds.current.personIds.add(p2.data.id);
						jamCreatedIds.current.keywordIds.add(k1.data.id);
						jamCreatedIds.current.keywordIds.add(k2.data.id);
						jamCreatedIds.current.aggregatorIds.add(a1.data.id);
						jamCreatedIds.current.aggregatorIds.add(a2.data.id);
					}

					if (tourId === "speculative-applications") {
						const [companyResult1, companyResult2] = await Promise.all([
							addEntity("company", {
								name: "Anthropic",
								website: "https://www.anthropic.com",
								note: "AI safety company. Builds Claude. Based in San Francisco — remote-friendly for UK applicants.",
								location: null,
								is_tour: true,
							}),
							addEntity("company", {
								name: "DeepMind",
								website: "https://www.deepmind.com",
								note: "AI research lab, part of Google. Main office in London (King's Cross). World-class research team.",
								location: null,
								is_tour: true,
							}),
						]);
						jamCreatedIds.current.companyIds.add(companyResult1.data.id);
						jamCreatedIds.current.companyIds.add(companyResult2.data.id);
					}

					if (tourId === "log-application") {
						const companyResult = await addEntity("company", {
							name: "Meridian Labs",
							website: "https://www.meridianlabs.com",
							note: "Product-led growth startup specialising in data analytics. ~80 employees.",
							location: null,
							is_tour: true,
						});
						const companyId: number = companyResult.data.id;
						jamCreatedIds.current.companyIds.add(companyId);

						const jobResult = await addEntity("job", {
							title: "Software Engineer",
							is_favourite: false,
							is_tour: true,
							description: null,
							note: null,
							url: "https://www.meridianlabs.com/jobs/software-engineer",
							salary_min: 65000,
							salary_max: 85000,
							salary_currency: null,
							personal_rating: null,
							deadline: null,
							company_id: companyId,
							source_aggregator_id: null,
							source_type: null,
							recruiter_id: null,
							recruitment_company_id: null,
							location: "London, UK",
							application_date: null,
							application_status: null,
							applied_via: null,
							application_note: null,
							application_aggregator_id: null,
							application_url: null,
							attendance_type: "hybrid",
							keywords: [],
							contacts: [],
						});
						setDemoJobId(jobResult.data.id);
						jamCreatedIds.current.jobIds.add(jobResult.data.id);
					}
				} finally {
					hideProgress();
				}

				setIsTourSelectOpen(false);
				setActiveTourId(tourId);
			} catch (err: any) {
				showToastError(`Failed to start tour: ${err?.message ?? "Unknown error"}`);
			}
		},
		[addEntity, setIsInTour, token, location.pathname, showToastError, showProgress, hideProgress]
	);

	const endTour = useCallback(
		async (completed: boolean, keepUserData?: boolean): Promise<void> => {
			const tourId: string | null = activeTourId;
			setActiveTourId(null);
			setIsInTour(false);

			document.querySelectorAll<HTMLElement>(".modal.show").forEach((modal) => {
				const cancelBtn = modal.querySelector<HTMLElement>('[id$="-cancel-button"]');
				(cancelBtn ?? modal.querySelector<HTMLElement>(".btn-close"))?.click();
			});

			if (
				tourId === "follow-up-email" ||
				tourId === "first-job" ||
				tourId === "log-interview" ||
				tourId === "log-update" ||
				tourId === "log-application"
			) {
				setDemoJobId(null);
			}

			if (tourId === "import-scraped-job") {
				setDemoJobEmailId(null);
			}

			if (tourId === "scraping-filters") {
				setDemoScrapingFilterId(null);
			}

			if (completed && tourId && !completedTourIds.has(tourId)) {
				const newIds: string[] = [...completedTourIds, tourId];
				setCompletedTourIds(new Set(newIds));
				void updateCurrentUser({ preferences: { completed_tours: newIds } });
			}

			// During a tour all visible entities have is_tour=true (setIsInTour(false) was called above
			// but the closure still holds the pre-update arrays). jamCreatedIds distinguishes JAM-
			// seeded entities from ones the user created themselves.
			const jamIds: TourSnapshot = jamCreatedIds.current;
			const hasNewEntities: boolean =
				jobs.length > 0 ||
				companies.length > 0 ||
				persons.length > 0 ||
				aggregators.length > 0 ||
				keywords.length > 0 ||
				scrapingExclusionFilters.length > 0 ||
				interviews.length > 0 ||
				jobApplicationUpdates.length > 0 ||
				speculativeApplications.length > 0;

			if (hasNewEntities) {
				setIsCleaningUp(true);
				try {
					// Round 1: always delete child entities — they depend on jobs that may be removed.
					await Promise.all([
						...interviews.map((i) => deleteEntity("interview", i.id)),
						...jobApplicationUpdates.map((u) => deleteEntity("jobApplicationUpdate", u.id)),
					]);

					if (keepUserData) {
						// Patch user-created entities to is_tour=false so they survive clearAll.
						// SAs under JAM-created companies are cascade-deleted with their company — skip them.
						const keepableSAs: SpeculativeApplicationData[] = speculativeApplications.filter(
							(s) => !jamIds.speculativeApplicationIds.has(s.id) && !jamIds.companyIds.has(s.company_id)
						);
						await Promise.all([
							...jobs
								.filter((j) => !jamIds.jobIds.has(j.id))
								.map((j) => updateEntity("job", j.id, { is_tour: false })),
							...companies
								.filter((c) => !jamIds.companyIds.has(c.id))
								.map((c) => updateEntity("company", c.id, { is_tour: false })),
							...persons
								.filter((p) => !jamIds.personIds.has(p.id))
								.map((p) => updateEntity("person", p.id, { is_tour: false })),
							...aggregators
								.filter((a) => !jamIds.aggregatorIds.has(a.id))
								.map((a) => updateEntity("aggregator", a.id, { is_tour: false })),
							...keywords
								.filter((k) => !jamIds.keywordIds.has(k.id))
								.map((k) => updateEntity("keyword", k.id, { is_tour: false })),
							...scrapingExclusionFilters
								.filter((f) => !jamIds.scrapingFilterIds.has(f.id))
								.map((f) => updateEntity("scrapingExclusionFilter", f.id, { is_tour: false })),
							...keepableSAs.map((s) => updateEntity("speculativeApplication", s.id, { is_tour: false })),
						]);
						// Delete JAM SAs before JAM companies (FK order)
						await Promise.all(
							speculativeApplications
								.filter((s) => jamIds.speculativeApplicationIds.has(s.id))
								.map((s) => deleteEntity("speculativeApplication", s.id))
						);
						await Promise.all([
							...jobs.filter((j) => jamIds.jobIds.has(j.id)).map((j) => deleteEntity("job", j.id)),
							...companies
								.filter((c) => jamIds.companyIds.has(c.id))
								.map((c) => deleteEntity("company", c.id)),
							...persons
								.filter((p) => jamIds.personIds.has(p.id))
								.map((p) => deleteEntity("person", p.id)),
							...aggregators
								.filter((a) => jamIds.aggregatorIds.has(a.id))
								.map((a) => deleteEntity("aggregator", a.id)),
							...keywords
								.filter((k) => jamIds.keywordIds.has(k.id))
								.map((k) => deleteEntity("keyword", k.id)),
							...scrapingExclusionFilters
								.filter((f) => jamIds.scrapingFilterIds.has(f.id))
								.map((f) => deleteEntity("scrapingExclusionFilter", f.id)),
						]);
					} else {
						// Delete all tour entities. SAs first to respect FK order.
						await Promise.all(
							speculativeApplications.map((s) => deleteEntity("speculativeApplication", s.id))
						);
						await Promise.all([
							...jobs.map((j) => deleteEntity("job", j.id)),
							...companies.map((c) => deleteEntity("company", c.id)),
							...persons.map((p) => deleteEntity("person", p.id)),
							...aggregators.map((a) => deleteEntity("aggregator", a.id)),
							...keywords.map((k) => deleteEntity("keyword", k.id)),
							...scrapingExclusionFilters.map((f) => deleteEntity("scrapingExclusionFilter", f.id)),
						]);
					}
				} finally {
					setIsCleaningUp(false);
					jamCreatedIds.current = emptySnapshot();
				}
			}

			// Delete all demo scraped job data — not tracked in DataContext so handled separately
			if (tourId === "import-scraped-job") {
				setDemoScrapedJobId(null);
				setDemoJobEmailId(null);
				try {
					await tourApi.clearAll(token!);
				} catch {
					// Best-effort
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
			aggregators,
			keywords,
			interviews,
			jobApplicationUpdates,
			scrapingExclusionFilters,
			speculativeApplications,
			deleteEntity,
			updateEntity,
			setIsInTour,
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
			const nextId: string = pendingNextTourId;
			setPendingNextTourId(null);
			void startTourRef.current(nextId);
		}
	}, [isTourActive, isCleaningUp, pendingNextTourId]);

	const endTourAndContinue = useCallback(
		(nextTourId: string, keepUserData?: boolean): void => {
			// Clear origin path so endTour doesn't navigate away before Tour B starts.
			originPathRef.current = null;
			setPendingNextTourId(nextTourId);
			void endTour(true, keepUserData ?? false);
		},
		[endTour]
	);

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
				demoJobEmailId,
				demoScrapingFilterId,
				allowedContextMenuActions,
				setAllowedContextMenuActions,
			}}
		>
			{children}
		</TourContext.Provider>
	);
}
