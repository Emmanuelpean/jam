import { ApiResponse, ApiResponsePromise, baseApi, serviceApi } from "./Base";
import { BaseServiceApi, LogResponse, ServiceRunnerResponse, ServiceStatus } from "./Services";
import {
	AnthropicDailyUsageData,
	ApifyBalanceData,
	ApifyDailyUsageData,
	BrightdataBalanceData,
	BrightdataDailyUsageData,
	StripeDailyIncomeData,
} from "../schemas/Services";

interface DateRangeQuery {
	start_date?: string;
	end_date?: string;
}

const dateRangeQs = ({ start_date, end_date }: DateRangeQuery): string => {
	const params: string[] = [];
	if (start_date) params.push(`start_date=${start_date}`);
	if (end_date) params.push(`end_date=${end_date}`);
	return params.length > 0 ? `?${params.join("&")}` : "";
};

export const externalServiceMonitoringApi = {
	getAnthropicHistory: async (range: DateRangeQuery, token: string): Promise<AnthropicDailyUsageData[]> => {
		const res: ApiResponse<AnthropicDailyUsageData[]> = await baseApi.get(
			`external-service-monitoring-history/anthropic${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getApifyHistory: async (range: DateRangeQuery, token: string): Promise<ApifyDailyUsageData[]> => {
		const res: ApiResponse<ApifyDailyUsageData[]> = await baseApi.get(
			`external-service-monitoring-history/apify${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getBrightdataHistory: async (range: DateRangeQuery, token: string): Promise<BrightdataDailyUsageData[]> => {
		const res: ApiResponse<BrightdataDailyUsageData[]> = await baseApi.get(
			`external-service-monitoring-history/brightdata${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getStripeHistory: async (range: DateRangeQuery, token: string): Promise<StripeDailyIncomeData[]> => {
		const res: ApiResponse<StripeDailyIncomeData[]> = await baseApi.get(
			`external-service-monitoring-history/stripe${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getBrightdataBalance: async (token: string): Promise<BrightdataBalanceData | null> => {
		const res: ApiResponse<BrightdataBalanceData | null> = await baseApi.get(
			"external-service-monitoring-history/brightdata/balance",
			token
		);
		return res.data;
	},
	getApifyBalance: async (token: string): Promise<ApifyBalanceData | null> => {
		const res: ApiResponse<ApifyBalanceData | null> = await baseApi.get(
			"external-service-monitoring-history/apify/balance",
			token
		);
		return res.data;
	},
};

// Service runner API — start takes no arguments (period fixed at 24h on the backend).
interface ExternalServiceMonitoringRunnerApi extends BaseServiceApi {
	start: (token: string) => ApiResponsePromise<ServiceRunnerResponse>;
}

export const externalServiceMonitoringRunnerApi: ExternalServiceMonitoringRunnerApi = {
	getStatus: (token: string): ApiResponsePromise<ServiceStatus> =>
		serviceApi.get("external-service-monitoring-service/status", token),
	stop: (token: string): ApiResponsePromise<ServiceRunnerResponse> =>
		serviceApi.post("external-service-monitoring-service/stop", {}, token),
	getLogs: (lines: number, token: string): ApiResponsePromise<LogResponse> =>
		serviceApi.get(`external-service-monitoring-service/logs?lines=${lines}`, token),
	start: (token: string): ApiResponsePromise<ServiceRunnerResponse> =>
		serviceApi.post("external-service-monitoring-service/start", {}, token),
};
