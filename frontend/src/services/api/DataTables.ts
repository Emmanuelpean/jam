import { createCrudApi, CrudApi } from "./Crud";
import {
	AggregatorData,
	CompanyData,
	Country,
	Currency,
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	LocationData,
	PersonData,
	ScrapingFilterData,
	SettingData,
	SpeculativeApplicationData,
} from "../Schemas";

export const jobsApi: CrudApi<JobData> = createCrudApi("jobs");
export const companiesApi: CrudApi<CompanyData> = createCrudApi("companies");
export const locationsApi: CrudApi<LocationData> = createCrudApi("locations");
export const keywordsApi: CrudApi<KeywordData> = createCrudApi("keywords");
export const personsApi: CrudApi<PersonData> = createCrudApi("persons");
export const aggregatorsApi: CrudApi<AggregatorData> = createCrudApi("aggregators");
export const interviewsApi: CrudApi<InterviewData> = createCrudApi("interviews");
export const jobApplicationUpdatesApi: CrudApi<JobApplicationUpdateData> = createCrudApi("job-application-updates");
export const settingsApi: CrudApi<SettingData> = createCrudApi("settings");
export const countriesApi: CrudApi<Country> = createCrudApi("others/countries");
export const currenciesApi: CrudApi<Currency> = createCrudApi("others/currencies");
export const scrapingFilterApi: CrudApi<ScrapingFilterData> = createCrudApi("scraping-filters");
export const speculativeApplicationsApi: CrudApi<SpeculativeApplicationData> =
	createCrudApi("speculative-applications");
