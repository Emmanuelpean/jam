import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
	aggregatorsApi,
	companiesApi,
	countriesApi,
	currenciesApi,
	interviewsApi,
	jobApplicationUpdatesApi,
	jobsApi,
	keywordsApi,
	locationsApi,
	personsApi,
	scrapingFilterApi,
	settingsApi,
	speculativeApplicationsApi,
} from "../services/api/DataTables";
import { ApiResponse, ApiResponsePromise } from "../services/api/Base";
import { userApi } from "../services/api/Users";
import { scrapedJobApi } from "../services/api/Services";
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
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	LocationData,
	PersonData,
	SpeculativeApplicationData,
} from "../services/schemas/DataTables";
import { SettingData, UserData } from "../services/schemas/Core";
import { ScrapedJobData, ScrapingFilterData } from "../services/schemas/Services";
import { Country, Currency } from "../services/schemas/Others";
import { ApiError } from "../services/api/ApiError";

export type EntityType =
	| "job"
	| "company"
	| "person"
	| "interview"
	| "jobApplicationUpdate"
	| "aggregator"
	| "keyword"
	| "location"
	| "setting"
	| "user"
	| "scrapedJob"
	| "scrapingFilter"
	| "speculativeApplication";

export type JamData =
	| KeywordData
	| LocationData
	| AggregatorData
	| PersonData
	| CompanyData
	| EnrichedJobData
	| InterviewData
	| JobApplicationUpdateData
	| UserData
	| SettingData
	| ScrapedJobData
	| ScrapingFilterData
	| SpeculativeApplicationData;

export const entityTypeToGenericName = (entityType: EntityType): string => {
	const nameMap: Record<EntityType, string> = {
		job: "Job",
		company: "Company",
		person: "Person",
		interview: "Interview",
		jobApplicationUpdate: "Job Application Update",
		aggregator: "Aggregator",
		keyword: "Tag",
		location: "Location",
		setting: "Setting",
		user: "User",
		scrapedJob: "Scraped Job",
		scrapingFilter: "Scraping Filter",
		speculativeApplication: "Speculative Application",
	};
	return nameMap[entityType];
};

export const entityTypeToName = (
	entityType: EntityType,
	dataContext: DataContextValue
): ((data: JamData) => string) => {
	// noinspection JSUnusedGlobalSymbols
	const nameMap: Record<EntityType, (data: JamData) => string> = {
		keyword: (data: JamData): string => (data as KeywordData).name,
		aggregator: (data: JamData): string => (data as AggregatorData).name,
		company: (data: JamData): string => (data as CompanyData).name,
		location: (data: JamData): string => (data as LocationData).name,
		person: (data: JamData): string => (data as PersonData).name,
		speculativeApplication: (data: JamData): string => {
			const company: CompanyData = findItemById(
				dataContext.companies,
				(data as SpeculativeApplicationData).company_id
			)!;
			return "Speculative Application for " + company.name;
		},
		job: (data: JamData): string => (data as JobData).title,
		interview: (data: JamData): string => {
			const job: JobData = findItemById(dataContext.jobs, (data as InterviewData).job_id)!;
			return `${job.title} - Interview #${(data as EnrichedInterviewData).number}`;
		},
		jobApplicationUpdate: (data: JamData): string => {
			const job: JobData = findItemById(dataContext.jobs, (data as InterviewData).job_id)!;
			return `${job.title} - Update #${(data as EnrichedJobApplicationUpdateData).number}`;
		},
		setting: (data: JamData): string => (data as SettingData).name,
		user: (data: JamData): string => (data as UserData).email,
		scrapedJob: (data: JamData): string => (data as ScrapedJobData)?.title || "Scraped Job",
		scrapingFilter: (data: JamData): string => getScrapingFilterName(data as ScrapingFilterData),
	};
	return nameMap[entityType];
};

const entityTypeToApi = (entityType: EntityType) => {
	const apiMap = {
		job: jobsApi,
		company: companiesApi,
		person: personsApi,
		interview: interviewsApi,
		jobApplicationUpdate: jobApplicationUpdatesApi,
		aggregator: aggregatorsApi,
		keyword: keywordsApi,
		location: locationsApi,
		setting: settingsApi,
		user: userApi,
		scrapedJob: scrapedJobApi,
		scrapingFilter: scrapingFilterApi,
		speculativeApplication: speculativeApplicationsApi,
	};
	return apiMap[entityType];
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
	locations: LocationData[];
	speculativeApplications: SpeculativeApplicationData[];
	settings: SettingData[];
	scrapingFilters: ScrapingFilterData[];
	users: UserData[];
	countries: Country[];
	currencies: Currency[];

	error: ApiError | null;

	// Generic update functions
	addEntity: <T extends EntityType>(type: T, data: any) => ApiResponsePromise<JamData>;
	updateEntity: <T extends EntityType>(type: T, id: number, data: Partial<JamData>) => ApiResponsePromise<JamData>;
	deleteEntity: <T extends EntityType>(type: T, id: number) => Promise<void>;
	getEntityData: <T extends EntityType>(type: T) => JamData[];
}

const DataContext = createContext<DataContextValue | undefined>(undefined);

export const DataProvider: React.FC<{ token: string; children: React.ReactNode }> = ({ token, children }) => {
	const { currentUser } = useAuth();
	const [rawJobs, setRawJobs] = useState<JobData[]>([]);
	const [companies, setCompanies] = useState<CompanyData[]>([]);
	const [persons, setPersons] = useState<PersonData[]>([]);
	const [rawInterviews, setRawInterviews] = useState<InterviewData[]>([]);
	const [rawJobApplicationUpdates, setRawJobApplicationUpdates] = useState<JobApplicationUpdateData[]>([]);
	const [aggregators, setAggregators] = useState<AggregatorData[]>([]);
	const [keywords, setKeywords] = useState<KeywordData[]>([]);
	const [locations, setLocations] = useState<LocationData[]>([]);
	const [speculativeApplications, setSpeculativeApplications] = useState<SpeculativeApplicationData[]>([]);
	const [settings, setSettings] = useState<SettingData[]>([]);
	const [scrapingFilters, setScrapingFilters] = useState<ScrapingFilterData[]>([]);
	const [users, setUsers] = useState<UserData[]>([]);
	const [_scrapedJobs, setScrapedJobs] = useState<any[]>([]);
	const [currencies, setCurrencies] = useState<Currency[]>([]);
	const [countries, setCountries] = useState<Country[]>([]);
	const { showLoading, hideLoading, updateProgress } = useLoading();
	const [error, setError] = useState<ApiError | null>(null);

	const interviews: EnrichedInterviewData[] = useMemo<EnrichedInterviewData[]>((): EnrichedInterviewData[] => {
		// Enrich interviews with their sequence number per job
		return rawInterviews.map((interview: InterviewData): EnrichedInterviewData => {
			const job: JobData | undefined = rawJobs.find((j: JobData): boolean => j.id === interview.job_id)!;

			let jobInterviews: InterviewData[] = rawInterviews.filter(
				(i: InterviewData): boolean => i.job_id === job.id
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
			const job: JobData | undefined = rawJobs.find((j: JobData): boolean => j.id === update.job_id)!;

			let jobUpdates: JobApplicationUpdateData[] = rawJobApplicationUpdates.filter(
				(u: JobApplicationUpdateData): boolean => u.job_id === job.id
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
				jobInterviews.forEach((i: InterviewData) => i.date && dates.push(new Date(i.date)));
				jobUpdates.forEach((u: JobApplicationUpdateData) => u.date && dates.push(new Date(u.date)));
				lastUpdateDate = dates.length > 0 ? new Date(Math.max(...dates.map((d) => d.getTime()))) : null;
			}

			// Calculate last_update_type
			let lastUpdateType: string | null = null;
			if (job.application_date && lastUpdateDate) {
				let mostRecentDate = new Date(job.application_date);
				lastUpdateType = "Application";

				if (jobInterviews.length > 0) {
					const latestInterview = jobInterviews.reduce((latest, current) =>
						new Date(current.date) > new Date(latest.date) ? current : latest
					);
					if (new Date(latestInterview.date) > mostRecentDate) {
						mostRecentDate = new Date(latestInterview.date);
						lastUpdateType = `Interview (${jobInterviews.length})`;
					}
				}

				if (jobUpdates.length > 0) {
					const latestUpdate = jobUpdates.reduce((latest, current) =>
						new Date(current.date) > new Date(latest.date) ? current : latest
					);
					if (new Date(latestUpdate.date) > mostRecentDate) {
						lastUpdateType = `Update (${jobUpdates.length})`;
					}
				}
			}

			// Calculate days_since_last_update
			const daysSinceLastUpdate = lastUpdateDate
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

	const fetchAllData = async () => {
		setError(null);

		// Define all promises with their labels
		const fetchOperations: any[] = [
			{ promise: jobsApi.getAll(token), label: "Jobs" } as TypedFetchOperation<JobData[]>,
			{
				promise: speculativeApplicationsApi.getAll(token),
				label: "Speculative Applications",
			} as TypedFetchOperation<SpeculativeApplicationData[]>,
			{ promise: companiesApi.getAll(token), label: "Companies" } as TypedFetchOperation<CompanyData[]>,
			{ promise: personsApi.getAll(token), label: "Persons" } as TypedFetchOperation<PersonData[]>,
			{ promise: interviewsApi.getAll(token), label: "Interviews" } as TypedFetchOperation<InterviewData[]>,
			{
				promise: jobApplicationUpdatesApi.getAll(token),
				label: "Job Application Updates",
			} as TypedFetchOperation<JobApplicationUpdateData[]>,
			{ promise: aggregatorsApi.getAll(token), label: "Aggregators" } as TypedFetchOperation<AggregatorData[]>,
			{ promise: keywordsApi.getAll(token), label: "Keywords" } as TypedFetchOperation<KeywordData[]>,
			{ promise: locationsApi.getAll(token), label: "Locations" } as TypedFetchOperation<LocationData[]>,
			{
				promise: scrapingFilterApi.getAll(token),
				label: "Scraping Filters",
			} as TypedFetchOperation<ScrapingFilterData[]>,
			{ promise: currenciesApi.getAll(token), label: "Miscellaneous" } as TypedFetchOperation<Currency[]>,
			{ promise: countriesApi.getAll(token), label: "Miscellaneous" } as TypedFetchOperation<Country[]>,
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

		// Show initial loading state
		showLoading("Initialising Data Load...", 0);

		try {
			// Track progress for each promise
			const trackedPromises = fetchOperations.map(({ promise, label }) =>
				promise.then(
					(
						result: ApiResponse<(JamData | Country | Currency)[]>
					): ApiResponse<(JamData | Country | Currency)[]> => {
						completedOperations++;
						const progressPercentage: number = Math.round((completedOperations / totalOperations) * 100);
						updateProgress(progressPercentage, `Loading ${label}...`);
						return result;
					}
				)
			);

			const results = await Promise.all(trackedPromises);

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
				locationsData,
				scrapingFiltersData,
				currenciesData,
				countriesData,
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
			setLocations(locationsData.data || []);
			setScrapingFilters(scrapingFiltersData.data || []);
			setCurrencies(currenciesData.data || []);
			setCountries(countriesData.data || []);
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
	const entityTypeToSetter = (type: EntityType) => {
		const setterMap = {
			job: setRawJobs,
			company: setCompanies,
			person: setPersons,
			interview: setRawInterviews,
			jobApplicationUpdate: setRawJobApplicationUpdates,
			aggregator: setAggregators,
			keyword: setKeywords,
			location: setLocations,
			setting: setSettings,
			user: setUsers,
			scrapedJob: setScrapedJobs,
			scrapingFilter: setScrapingFilters,
			speculativeApplication: setSpeculativeApplications,
		};
		return setterMap[type];
	};

	const addEntity = useCallback(
		async <T extends EntityType>(entityType: T, newData: any): Promise<any> => {
			try {
				const api: CrudApi<JamData> = entityTypeToApi(entityType);
				const apiResult: ApiResponse<JamData> = await api.create(newData, token);
				const setter = entityTypeToSetter(entityType);
				setter((prev: any[]): any[] => [...prev, apiResult.data]);
				return apiResult;
			} catch (error) {
				console.error(`Failed to add ${entityType}:`, error);
				throw error;
			}
		},
		[token]
	);

	const updateEntity = useCallback(
		async <T extends EntityType>(entityType: T, id: number, updatedData: any): Promise<any> => {
			try {
				const api: CrudApi<JamData> = entityTypeToApi(entityType);
				const apiResult: ApiResponse<JamData> = await api.update(id, updatedData, token);
				const setter = entityTypeToSetter(entityType);
				setter((prev: any[]): any[] => prev.map((item: any) => (item.id === id ? apiResult.data : item)));
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
				const api: CrudApi<JamData> = entityTypeToApi(entityType);
				await api.delete(id, token);
				const setter = entityTypeToSetter(entityType);
				setter((prev: any[]): any[] => prev.filter((item: any): boolean => item.id !== id));
				if (entityType === "job") {
					setRawInterviews((prev: InterviewData[]): InterviewData[] =>
						prev.filter((interview: InterviewData): boolean => interview.job_id !== id)
					);
					setRawJobApplicationUpdates((prev: JobApplicationUpdateData[]): JobApplicationUpdateData[] =>
						prev.filter((update: JobApplicationUpdateData): boolean => update.job_id !== id)
					);
				}
			} catch (error) {
				console.error(`Failed to delete ${entityType}:`, error);
				throw error;
			}
		},
		[token]
	);

	const getEntityData = useCallback(
		<T extends EntityType>(entityType: T): JamData[] => {
			const dataMap: Record<EntityType, JamData[]> = {
				job: jobs,
				company: companies,
				person: persons,
				interview: interviews,
				jobApplicationUpdate: jobApplicationUpdates,
				aggregator: aggregators,
				keyword: keywords,
				location: locations,
				setting: settings,
				user: users,
				scrapedJob: _scrapedJobs,
				scrapingFilter: scrapingFilters,
				speculativeApplication: speculativeApplications,
			};
			return dataMap[entityType];
		},
		[
			jobs,
			companies,
			persons,
			interviews,
			jobApplicationUpdates,
			aggregators,
			keywords,
			locations,
			settings,
			users,
			_scrapedJobs,
			scrapingFilters,
			speculativeApplications,
		]
	);

	useEffect(() => {
		if (!token || !currentUser) return;
		fetchAllData().then((): void => {});
	}, [token, currentUser?.is_admin]);

	return (
		<DataContext.Provider
			value={{
				jobs,
				companies,
				persons,
				interviews,
				jobApplicationUpdates,
				aggregators,
				keywords,
				locations,
				scrapingFilters,
				countries,
				currencies,
				speculativeApplications,
				settings,
				users,
				error,
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
