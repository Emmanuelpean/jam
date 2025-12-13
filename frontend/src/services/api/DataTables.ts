import { createCrudApi, CrudApi } from "./Base";

export const jobsApi: CrudApi = createCrudApi("jobs");
export const companiesApi: CrudApi = createCrudApi("companies");
export const locationsApi: CrudApi = createCrudApi("locations");
export const keywordsApi: CrudApi = createCrudApi("keywords");
export const personsApi: CrudApi = createCrudApi("persons");
export const aggregatorsApi: CrudApi = createCrudApi("aggregators");
export const interviewsApi: CrudApi = createCrudApi("interviews");
export const jobApplicationUpdatesApi: CrudApi = createCrudApi("jobapplicationupdates");
export const settingsApi: CrudApi = createCrudApi("settings");
export const countriesApi: CrudApi = createCrudApi("others/countries");
export const currenciesApi: CrudApi = createCrudApi("others/currencies");
