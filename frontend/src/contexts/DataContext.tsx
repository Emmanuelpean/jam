import React, {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useLayoutEffect,
	useMemo,
	useRef,
	useState,
} from "react";
import {
	aggregatorsApi,
	companiesApi,
	filesApi,
	interviewsApi,
	jobApplicationUpdatesApi,
	jobsApi,
	keywordsApi,
	personsApi,
	scrapingExclusionFilterApi,
	scrapingFavouriteFilterApi,
	settingsApi,
	speculativeApplicationsApi,
} from "../services/api/DataTables";
import { ApiResponse, ApiResponsePromise } from "../services/api/Base";
import { userApi } from "../services/api/Users";
import { aiSystemPromptsApi, jobEmailApi, scrapedJobApi } from "../services/api/Services";
import { useAuth } from "./AuthContext";
import { useLoading } from "./LoadingContext";
import { findItemById, sortByKey } from "../utils/Utils";
import { CrudApi } from "../services/api/Crud";
import { getScrapingFilterName } from "../components/rendering/view/ViewRenders";

import {
	AggregatorData,
	CompanyData,
	EnrichedInterviewData,
	EnrichedJobApplicationUpdateData,
	EnrichedJobData,
	FileData,
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	PersonData,
	SpeculativeApplicationData,
} from "../services/schemas/DataTables";
import { SettingData, UserData } from "../services/schemas/Core";
import { AiSystemPromptData, JobEmailData, ScrapedJobData, ScrapingFilterData } from "../services/schemas/Services";
import { ApiError } from "../services/api/ApiError";
import { GeoLocationData } from "../services/schemas/Base";
import { tourApi } from "../services/api/Others";
import {
	AggregatorCreate,
	CompanyCreate,
	FileCreate,
	InterviewCreate,
	JobApplicationUpdateCreate,
	JobCreate,
	KeywordCreate,
	PersonCreate,
	SpeculativeApplicationCreate,
} from "../services/schemas/DataTables";
import { SettingCreate, UserCreate } from "../services/schemas/Core";
import { ScrapingFilterCreate } from "../services/schemas/Services";

export type EntityType =
	| "job"
	| "company"
	| "person"
	| "interview"
	| "jobApplicationUpdate"
	| "aggregator"
	| "keyword"
	| "setting"
	| "user"
	| "scrapedJob"
	| "scrapingExclusionFilter"
	| "scrapingFavouriteFilter"
	| "speculativeApplication"
	| "jobEmail"
	| "geolocation"
	| "file";

export type JamData =
	| KeywordData
	| AggregatorData
	| PersonData
	| CompanyData
	| EnrichedJobData
	| EnrichedInterviewData
	| EnrichedJobApplicationUpdateData
	| UserData
	| SettingData
	| ScrapedJobData
	| ScrapingFilterData
	| SpeculativeApplicationData
	| JobEmailData
	| GeoLocationData
	| FileData;

export const entityTypeToGenericName = (entityType: EntityType): string => {
	const nameMap: Record<EntityType, string> = {
		job: "Job",
		company: "Company",
		person: "Contact",
		interview: "Interview",
		jobApplicationUpdate: "Job Application Update",
		aggregator: "Aggregator",
		keyword: "Tag",
		setting: "Setting",
		user: "User",
		scrapedJob: "Scraped Job",
		scrapingExclusionFilter: "Scraping Filter",
		scrapingFavouriteFilter: "Favourite Filter",
		speculativeApplication: "Speculative Application",
		jobEmail: "Job Email",
		geolocation: "Location",
		file: "File",
	};
	return nameMap[entityType];
};

export type EntityTypeDataMap = {
	keyword: KeywordData;
	aggregator: AggregatorData;
	company: CompanyData;
	person: PersonData;
	speculativeApplication: SpeculativeApplicationData;
	job: EnrichedJobData;
	interview: EnrichedInterviewData;
	jobApplicationUpdate: EnrichedJobApplicationUpdateData;
	setting: SettingData;
	user: UserData;
	scrapedJob: ScrapedJobData;
	scrapingExclusionFilter: ScrapingFilterData;
	scrapingFavouriteFilter: ScrapingFilterData;
	jobEmail: JobEmailData;
	geolocation: GeoLocationData;
	file: FileData;
};

export const entityTypeToName = <T extends EntityType>(
	entityType: T,
	dataContext: DataContextValue
): ((data: EntityTypeDataMap[T]) => string) => {
	const nameMap: { [K in EntityType]: (data: EntityTypeDataMap[K]) => string } = {
		keyword: (data: KeywordData): string => data.name,
		aggregator: (data: AggregatorData): string => data.name,
		company: (data: CompanyData): string => data.name,
		person: (data: PersonData): string => data.name,
		speculativeApplication: (data: SpeculativeApplicationData): string => {
			const company: CompanyData = findItemById(dataContext.companies, data.company_id)!;
			return "Speculative Application for " + company.name;
		},
		job: (data: EnrichedJobData): string => data.title,
		interview: (data: EnrichedInterviewData): string => {
			const job: JobData = findItemById(dataContext.jobs, data.job_id)!;
			return `${job.title} - Interview #${data.number}`;
		},
		jobApplicationUpdate: (data: EnrichedJobApplicationUpdateData): string => {
			const job: JobData = findItemById(dataContext.jobs, data.job_id)!;
			return `${job.title} - Update #${data.number}`;
		},
		setting: (data: SettingData): string => data.name,
		user: (data: UserData): string => data.email,
		scrapedJob: (data: ScrapedJobData): string => data?.title || data?.url || "Scraped Job",
		scrapingExclusionFilter: (data: ScrapingFilterData): string => getScrapingFilterName(data),
		scrapingFavouriteFilter: (data: ScrapingFilterData): string => getScrapingFilterName(data),
		jobEmail: (data: JobEmailData): string => data?.subject || "Job Email",
		geolocation: (data: GeoLocationData): string => data.query || "Location",
		file: (data: FileData): string => data.filename,
	};
	return nameMap[entityType];
};

export type EntityRawDataMap = Omit<EntityTypeDataMap, "job" | "interview" | "jobApplicationUpdate"> & {
	job: JobData;
	interview: InterviewData;
	jobApplicationUpdate: JobApplicationUpdateData;
};

export type RawJamData = EntityRawDataMap[EntityType];

export type EntityCreateDataMap = {
	keyword: KeywordCreate;
	aggregator: AggregatorCreate;
	company: CompanyCreate;
	person: PersonCreate;
	job: JobCreate;
	interview: InterviewCreate;
	jobApplicationUpdate: JobApplicationUpdateCreate;
	speculativeApplication: SpeculativeApplicationCreate;
	scrapingExclusionFilter: ScrapingFilterCreate;
	scrapingFavouriteFilter: ScrapingFilterCreate;
	file: FileCreate;
	setting: SettingCreate;
	user: UserCreate;
	scrapedJob: Record<string, unknown>;
	jobEmail: Record<string, unknown>;
	geolocation: Record<string, unknown>;
};

const entityTypeToApi = <T extends EntityType>(entityType: T): CrudApi<EntityRawDataMap[T]> | null => {
	const apiMap: Partial<{ [K in EntityType]: CrudApi<EntityRawDataMap[K]> }> = {
		job: jobsApi,
		company: companiesApi,
		person: personsApi,
		interview: interviewsApi,
		jobApplicationUpdate: jobApplicationUpdatesApi,
		aggregator: aggregatorsApi,
		keyword: keywordsApi,
		setting: settingsApi,
		user: userApi,
		scrapedJob: scrapedJobApi,
		scrapingExclusionFilter: scrapingExclusionFilterApi,
		scrapingFavouriteFilter: scrapingFavouriteFilterApi,
		speculativeApplication: speculativeApplicationsApi,
		jobEmail: jobEmailApi,
		file: filesApi,
	};
	return apiMap[entityType] ?? null;
};

interface TypedFetchOperation<T> {
	promise: ApiResponsePromise<T>;
	label: string;
}

export interface DataContextValue {
	// Data arrays
	jobs: EnrichedJobData[];
	companies: CompanyData[];
	persons: PersonData[];
	interviews: EnrichedInterviewData[];
	jobApplicationUpdates: EnrichedJobApplicationUpdateData[];
	aggregators: AggregatorData[];
	keywords: KeywordData[];
	speculativeApplications: SpeculativeApplicationData[];
	settings: SettingData[];
	scrapingExclusionFilters: ScrapingFilterData[];
	scrapingFavouriteFilters: ScrapingFilterData[];
	users: UserData[];
	aiSystemPrompts: AiSystemPromptData[];
	files: FileData[];

	error: ApiError | null;

	setIsInTour: (isInTour: boolean) => void;

	// Generic update functions
	addEntity: <T extends EntityType>(type: T, data: EntityCreateDataMap[T]) => ApiResponsePromise<EntityRawDataMap[T]>;
	updateEntity: <T extends EntityType>(
		type: T,
		id: number,
		data: Partial<JamData>
	) => ApiResponsePromise<EntityRawDataMap[T]>;
	deleteEntity: <T extends EntityType>(type: T, id: number) => Promise<void>;
	getEntityData: <T extends EntityType>(type: T) => EntityTypeDataMap[T][];
}

const DataContext = createContext<DataContextValue | undefined>(undefined);

export const DataProvider: React.FC<{ token: string; children: React.ReactNode }> = ({ token, children }) => {
	const { currentUser } = useAuth();
	const [rawJobs, setRawJobs] = useState<JobData[]>([]);
	const [companies, setCompanies] = useState<CompanyData[]>([]);
	const [persons, setPersons] = useState<PersonData[]>([]);
	const [isInTour, setIsInTourState] = useState<boolean>(false);
	const isInTourRef = useRef<boolean>(false);
	const setIsInTour = useCallback((value: boolean): void => {
		isInTourRef.current = value;
		setIsInTourState(value);
	}, []);
	const [rawInterviews, setRawInterviews] = useState<InterviewData[]>([]);
	const [rawJobApplicationUpdates, setRawJobApplicationUpdates] = useState<JobApplicationUpdateData[]>([]);
	const [aggregators, setAggregators] = useState<AggregatorData[]>([]);
	const [keywords, setKeywords] = useState<KeywordData[]>([]);
	const [speculativeApplications, setSpeculativeApplications] = useState<SpeculativeApplicationData[]>([]);
	const [settings, setSettings] = useState<SettingData[]>([]);
	const [scrapingExclusionFilters, setScrapingExclusionFilters] = useState<ScrapingFilterData[]>([]);
	const [scrapingFavouriteFilters, setScrapingFavouriteFilters] = useState<ScrapingFilterData[]>([]);
	const [users, setUsers] = useState<UserData[]>([]);
	const [aiSystemPrompts, setAiSystemPrompts] = useState<AiSystemPromptData[]>([]);
	const [files, setFiles] = useState<FileData[]>([]);
	const { showLoading, hideLoading, updateProgress } = useLoading();
	const [error, setError] = useState<ApiError | null>(null);

	const interviews: EnrichedInterviewData[] = useMemo<EnrichedInterviewData[]>((): EnrichedInterviewData[] => {
		// Enrich interviews with their sequence number per job
		return rawInterviews.map((interview: InterviewData): EnrichedInterviewData => {
			let jobInterviews: InterviewData[] = rawInterviews.filter(
				(i: InterviewData): boolean => i.job_id === interview.job_id
			);
			jobInterviews = sortByKey(jobInterviews, "date", true);
			const index: number = jobInterviews.findIndex((i: InterviewData): boolean => i.id === interview.id);
			return {
				...interview,
				number: index + 1,
			};
		});
	}, [rawInterviews]);

	const jobApplicationUpdates: EnrichedJobApplicationUpdateData[] = useMemo<
		EnrichedJobApplicationUpdateData[]
	>((): EnrichedJobApplicationUpdateData[] => {
		// Enrich updates with their sequence number per job
		return rawJobApplicationUpdates.map((update: JobApplicationUpdateData): EnrichedJobApplicationUpdateData => {
			let jobUpdates: JobApplicationUpdateData[] = rawJobApplicationUpdates.filter(
				(u: JobApplicationUpdateData): boolean => u.job_id === update.job_id
			);
			jobUpdates = sortByKey(jobUpdates, "date", true);
			const index: number = jobUpdates.findIndex((u: JobApplicationUpdateData): boolean => u.id === update.id);
			return {
				...update,
				number: index + 1,
			};
		});
	}, [rawJobApplicationUpdates]);

	const jobs: EnrichedJobData[] = useMemo<EnrichedJobData[]>((): EnrichedJobData[] => {
		// Enrich jobs with calculated fields
		return rawJobs.map((job: JobData): EnrichedJobData => {
			const jobInterviews: InterviewData[] = rawInterviews.filter(
				(i: InterviewData): boolean => i.job_id === job.id
			);
			const jobUpdates: JobApplicationUpdateData[] = rawJobApplicationUpdates.filter(
				(u: JobApplicationUpdateData): boolean => u.job_id === job.id
			);

			// Calculate last_update_date
			let lastUpdateDate: Date | null = null;
			if (job.application_date) {
				const dates: Date[] = [new Date(job.application_date)];
				jobInterviews.forEach((i: InterviewData): number => i.date && dates.push(new Date(i.date)));
				jobUpdates.forEach((u: JobApplicationUpdateData): number => u.date && dates.push(new Date(u.date)));
				lastUpdateDate =
					dates.length > 0 ? new Date(Math.max(...dates.map((d: Date): number => d.getTime()))) : null;
			}

			// Calculate last_update_type
			let lastUpdateType: string | null = null;
			if (job.application_date && lastUpdateDate) {
				let mostRecentDate: Date = new Date(job.application_date);
				lastUpdateType = "Application";

				if (jobInterviews.length > 0) {
					const latestInterview: InterviewData = jobInterviews.reduce(
						(latest: InterviewData, current: InterviewData): InterviewData =>
							new Date(current.date) > new Date(latest.date) ? current : latest
					);
					if (new Date(latestInterview.date) > mostRecentDate) {
						mostRecentDate = new Date(latestInterview.date);
						lastUpdateType = `Interview (${jobInterviews.length})`;
					}
				}

				if (jobUpdates.length > 0) {
					const latestUpdate: JobApplicationUpdateData = jobUpdates.reduce(
						(
							latest: JobApplicationUpdateData,
							current: JobApplicationUpdateData
						): JobApplicationUpdateData =>
							new Date(current.date) > new Date(latest.date) ? current : latest
					);
					if (new Date(latestUpdate.date) > mostRecentDate) {
						lastUpdateType = `Update (${jobUpdates.length})`;
					}
				}
			}

			// Calculate days_since_last_update
			const daysSinceLastUpdate: number | null = lastUpdateDate
				? Math.floor((Date.now() - lastUpdateDate.getTime()) / (1000 * 60 * 60 * 24))
				: null;

			// Calculate days_until_deadline
			let daysUntilDeadline: number | null = null;
			if (job.deadline) {
				const now = new Date();
				const deadlineDate = new Date(job.deadline);
				deadlineDate.setHours(23, 59, 59);
				daysUntilDeadline = (deadlineDate.getTime() - now.getTime()) / 1000;
			}

			// Create the job name from the title and the company name
			let jobName: string = job.title;
			if (job.company_id) {
				const company: CompanyData | undefined = companies.find(
					(c: CompanyData): boolean => c.id === job.company_id
				);
				if (company) {
					jobName = `${job.title} (${company.name})`;
				}
			}

			return {
				...job,
				last_update_date: lastUpdateDate,
				last_update_type: lastUpdateType,
				days_since_last_update: daysSinceLastUpdate,
				days_until_deadline: daysUntilDeadline,
				name: jobName,
			};
		});
	}, [rawJobs, rawInterviews, rawJobApplicationUpdates, companies]);

	const fetchAllData = async (): Promise<void> => {
		setError(null);

		// Define all promises with their labels
		const fetchOperations: any[] = [
			{ promise: jobsApi.getAll(token), label: "Jobs" } as TypedFetchOperation<JobData[]>,
			{
				promise: speculativeApplicationsApi.getAll(token),
				label: "Speculative Applications",
			} as TypedFetchOperation<SpeculativeApplicationData[]>,
			{ promise: companiesApi.getAll(token), label: "Companies" } as TypedFetchOperation<CompanyData[]>,
			{ promise: personsApi.getAll(token), label: "Contacts" } as TypedFetchOperation<PersonData[]>,
			{ promise: interviewsApi.getAll(token), label: "Interviews" } as TypedFetchOperation<InterviewData[]>,
			{
				promise: jobApplicationUpdatesApi.getAll(token),
				label: "Job Application Updates",
			} as TypedFetchOperation<JobApplicationUpdateData[]>,
			{ promise: aggregatorsApi.getAll(token), label: "Aggregators" } as TypedFetchOperation<AggregatorData[]>,
			{ promise: keywordsApi.getAll(token), label: "Keywords" } as TypedFetchOperation<KeywordData[]>,
			{
				promise: scrapingExclusionFilterApi.getAll(token),
				label: "Scraping Filters",
			} as TypedFetchOperation<ScrapingFilterData[]>,
			{
				promise: scrapingFavouriteFilterApi.getAll(token),
				label: "Scraping Filters",
			} as TypedFetchOperation<ScrapingFilterData[]>,
			{
				promise: filesApi.getAll(token),
				label: "Files",
			} as TypedFetchOperation<FileData[]>,
			{
				promise: aiSystemPromptsApi.getAll(token),
				label: "Miscellaneous",
			} as TypedFetchOperation<AiSystemPromptData[]>,
		];

		// Add admin-only calls if user is admin
		if (currentUser?.is_admin) {
			fetchOperations.push(
				{ promise: settingsApi.getAll(token), label: "Settings" } as TypedFetchOperation<SettingData[]>,
				{ promise: userApi.getAll(token), label: "Users" } as TypedFetchOperation<UserData[]>
			);
		}

		const totalOperations: number = fetchOperations.length;
		let completedOperations: number = 0;
		let displayIndex: number = 0;

		try {
			// Track progress for each promise
			const trackedPromises: any[] = fetchOperations.map(({ promise }: any): any =>
				promise.then((result: ApiResponse<JamData[]>): ApiResponse<JamData[]> => {
					completedOperations++;
					const progressPercentage: number = Math.round((completedOperations / totalOperations) * 100);
					const displayLabel: string = fetchOperations[displayIndex++].label;
					if (displayLabel === "Miscellaneous") {
						updateProgress(progressPercentage, `...And The Rest`);
					} else {
						updateProgress(progressPercentage, `Loading Your ${displayLabel}...`);
					}
					return result;
				})
			);

			const results: any[] = await Promise.all(trackedPromises);

			// Destructure based on what we fetched
			const [
				jobsData,
				speculativeApplicationData,
				companiesData,
				personsData,
				interviewsData,
				jobApplicationUpdatesData,
				aggregatorsData,
				keywordsData,
				scrapingFiltersData,
				scrapingFavouriteFiltersData,
				aiSystemPromptsData,
				filesData,
				...adminData
			] = results;

			setRawJobs(jobsData.data || []);
			setSpeculativeApplications(speculativeApplicationData.data || []);
			setCompanies(companiesData.data || []);
			setPersons(personsData.data || []);
			setRawInterviews(interviewsData.data || []);
			setRawJobApplicationUpdates(jobApplicationUpdatesData.data || []);
			setAggregators(aggregatorsData.data || []);
			setKeywords(keywordsData.data || []);
			setScrapingExclusionFilters(scrapingFiltersData.data || []);
			setScrapingFavouriteFilters(scrapingFavouriteFiltersData.data || []);
			setAiSystemPrompts(aiSystemPromptsData.data || []);
			setFiles(filesData.data || []);
			if (currentUser?.is_admin) {
				setSettings(adminData[0].data || []);
				setUsers(adminData[1].data || []);
			}
		} catch (e: any) {
			setError(e);
		} finally {
			hideLoading();
		}
	};

	// Helper to get setter function for an entity type
	const entityTypeToSetter = <T extends EntityType>(
		type: T
	): React.Dispatch<React.SetStateAction<EntityRawDataMap[T][]>> | undefined => {
		const setterMap: Partial<{ [K in EntityType]: React.Dispatch<React.SetStateAction<EntityRawDataMap[K][]>> }> = {
			job: setRawJobs,
			company: setCompanies,
			person: setPersons,
			interview: setRawInterviews,
			jobApplicationUpdate: setRawJobApplicationUpdates,
			aggregator: setAggregators,
			keyword: setKeywords,
			setting: setSettings,
			user: setUsers,
			scrapingExclusionFilter: setScrapingExclusionFilters,
			scrapingFavouriteFilter: setScrapingFavouriteFilters,
			speculativeApplication: setSpeculativeApplications,
			file: setFiles,
		};
		return setterMap[type] as React.Dispatch<React.SetStateAction<EntityRawDataMap[T][]>> | undefined;
	};

	const addEntity = useCallback(
		async <T extends EntityType>(
			entityType: T,
			newData: EntityCreateDataMap[T]
		): Promise<ApiResponse<EntityRawDataMap[T]>> => {
			const api: CrudApi<EntityRawDataMap[T]> | null = entityTypeToApi(entityType);
			if (!api) throw new Error(`No API for entity type: ${entityType}`);
			try {
				const payload: EntityCreateDataMap[T] = isInTourRef.current ? { ...newData, is_tour: true } : newData;
				const apiResult: ApiResponse<EntityRawDataMap[T]> = await api.create(payload, token);
				const setter = entityTypeToSetter(entityType);
				setter?.((prev: any[]): any[] => [...prev, apiResult.data]);
				return apiResult;
			} catch (error) {
				console.error(`Failed to add ${entityType}:`, error);
				throw error;
			}
		},
		[token]
	);

	const updateEntity = useCallback(
		async <T extends EntityType>(
			entityType: T,
			id: number,
			updatedData: any
		): Promise<ApiResponse<EntityRawDataMap[T]>> => {
			const api: CrudApi<EntityRawDataMap[T]> | null = entityTypeToApi(entityType);
			if (!api) throw new Error(`No API for entity type: ${entityType}`);
			try {
				const apiResult: ApiResponse<EntityRawDataMap[T]> = await api.update(id, updatedData, token);
				const setter = entityTypeToSetter(entityType);
				setter?.((prev: any[]): any[] => prev.map((item: any) => (item.id === id ? apiResult.data : item)));
				return apiResult;
			} catch (error) {
				console.error(`Failed to update ${entityType}:`, error);
				throw error;
			}
		},
		[token]
	);

	const deleteEntity = useCallback(
		async <T extends EntityType>(entityType: T, id: number): Promise<void> => {
			try {
				const api: CrudApi<EntityRawDataMap[T]> | null = entityTypeToApi(entityType);
				if (!api) return;
				await api.delete(id, token);
				const setter = entityTypeToSetter(entityType);
				setter?.((prev: any[]): any[] => prev.filter((item: any): boolean => item.id !== id));
				if (entityType === "job") {
					setRawInterviews((prev: InterviewData[]): InterviewData[] =>
						prev.filter((interview: InterviewData): boolean => interview.job_id !== id)
					);
					setRawJobApplicationUpdates((prev: JobApplicationUpdateData[]): JobApplicationUpdateData[] =>
						prev.filter((update: JobApplicationUpdateData): boolean => update.job_id !== id)
					);
				}
				if (entityType === "company") {
					setSpeculativeApplications((prev: SpeculativeApplicationData[]): SpeculativeApplicationData[] =>
						prev.filter((sa: SpeculativeApplicationData): boolean => sa.company_id !== id)
					);
				}
			} catch (error) {
				console.error(`Failed to delete ${entityType}:`, error);
				throw error;
			}
		},
		[token]
	);

	const visibleData = useMemo(() => {
		return {
			jobs: jobs.filter((j: EnrichedJobData): boolean => j.is_tour === isInTour),
			companies: companies.filter((c: CompanyData): boolean => c.is_tour === isInTour),
			persons: persons.filter((p: PersonData): boolean => p.is_tour === isInTour),
			interviews: interviews.filter((i: EnrichedInterviewData): boolean => i.is_tour === isInTour),
			jobApplicationUpdates: jobApplicationUpdates.filter(
				(u: EnrichedJobApplicationUpdateData): boolean => u.is_tour === isInTour
			),
			aggregators: aggregators.filter((a: AggregatorData): boolean => a.is_tour === isInTour),
			keywords: keywords.filter((k: KeywordData): boolean => k.is_tour === isInTour),
			scrapingExclusionFilters: scrapingExclusionFilters.filter(
				(f: ScrapingFilterData): boolean => f.is_tour === isInTour
			),
			speculativeApplications: speculativeApplications.filter(
				(sa: SpeculativeApplicationData): boolean => sa.is_tour === isInTour
			),
			files: files.filter((f: FileData): boolean => f.is_tour === isInTour),
			scrapingFavouriteFilters: scrapingFavouriteFilters.filter(
				(s: ScrapingFilterData) => s.is_tour === isInTour
			),
		};
	}, [
		isInTour,
		jobs,
		companies,
		persons,
		interviews,
		jobApplicationUpdates,
		aggregators,
		keywords,
		files,
		scrapingExclusionFilters,
		scrapingFavouriteFilters,
		speculativeApplications,
	]);

	const getEntityData = useCallback(
		<T extends EntityType>(entityType: T): EntityTypeDataMap[T][] => {
			const dataMap: Partial<{ [K in EntityType]: EntityTypeDataMap[K][] }> = {
				job: visibleData.jobs,
				company: visibleData.companies,
				person: visibleData.persons,
				interview: visibleData.interviews,
				jobApplicationUpdate: visibleData.jobApplicationUpdates,
				aggregator: visibleData.aggregators,
				keyword: visibleData.keywords,
				scrapingExclusionFilter: visibleData.scrapingExclusionFilters,
				setting: settings,
				user: users,
				scrapingFavouriteFilter: scrapingFavouriteFilters,
				speculativeApplication: visibleData.speculativeApplications,
				file: files,
			};
			return (dataMap[entityType] ?? []) as EntityTypeDataMap[T][];
		},
		[visibleData, settings, users, scrapingFavouriteFilters, files]
	);

	// Show loading immediately on mount — DataProvider only renders when !!token,
	// so this fires on login and on page refresh with an existing session.
	useLayoutEffect((): void => {
		showLoading("Loading Your Data...", 0);
	}, []);

	useEffect((): void => {
		if (!token || !currentUser) return;
		void tourApi
			.clearAll(token)
			.catch((): void => {})
			.then((): Promise<void> => fetchAllData());
	}, [token, currentUser?.is_admin]);

	return (
		<DataContext.Provider
			value={{
				...visibleData,
				aiSystemPrompts,
				settings,
				users,
				error,
				setIsInTour,
				updateEntity,
				deleteEntity,
				addEntity,
				getEntityData,
			}}
		>
			{children}
		</DataContext.Provider>
	);
};

export const useDataContext = (): DataContextValue => {
	const context: DataContextValue | undefined = useContext(DataContext);
	if (!context) throw new Error("useDataContext must be used within a DataProvider");
	return context;
};
