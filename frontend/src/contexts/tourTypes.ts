export interface DemoIds {
	jobId: number | null;
	scrapedJobId: number | null;
	jobEmailId: number | null;
}

export interface TourSnapshot {
	jobIds: Set<number>;
	companyIds: Set<number>;
	personIds: Set<number>;
	interviewIds: Set<number>;
	jobApplicationUpdateIds: Set<number>;
	scrapingFilterIds: Set<number>;
	scrapingFavouriteFilterIds: Set<number>;
	aggregatorIds: Set<number>;
	keywordIds: Set<number>;
	speculativeApplicationIds: Set<number>;
	fileIds: Set<number>;
}

export interface TourContextType {
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
