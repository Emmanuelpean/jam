import { JobRatingServiceLogData } from "../services/schemas/Services";
import { jobRatingServiceLogApi } from "../services/api/Services";
import { DateRange } from "../utils/TimeUtils";
import { useServiceLogs } from "./useServiceLogs";

export const useJobRatingServiceLogs = (isServiceRunning: boolean, dateRange: DateRange) => {
	return useServiceLogs<JobRatingServiceLogData>(jobRatingServiceLogApi, isServiceRunning, dateRange);
};
