// DataContext.tsx
import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
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
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	LocationData,
	PersonData,
	SettingData,
	UserData,
} from "../services/Schemas";
import { SelectOption } from "../utils/Utils";
import { fetchCountries } from "../utils/CountryUtils";
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

export interface DataContextValue {
	// Data arrays
	jobs: JobData[];
	companies: CompanyData[];
	persons: PersonData[];
	interviews: InterviewData[];
	jobApplicationUpdates: JobApplicationUpdateData[];
	aggregators: AggregatorData[];
	keywords: KeywordData[];
	locations: LocationData[];
	settings: SettingData[];
	users: UserData[];
	countries: SelectOption[];

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
	const [jobs, setJobs] = useState<JobData[]>([]);
	const [companies, setCompanies] = useState<CompanyData[]>([]);
	const [persons, setPersons] = useState<PersonData[]>([]);
	const [interviews, setInterviews] = useState<InterviewData[]>([]);
	const [jobApplicationUpdates, setJobApplicationUpdates] = useState<JobApplicationUpdateData[]>([]);
	const [aggregators, setAggregators] = useState<AggregatorData[]>([]);
	const [keywords, setKeywords] = useState<KeywordData[]>([]);
	const [locations, setLocations] = useState<LocationData[]>([]);
	const [settings, setSettings] = useState<SettingData[]>([]);
	const [users, setUsers] = useState<UserData[]>([]);
	const [countries, setCountries] = useState<SelectOption[]>([]);
	const { showLoading, hideLoading } = useLoading();
	const [error, setError] = useState<ApiError | null>(null);

	const fetchAllData = async () => {
		showLoading();
		setError(null);
		try {
			const promises = [
				await jobsApi.getAll(token),
				await companiesApi.getAll(token),
				await personsApi.getAll(token),
				await interviewsApi.getAll(token),
				await jobApplicationUpdatesApi.getAll(token),
				await aggregatorsApi.getAll(token),
				await keywordsApi.getAll(token),
				await locationsApi.getAll(token),
				await fetchCountries(),
			];

			// Only add admin-only calls if user is admin
			if (currentUser?.is_admin) {
				promises.push(await settingsApi.getAll(token));
				promises.push(await userApi.getAll(token));
			}

			const results = await Promise.all(promises);

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
				countriesData,
				...adminData
			] = results;

			setJobs(jobsData || []);
			setCompanies(companiesData || []);
			setPersons(personsData || []);
			setInterviews(interviewsData || []);
			setJobApplicationUpdates(jobApplicationUpdatesData || []);
			setAggregators(aggregatorsData || []);
			setKeywords(keywordsData || []);
			setLocations(locationsData || []);
			setCountries(countriesData || []);

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

	// Helper to refetch all jobs
	const refetchJobs = useCallback(async () => {
		try {
			const jobsData = await jobsApi.getAll(token);
			setJobs(jobsData || []);
		} catch (error) {
			console.error("Failed to refetch jobs:", error);
		}
	}, [token]);

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
			jobs: setJobs,
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

				// Refetch jobs if jobs, interviews, or jobApplicationUpdates changed
				if (type === "jobs" || type === "interviews" || type === "jobApplicationUpdates") {
					await refetchJobs();
				}

				return apiResult;
			} catch (error) {
				console.error(`Failed to update ${type}:`, error);
				throw error;
			}
		},
		[token, refetchJobs],
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

				// Refetch jobs if jobs, interviews, or jobApplicationUpdates changed
				if (type === "jobs" || type === "interviews" || type === "jobApplicationUpdates") {
					await refetchJobs();
				}
			} catch (error) {
				console.error(`Failed to delete ${type}:`, error);
				throw error;
			}
		},
		[token, refetchJobs],
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

				// Refetch jobs if jobs, interviews, or jobApplicationUpdates changed
				if (type === "jobs" || type === "interviews" || type === "jobApplicationUpdates") {
					await refetchJobs();
				}

				return apiResult;
			} catch (error) {
				console.error(`Failed to add ${type}:`, error);
				throw error;
			}
		},
		[token, refetchJobs],
	);

	useEffect(() => {
		fetchAllData().then(() => {});
	}, [token]);

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
				countries,
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
