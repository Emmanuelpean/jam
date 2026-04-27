import { createCrudApi, CrudApi } from "./Crud";
import {
	AggregatorData,
	CompanyData,
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	PersonData,
	SpeculativeApplicationData,
} from "../schemas/DataTables";
import { SettingData } from "../schemas/Core";
import { Country, Currency } from "../schemas/Others";
import { ScrapingFilterData } from "../schemas/Services";

export const jobsApi: CrudApi<JobData> = createCrudApi("jobs");
export const companiesApi: CrudApi<CompanyData> = createCrudApi("companies");
export const keywordsApi: CrudApi<KeywordData> = createCrudApi("keywords");
export const personsApi: CrudApi<PersonData> = createCrudApi("persons");
export const aggregatorsApi: CrudApi<AggregatorData> = createCrudApi("aggregators");
export const interviewsApi: CrudApi<InterviewData> = createCrudApi("interviews");
export const jobApplicationUpdatesApi: CrudApi<JobApplicationUpdateData> = createCrudApi("job-application-updates");
export const settingsApi: CrudApi<SettingData> = createCrudApi("settings");
export const countriesApi: CrudApi<Country> = createCrudApi("others/countries");
export const currenciesApi: CrudApi<Currency> = createCrudApi("others/currencies");
export const scrapingExclusionFilterApi: CrudApi<ScrapingFilterData> = createCrudApi("scraping-exclusion-filters");
export const scrapingFavouriteFilterApi: CrudApi<ScrapingFilterData> = createCrudApi("scraping-favourite-filters");
export const speculativeApplicationsApi: CrudApi<SpeculativeApplicationData> =
	createCrudApi("speculative-applications");
