import { createCrudApi, CrudApi } from "./Crud";
import { ApiResponsePromise, baseApi } from "./Base";
import {
	AggregatorData,
	CompanyData,
	FileWithContentData,
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	PersonData,
	SpeculativeApplicationData,
} from "../schemas/DataTables";
import { SettingData } from "../schemas/Core";
import { Currency } from "../schemas/Others";
import { ScrapingFilterData } from "../schemas/Services";

export const jobsApi: CrudApi<JobData> = createCrudApi("jobs");
export const companiesApi: CrudApi<CompanyData> = createCrudApi("companies");
export const keywordsApi: CrudApi<KeywordData> = createCrudApi("keywords");
export const personsApi: CrudApi<PersonData> = createCrudApi("persons");
export const aggregatorsApi: CrudApi<AggregatorData> = createCrudApi("aggregators");
export const interviewsApi: CrudApi<InterviewData> = createCrudApi("interviews");
export const jobApplicationUpdatesApi: CrudApi<JobApplicationUpdateData> = createCrudApi("job-application-updates");
export const settingsApi: CrudApi<SettingData> = createCrudApi("settings");
export const currenciesApi: CrudApi<Currency> = createCrudApi("others/currencies");
export const scrapingExclusionFilterApi: CrudApi<ScrapingFilterData> = createCrudApi("scraping-exclusion-filters");
export const scrapingFavouriteFilterApi: CrudApi<ScrapingFilterData> = createCrudApi("scraping-favourite-filters");
export const speculativeApplicationsApi: CrudApi<SpeculativeApplicationData> =
	createCrudApi("speculative-applications");

interface FilesApi extends CrudApi<FileWithContentData> {
	download: (id: number, filename: string, token: string) => Promise<void>;
	preview: (id: number, token: string) => Promise<void>;
	getContent: (id: number, token: string) => ApiResponsePromise<FileWithContentData>;
}

export const filesApi: FilesApi = {
	...createCrudApi<FileWithContentData>("files"),
	download: (id: number, filename: string, token: string): Promise<void> =>
		baseApi.downloadFile(`files/${id}/download`, filename, token),
	preview: async (id: number, token: string): Promise<void> => {
		const response = await baseApi.get(`files/${id}/download`, token, { responseType: "blob" });
		const url = window.URL.createObjectURL(response.data);
		window.open(url, "_blank");
	},
	getContent: (id: number, token: string): ApiResponsePromise<FileWithContentData> => baseApi.get(`files/${id}/content`, token),
};
