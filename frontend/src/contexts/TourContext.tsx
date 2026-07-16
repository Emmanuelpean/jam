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
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { EntityType, useDataContext } from "./DataContext";
import { useProgressOverlay } from "./useProgressOverlayContext";
import { useGlobalToast } from "../hooks/useNotificationToast";
import { tourApi } from "../services/api/Others";
import {
	CompanyData,
	EnrichedJobData,
	KeywordData,
	PersonData,
	SpeculativeApplicationData,
} from "../services/schemas/DataTables";
import { ScrapingFilterData } from "../services/schemas/Services";
import { DemoIds, TourContextType, TourSnapshot } from "./tourTypes";
import { runTourSetup } from "./tourSetups";

export type { TourSnapshot, TourContextType };

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
		scrapingFavouriteFilterIds: new Set(),
		aggregatorIds: new Set(),
		keywordIds: new Set(),
		speculativeApplicationIds: new Set(),
		fileIds: new Set(),
	};
}

// Tours that isolate the user's real data by filtering to is_tour=true during the tour.
// Every tour should be in this set unless there is an explicit reason not to isolate.
const ISOLATED_TOURS = new Set([
	"first-job",
	"follow-up-email",
	"scraping-filters",
	"log-interview",
	"log-update",
	"log-application",
	"add-contact",
	"speculative-applications",
	"import-scraped-job",
]);

export function TourProvider({ children }: TourProviderProps): JSX.Element {
	const [activeTourId, setActiveTourId] = useState<string | null>(null);
	const [isTourSelectOpen, setIsTourSelectOpen] = useState<boolean>(false);
	const [tourSelectHideDismiss, setTourSelectHideDismiss] = useState<boolean>(false);
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
		aggregators,
		keywords,
		scrapingExclusionFilters,
		scrapingFavouriteFilters,
		speculativeApplications,
		files,
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
	const demoIdsRef = useRef<DemoIds>({ jobId: null, scrapedJobId: null, jobEmailId: null });

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

	const hasUserCreatedData: boolean = useMemo((): boolean => {
		if (!isTourActive || activeTourId === null || !ISOLATED_TOURS.has(activeTourId)) return false;
		const jamIds: TourSnapshot = jamCreatedIds.current;
		return (
			jobs.some((j: EnrichedJobData): boolean => !jamIds.jobIds.has(j.id)) ||
			companies.some((c: CompanyData): boolean => !jamIds.companyIds.has(c.id)) ||
			persons.some((p: PersonData): boolean => !jamIds.personIds.has(p.id)) ||
			keywords.some((k: KeywordData): boolean => !jamIds.keywordIds.has(k.id)) ||
			scrapingExclusionFilters.some((f: ScrapingFilterData): boolean => !jamIds.scrapingFilterIds.has(f.id)) ||
			speculativeApplications.some(
				(s: SpeculativeApplicationData): boolean =>
					!jamIds.speculativeApplicationIds.has(s.id) && !jamIds.companyIds.has(s.company_id)
			)
		);
	}, [
		isTourActive,
		activeTourId,
		jobs,
		companies,
		persons,
		keywords,
		scrapingExclusionFilters,
		speculativeApplications,
	]);

	const startTour = useCallback(
		async (tourId: string): Promise<void> => {
			try {
				originPathRef.current = location.pathname;
				await tourApi.clearAll(token!);

				jamCreatedIds.current = emptySnapshot();
				demoIdsRef.current = { jobId: null, scrapedJobId: null, jobEmailId: null };

				if (ISOLATED_TOURS.has(tourId)) setIsInTour(true);

				showProgress("Setting up tour...");
				try {
					await runTourSetup(tourId, { addEntity, jamCreatedIds, demoIds: demoIdsRef, token: token! });
				} finally {
					hideProgress();
				}

				setDemoJobId(demoIdsRef.current.jobId);
				setDemoScrapedJobId(demoIdsRef.current.scrapedJobId);
				setDemoJobEmailId(demoIdsRef.current.jobEmailId);

				setIsTourSelectOpen(false);
				setActiveTourId(tourId);
			} catch (err: any) {
				showToastError(`Failed to start tour: ${err?.message ?? "Unknown error"}`);
			}
		},
		[addEntity, setIsInTour, token, location.pathname, showToastError]
	);

	const endTour = useCallback(
		async (completed: boolean, keepUserData?: boolean): Promise<void> => {
			if (!activeTourId) return;

			const tourId: string = activeTourId;
			setActiveTourId(null);
			setIsInTour(false);

			document.querySelectorAll<HTMLElement>(".modal.show").forEach((modal: HTMLElement): void => {
				const cancelBtn: HTMLElement | null = modal.querySelector<HTMLElement>('[id$="-cancel-button"]');
				(cancelBtn ?? modal.querySelector<HTMLElement>(".btn-close"))?.click();
			});

			setDemoJobId(null);
			setDemoScrapedJobId(null);
			setDemoJobEmailId(null);
			setDemoScrapingFilterId(null);

			if (completed && !completedTourIds.has(tourId)) {
				const newIds: string[] = [...completedTourIds, tourId];
				setCompletedTourIds(new Set(newIds));
				void updateCurrentUser({ preferences: { completed_tours: newIds } });
			}

			const jamIds: TourSnapshot = jamCreatedIds.current;

			if (ISOLATED_TOURS.has(tourId)) {
				setIsCleaningUp(true);
				try {
					const groups: Array<{
						items: { id: number; is_tour: boolean }[];
						type: EntityType;
						jamIdSet: Set<number>;
					}> = [
						{ items: jobs, type: "job", jamIdSet: jamIds.jobIds },
						{ items: companies, type: "company", jamIdSet: jamIds.companyIds },
						{ items: persons, type: "person", jamIdSet: jamIds.personIds },
						{ items: aggregators, type: "aggregator", jamIdSet: jamIds.aggregatorIds },
						{ items: keywords, type: "keyword", jamIdSet: jamIds.keywordIds },
						{
							items: scrapingExclusionFilters,
							type: "scrapingExclusionFilter",
							jamIdSet: jamIds.scrapingFilterIds,
						},
						{
							items: scrapingFavouriteFilters,
							type: "scrapingFavouriteFilter",
							jamIdSet: jamIds.scrapingFavouriteFilterIds,
						},
						{ items: files, type: "file", jamIdSet: jamIds.fileIds },
					];

					// Round 1: always delete JAM-created entities.
					await Promise.all(
						groups.flatMap(({ items, type, jamIdSet }): Promise<void>[] =>
							items
								.filter((e): boolean => e.is_tour && jamIdSet.has(e.id))
								.map((e): Promise<void> => deleteEntity(type, e.id))
						)
					);

					// Round 2: user-created entities — patch to is_tour=false or delete.
					if (keepUserData) {
						const keepableSAs: SpeculativeApplicationData[] = speculativeApplications.filter(
							(s: SpeculativeApplicationData): boolean =>
								!jamIds.speculativeApplicationIds.has(s.id) && !jamIds.companyIds.has(s.company_id)
						);
						await Promise.all([
							...groups.flatMap(({ items, type, jamIdSet }) =>
								items
									.filter((e: { id: number }): boolean => !jamIdSet.has(e.id))
									.map((e: { id: number }) => updateEntity(type, e.id, { is_tour: false }))
							),
							...keepableSAs.map((s) => updateEntity("speculativeApplication", s.id, { is_tour: false })),
						]);
					} else {
						await Promise.all(
							groups.flatMap(({ items, type, jamIdSet }): Promise<void>[] =>
								items
									.filter((e): boolean => e.is_tour && !jamIdSet.has(e.id))
									.map((e): Promise<void> => deleteEntity(type, e.id))
							)
						);
					}

					// Round 3: Clear all remaining data
					await tourApi.clearAll(token!);
				} catch {
					showToastError(
						"Failed to clean up tour data. This may cause tour generated data to be visible. " +
							"You may try to reload the page to fix this."
					);
				} finally {
					setIsCleaningUp(false);
					jamCreatedIds.current = emptySnapshot();
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
			scrapingExclusionFilters,
			scrapingFavouriteFilters,
			speculativeApplications,
			files,
			deleteEntity,
			updateEntity,
			setIsInTour,
			token,
			navigate,
			showProgress,
			hideProgress,
		]
	);

	// Always points to the latest startTour so the pending-next-tour effect uses fresh state.
	const startTourRef = useRef(startTour);
	startTourRef.current = startTour;

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

	const openTourSelect = useCallback((options?: { hideDismiss?: boolean }): void => {
		setTourSelectHideDismiss(options?.hideDismiss ?? false);
		setIsTourSelectOpen(true);
	}, []);
	const closeTourSelect = useCallback((): void => setIsTourSelectOpen(false), []);
	const toggleTourSelect = useCallback((options?: { hideDismiss?: boolean }): void => {
		setIsTourSelectOpen((prev: boolean): boolean => {
			if (!prev) setTourSelectHideDismiss(options?.hideDismiss ?? false);
			return !prev;
		});
	}, []);

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
				tourSelectHideDismiss,
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
