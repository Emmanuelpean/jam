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
	scrapedJobFilterApi,
	settingsApi,
} from "../services/api/DataTables";
import { ApiError, ApiResponse, ApiResponsePromise } from "../services/api/Base";
import { userApi } from "../services/api/Users";
import { scrapedJobApi } from "../services/api/Services";
import { useAuth } from "./AuthContext";
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
	ScrapedJobData,
	ScrapedJobFilterData,
	SettingData,
	UserData,
} from "../services/Schemas";
import { useLoading } from "./LoadingContext";
import { sortByKey } from "../utils/Utils";

export type EntityType =
	| "jobs"
	| "companies"
	| "persons"
	| "interviews"
	| "jobApplicationUpdates"
	| "aggregators"
	| "keywords"
	| "locations"
	| "settings"
	| "users"
	| "scrapedJobs"
	| "scrapedJobFilters";

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
	| ScrapedJobFilterData;

export const endpointToEntityType = (endpoint: string): EntityType | null => {
	const mapping: Record<string, EntityType> = {
		jobs: "jobs",
		companies: "companies",
		persons: "persons",
		interviews: "interviews",
		jobapplicationupdates: "jobApplicationUpdates",
		aggregators: "aggregators",
		keywords: "keywords",
		locations: "locations",
		settings: "settings",
		users: "users",
		scraped_jobs: "scrapedJobs",
		scraped_job_filters: "scrapedJobFilters",
	};
	return mapping[endpoint.toLowerCase()] || null;
};

export interface Currency {
	symbol: string;
	name: string;
	symbol_native: string;
	decimal_digits: number;
	rounding: number;
	code: string;
	name_plural: string;
}

export interface Country {
	name: string;
	code: string;
}

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
	settings: SettingData[];
	scrapedJobFilters: ScrapedJobFilterData[];
	users: UserData[];
	countries: Country[];
	currencies: Currency[];

	error: ApiError | null;

	// Generic update functions
	addEntity: <T extends EntityType>(type: T, data: any) => Promise<ApiResponse<JamData>>;
	updateEntity: <T extends EntityType>(type: T, id: number, data: any) => Promise<ApiResponse<JamData>>;
	deleteEntity: <T extends EntityType>(type: T, id: number) => Promise<void>;
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
	const [settings, setSettings] = useState<SettingData[]>([]);
	const [scrapedJobFilters, setScrapedJobFilters] = useState<ScrapedJobFilterData[]>([]);
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
				(i: InterviewData): boolean => i.job_id === job.id,
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
				(u: JobApplicationUpdateData): boolean => u.job_id === job.id,
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
				(i: InterviewData): boolean => i.job_id === job.id,
			);
			const jobUpdates: JobApplicationUpdateData[] = rawJobApplicationUpdates.filter(
				(u: JobApplicationUpdateData): boolean => u.job_id === job.id,
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
						new Date(current.date) > new Date(latest.date) ? current : latest,
					);
					if (new Date(latestInterview.date) > mostRecentDate) {
						mostRecentDate = new Date(latestInterview.date);
						lastUpdateType = `Interview (${jobInterviews.length})`;
					}
				}

				if (jobUpdates.length > 0) {
					const latestUpdate = jobUpdates.reduce((latest, current) =>
						new Date(current.date) > new Date(latest.date) ? current : latest,
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
					(c: CompanyData): boolean => c.id === job.company_id,
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
			{ promise: companiesApi.getAll(token), label: "Companies" } as TypedFetchOperation<CompanyData[]>,
			{ promise: personsApi.getAll(token), label: "Persons" } as TypedFetchOperation<PersonData[]>,
			{ promise: interviewsApi.getAll(token), label: "Interviews" } as TypedFetchOperation<InterviewData[]>,
			{ promise: jobApplicationUpdatesApi.getAll(token), label: "Updates" } as TypedFetchOperation<
				JobApplicationUpdateData[]
			>,
			{ promise: aggregatorsApi.getAll(token), label: "Aggregators" } as TypedFetchOperation<AggregatorData[]>,
			{ promise: keywordsApi.getAll(token), label: "Keywords" } as TypedFetchOperation<KeywordData[]>,
			{ promise: locationsApi.getAll(token), label: "Locations" } as TypedFetchOperation<LocationData[]>,
			{ promise: scrapedJobFilterApi.getAll(token), label: "Scraped Job Filters" } as TypedFetchOperation<
				ScrapedJobFilterData[]
			>,
			{ promise: currenciesApi.getAll(token), label: "Miscellaneous" } as TypedFetchOperation<Currency[]>,
			{ promise: countriesApi.getAll(token), label: "Miscellaneous" } as TypedFetchOperation<Country[]>,
		];

		// Add admin-only calls if user is admin
		if (currentUser?.is_admin) {
			fetchOperations.push(
				{ promise: settingsApi.getAll(token), label: "Settings" } as TypedFetchOperation<SettingData[]>,
				{ promise: userApi.getAll(token), label: "Users" } as TypedFetchOperation<UserData[]>,
			);
		}

		const totalOperations = fetchOperations.length;
		let completedOperations = 0;

		// Show initial loading state
		showLoading("Initialising data load...", 0);

		try {
			// Track progress for each promise
			const trackedPromises = fetchOperations.map(({ promise, label }) =>
				promise.then(
					(
						result: ApiResponse<(JamData | Country | Currency)[]>,
					): ApiResponse<(JamData | Country | Currency)[]> => {
						completedOperations++;
						const progressPercentage = Math.round((completedOperations / totalOperations) * 100);
						updateProgress(progressPercentage, `Loading ${label}...`);
						return result;
					},
				),
			);

			const results = await Promise.all(trackedPromises);

			// Destructure based on what we fetched
			const [
				jobsData,
				companiesData,
				personsData,
				interviewsData,
				jobApplicationUpdatesData,
				aggregatorsData,
				keywordsData,
				locationsData,
				scrapedJobFiltersData,
				currenciesData,
				countriesData,
				...adminData
			] = results;

			setRawJobs(jobsData.data || []);
			setCompanies(companiesData.data || []);
			setPersons(personsData.data || []);
			setRawInterviews(interviewsData.data || []);
			setRawJobApplicationUpdates(jobApplicationUpdatesData.data || []);
			setAggregators(aggregatorsData.data || []);
			setKeywords(keywordsData.data || []);
			setLocations(locationsData.data || []);
			setScrapedJobFilters(scrapedJobFiltersData.data || []);
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

	// Helper to get API instance for an entity type
	const getApi = (type: EntityType) => {
		const apiMap = {
			jobs: jobsApi,
			companies: companiesApi,
			persons: personsApi,
			interviews: interviewsApi,
			jobApplicationUpdates: jobApplicationUpdatesApi,
			aggregators: aggregatorsApi,
			keywords: keywordsApi,
			locations: locationsApi,
			settings: settingsApi,
			users: userApi,
			scrapedJobs: scrapedJobApi,
			scrapedJobFilters: scrapedJobFilterApi,
		};
		return apiMap[type];
	};

	// Helper to get setter function for an entity type
	const getSetter = (type: EntityType) => {
		const setterMap = {
			jobs: setRawJobs,
			companies: setCompanies,
			persons: setPersons,
			interviews: setRawInterviews,
			jobApplicationUpdates: setRawJobApplicationUpdates,
			aggregators: setAggregators,
			keywords: setKeywords,
			locations: setLocations,
			settings: setSettings,
			users: setUsers,
			scrapedJobs: setScrapedJobs,
			scrapedJobFilters: setScrapedJobFilters,
		};
		return setterMap[type];
	};

	const updateData = (apiResult: ApiResponse<JamData>, entityType: EntityType) => {
		const setter = getSetter(entityType);
		if (apiResult.status === 200) {
			setter((prev: any[]): any[] =>
				prev.map((item: any) => (item.id === apiResult.data.id ? apiResult.data : item)),
			);
		} else if (apiResult.status === 201) {
			setter((prev: any[]): any[] => [...prev, apiResult.data]);
		} else if (apiResult.status === 204 || apiResult.status === 202) {
			setter((prev: any[]): any[] => prev.filter((item: any): boolean => item.id !== apiResult.data.id));
		}
	};

	// Generic add function - refetch jobs if needed
	const addEntity = useCallback(
		async <T extends EntityType>(type: T, newData: any): Promise<ApiResponse<JamData>> => {
			try {
				// Create on backend first
				const api = getApi(type);
				const apiResult = await api.create(newData, token);
				updateData(apiResult, type);
				return apiResult;
			} catch (error) {
				console.error(`Failed to add ${type}:`, error);
				throw error;
			}
		},
		[token],
	);

	// Generic update function - refetch jobs if needed
	const updateEntity = useCallback(
		async <T extends EntityType>(type: T, id: number, updatedData: any): Promise<ApiResponse<JamData>> => {
			try {
				// Update backend first
				const api = getApi(type);
				const apiResult: ApiResponse<JamData> = await api.update(id, updatedData, token);
				updateData(apiResult, type);

				return apiResult;
			} catch (error) {
				console.error(`Failed to update ${type}:`, error);
				throw error;
			}
		},
		[token],
	);

	// Generic delete function - refetch jobs if needed
	const deleteEntity = useCallback(
		async <T extends EntityType>(type: T, id: number): Promise<void> => {
			try {
				// Delete from backend first
				const api = getApi(type);
				const apiResult: ApiResponse<JamData> = await api.delete(id, token);
				updateData(apiResult, type);
			} catch (error) {
				console.error(`Failed to delete ${type}:`, error);
				throw error;
			}
		},
		[token],
	);

	useEffect(() => {
		if (!token || !currentUser) return;
		fetchAllData().then(() => {});
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
				scrapedJobFilters,
				countries,
				currencies,
				settings,
				users,
				error,
				updateEntity,
				deleteEntity,
				addEntity,
			}}
		>
			{children}
		</DataContext.Provider>
	);
};

export const useDataContext = () => {
	const context = useContext(DataContext);
	if (!context) throw new Error("useDataContext must be used within a DataProvider");
	return context;
};
