import { createContext, useContext } from "react";
import { ApiResponsePromise } from "../services/api/Base";
import { ApiError } from "../services/api/ApiError";
import { EmailTemplate } from "../services/api/Others";
import {
	AggregatorData,
	CompanyData,
	EnrichedInterviewData,
	EnrichedJobApplicationUpdateData,
	EnrichedJobData,
	FileData,
	KeywordData,
	PersonData,
	SpeculativeApplicationData,
} from "../services/schemas/DataTables";
import { ScrapingFilterData } from "../services/schemas/Services";
import { SettingData, UserData } from "../services/schemas/Core";
import type { EntityCreateDataMap, EntityRawDataMap, EntityType, EntityTypeDataMap, JamData } from "./DataContext";

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
	files: FileData[];
	emailTemplates: EmailTemplate[];

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

export const DataContext = createContext<DataContextValue | undefined>(undefined);

export const useDataContext = (): DataContextValue => {
	const context: DataContextValue | undefined = useContext(DataContext);
	if (!context) throw new Error("useDataContext must be used within a DataProvider");
	return context;
};

// Non-throwing variant for components that render outside the DataProvider (e.g. when logged out).
export const useDataContextOptional = (): DataContextValue | undefined => useContext(DataContext);
