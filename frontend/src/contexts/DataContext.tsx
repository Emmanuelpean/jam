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

type EntityType =
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

interface DataContextValue {
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

	loading: boolean;
	error: ApiError | null;
	reloadAll: () => void;

	// Generic update functions
	updateEntity: <T extends EntityType>(type: T, id: number, data: any) => void;
	deleteEntity: <T extends EntityType>(type: T, id: number) => void;
	addEntity: <T extends EntityType>(type: T, data: any) => void;
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
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<ApiError | null>(null);

	const fetchAllData = async () => {
		setLoading(true);
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

			if (currentUser?.is_admin) {
				setSettings(adminData[0] || []);
				setUsers(adminData[1] || []);
			}
		} catch (e: any) {
			setError(e);
		} finally {
			setLoading(false);
		}
	};

	// Generic update function
	const updateEntity = useCallback(<T extends EntityType>(type: T, id: number, updatedData: any) => {
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

		const setter = setterMap[type];
		setter((prev: any[]): any[] => prev.map((item: any) => (item.id === id ? { ...item, ...updatedData } : item)));
	}, []);

	// Generic delete function
	const deleteEntity = useCallback(<T extends EntityType>(type: T, id: number) => {
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

		const setter = setterMap[type];
		setter((prev: any[]): any[] => prev.filter((item: any) => item.id !== id));
	}, []);

	// Generic add function
	const addEntity = useCallback(<T extends EntityType>(type: T, newData: any) => {
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

		const setter = setterMap[type];
		setter((prev: any[]): any[] => [...prev, newData]);
	}, []);

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
				loading,
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
