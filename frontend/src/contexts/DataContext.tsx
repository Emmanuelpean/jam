import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
	aggregatorsApi,
	ApiError,
	companiesApi,
	interviewsApi,
	jobApplicationUpdatesApi,
	jobsApi,
	keywordsApi,
	locationsApi,
	personsApi,
	settingsApi,
	userApi,
} from "../services/Api";
import { useAuth } from "./AuthContext";
import {
	AggregatorData,
	CompanyData,
	EnrichedJobData,
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	LocationData,
	PersonData,
	SettingData,
	UserData,
} from "../services/Schemas";
import { useLoading } from "./LoadingContext";

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
	| "users";

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

export interface DataContextValue {
	// Data arrays
	jobs: EnrichedJobData[];
	companies: CompanyData[];
	persons: PersonData[];
	interviews: InterviewData[];
	jobApplicationUpdates: JobApplicationUpdateData[];
	aggregators: AggregatorData[];
	keywords: KeywordData[];
	locations: LocationData[];
	settings: SettingData[];
	users: UserData[];

	error: ApiError | null;
	reloadAll: () => void;

	// Generic update functions
	updateEntity: <T extends EntityType>(type: T, id: number, data: any) => Promise<any>;
	deleteEntity: <T extends EntityType>(type: T, id: number) => Promise<void>;
	addEntity: <T extends EntityType>(type: T, data: any) => Promise<any>;
}

const DataContext = createContext<DataContextValue | undefined>(undefined);

export const DataProvider: React.FC<{ token: string; children: React.ReactNode }> = ({ token, children }) => {
	const { currentUser } = useAuth();
	const [rawJobs, setRawJobs] = useState<JobData[]>([]);
	const [companies, setCompanies] = useState<CompanyData[]>([]);
	const [persons, setPersons] = useState<PersonData[]>([]);
	const [interviews, setInterviews] = useState<InterviewData[]>([]);
	const [jobApplicationUpdates, setJobApplicationUpdates] = useState<JobApplicationUpdateData[]>([]);
	const [aggregators, setAggregators] = useState<AggregatorData[]>([]);
	const [keywords, setKeywords] = useState<KeywordData[]>([]);
	const [locations, setLocations] = useState<LocationData[]>([]);
	const [settings, setSettings] = useState<SettingData[]>([]);
	const [users, setUsers] = useState<UserData[]>([]);
	const { showLoading, hideLoading, updateProgress } = useLoading();
	const [error, setError] = useState<ApiError | null>(null);

	const jobs: EnrichedJobData[] = useMemo<EnrichedJobData[]>((): EnrichedJobData[] => {
		return rawJobs.map((job: JobData): EnrichedJobData => {
			const jobInterviews = interviews.filter((i) => i.job_id === job.id);
			const jobUpdates = jobApplicationUpdates.filter((u) => u.job_id === job.id);

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
						lastUpdateType = `Interview #${jobInterviews.length}`;
					}
				}

				if (jobUpdates.length > 0) {
					const latestUpdate = jobUpdates.reduce((latest, current) =>
						new Date(current.date) > new Date(latest.date) ? current : latest,
					);
					if (new Date(latestUpdate.date) > mostRecentDate) {
						lastUpdateType = `Update #${jobUpdates.length}`;
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

			return {
				...job,
				last_update_date: lastUpdateDate,
				last_update_type: lastUpdateType,
				days_since_last_update: daysSinceLastUpdate,
				days_until_deadline: daysUntilDeadline,
			};
		});
	}, [rawJobs, interviews, jobApplicationUpdates]);

	const fetchAllData = async () => {
		setError(null);

		// Define all promises with their labels
		const fetchOperations = [
			{ promise: jobsApi.getAll(token), label: "Jobs" },
			{ promise: companiesApi.getAll(token), label: "Companies" },
			{ promise: personsApi.getAll(token), label: "Persons" },
			{ promise: interviewsApi.getAll(token), label: "Interviews" },
			{ promise: jobApplicationUpdatesApi.getAll(token), label: "Updates" },
			{ promise: aggregatorsApi.getAll(token), label: "Aggregators" },
			{ promise: keywordsApi.getAll(token), label: "Keywords" },
			{ promise: locationsApi.getAll(token), label: "Locations" },
		];

		// Add admin-only calls if user is admin
		if (currentUser?.is_admin) {
			fetchOperations.push(
				{ promise: settingsApi.getAll(token), label: "Settings" },
				{ promise: userApi.getAll(token), label: "Users" },
			);
		}

		const totalOperations = fetchOperations.length;
		let completedOperations = 0;

		// Show initial loading state
		showLoading("Initialising data load...", 0);

		try {
			// Track progress for each promise
			const trackedPromises = fetchOperations.map(({ promise, label }) =>
				promise.then((result) => {
					completedOperations++;
					const progressPercentage = Math.round((completedOperations / totalOperations) * 100);
					updateProgress(progressPercentage, `Loading ${label}...`);
					return result;
				}),
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
				...adminData
			] = results;

			setRawJobs(jobsData || []);
			setCompanies(companiesData || []);
			setPersons(personsData || []);
			setInterviews(interviewsData || []);
			setJobApplicationUpdates(jobApplicationUpdatesData || []);
			setAggregators(aggregatorsData || []);
			setKeywords(keywordsData || []);
			setLocations(locationsData || []);

			if (currentUser?.is_admin) {
				setSettings(adminData[0] || []);
				setUsers(adminData[1] || []);
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
		};
		return apiMap[type];
	};

	// Helper to get setter function for an entity type
	const getSetter = (type: EntityType) => {
		const setterMap = {
			jobs: setRawJobs,
			companies: setCompanies,
			persons: setPersons,
			interviews: setInterviews,
			jobApplicationUpdates: setJobApplicationUpdates,
			aggregators: setAggregators,
			keywords: setKeywords,
			locations: setLocations,
			settings: setSettings,
			users: setUsers,
		};
		return setterMap[type];
	};

	// Generic update function - refetch jobs if needed
	const updateEntity = useCallback(
		async <T extends EntityType>(type: T, id: number, updatedData: any): Promise<any> => {
			try {
				// Update backend first
				const api = getApi(type);
				const apiResult = await api.update(id, updatedData, token);

				// Update the entity itself in context
				const setter = getSetter(type);
				setter((prev: any[]): any[] => prev.map((item: any) => (item.id === id ? apiResult : item)));

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
				await api.delete(id, token);

				// Remove from the entity's own array
				const setter = getSetter(type);
				setter((prev: any[]): any[] => prev.filter((item: any) => item.id !== id));
			} catch (error) {
				console.error(`Failed to delete ${type}:`, error);
				throw error;
			}
		},
		[token],
	);

	// Generic add function - refetch jobs if needed
	const addEntity = useCallback(
		async <T extends EntityType>(type: T, newData: any): Promise<any> => {
			try {
				// Create on backend first
				const api = getApi(type);
				const apiResult = await api.create(newData, token);

				// Add to the entity's own array
				const setter = getSetter(type);
				setter((prev: any[]): any[] => [...prev, apiResult]);

				return apiResult;
			} catch (error) {
				console.error(`Failed to add ${type}:`, error);
				throw error;
			}
		},
		[token],
	);

	useEffect(() => {
		if (!currentUser) return;

		fetchAllData().then(() => {});
	}, [token, currentUser?.token, currentUser?.is_admin]);

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
				settings,
				users,
				error,
				reloadAll: fetchAllData,
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
