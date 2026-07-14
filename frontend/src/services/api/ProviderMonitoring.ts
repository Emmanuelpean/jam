import { ApiResponse, baseApi } from "./Base";
import { createServiceApi } from "./Services";
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

export const providerMonitoringApi = {
	getAnthropicHistory: async (range: DateRangeQuery, token: string): Promise<AnthropicDailyUsageData[]> => {
		const res: ApiResponse<AnthropicDailyUsageData[]> = await baseApi.get(
			`provider-monitoring-history/anthropic${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getApifyHistory: async (range: DateRangeQuery, token: string): Promise<ApifyDailyUsageData[]> => {
		const res: ApiResponse<ApifyDailyUsageData[]> = await baseApi.get(
			`provider-monitoring-history/apify${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getBrightdataHistory: async (range: DateRangeQuery, token: string): Promise<BrightdataDailyUsageData[]> => {
		const res: ApiResponse<BrightdataDailyUsageData[]> = await baseApi.get(
			`provider-monitoring-history/brightdata${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getStripeHistory: async (range: DateRangeQuery, token: string): Promise<StripeDailyIncomeData[]> => {
		const res: ApiResponse<StripeDailyIncomeData[]> = await baseApi.get(
			`provider-monitoring-history/stripe${dateRangeQs(range)}`,
			token
		);
		return res.data;
	},
	getBrightdataBalance: async (token: string): Promise<BrightdataBalanceData | null> => {
		const res: ApiResponse<BrightdataBalanceData | null> = await baseApi.get(
			"provider-monitoring-history/brightdata/balance",
			token
		);
		return res.data;
	},
	getApifyBalance: async (token: string): Promise<ApifyBalanceData | null> => {
		const res: ApiResponse<ApifyBalanceData | null> = await baseApi.get(
			"provider-monitoring-history/apify/balance",
			token
		);
		return res.data;
	},
};

export const providerMonitoringRunnerApi = createServiceApi("provider_monitoring_service");
