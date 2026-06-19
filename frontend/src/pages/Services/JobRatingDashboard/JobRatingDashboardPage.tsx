import React, { JSX, useState } from "react";
import { jobRatingServiceRunnerApi } from "../../../services/api/Services";
import LogViewer from "../LogViewer/LogViewer";
import { LatestRunProgress } from "./LatestRunProgress";
import { RunHistoryChart } from "./RunHistoryChart";
import { ErrorSummaryCard } from "./ErrorSummaryCard";
import { useJobRatingServiceLogs } from "../../../hooks/useJobRatingServiceLog";
import { useJobRatingErrors } from "../../../hooks/useJobRatingErrors";
import { DateRange } from "../../../utils/TimeUtils";
import TimeSelection from "../../../components/TimeSelection/TimeSelection";
import { formatErrorMessage, LiftedServiceStatusProps } from "../ServiceUtils";
import "../Service.scss";

const JobRatingDashboard = ({ serviceStatus, statusError }: LiftedServiceStatusProps): JSX.Element => {
	const [dateRange, setDateRange] = useState<DateRange>({ start: new Date(), end: new Date() });

	const {
		previousServiceLogs,
		latestServiceLog,
		serviceLogError,
		loading: logsLoading,
	} = useJobRatingServiceLogs(serviceStatus?.service_running || false, dateRange);

	const {
		scraperErrors: previousRatingErrors,
		error: previousRatingRequestError,
		loading: previousRatingErrorsLoading,
	} = useJobRatingErrors(previousServiceLogs, true);
	const {
		scraperErrors: lastRatingErrors,
		error: latestRatingRequestError,
		loading: lastRatingErrorsLoading,
	} = useJobRatingErrors(latestServiceLog);

	const collectedErrors = [
		{ key: "status", label: "Service status", value: statusError },
		{ key: "serviceLogs", label: "Service logs", value: serviceLogError },
		{ key: "lastRatingError", label: "Last rating error", value: latestRatingRequestError },
		{ key: "latestRatingError", label: "Latest rating error", value: previousRatingRequestError },
	].filter((e) => e.value);

	return (
		<div>
			{collectedErrors.length > 0 && (
				<div className="alert alert-danger mb-4 shadow-sm rounded-3" role="alert">
					<div className="d-flex align-items-start">
						<i className="bi bi-exclamation-triangle-fill me-3 fs-5"></i>
						<div className="flex-grow-1">
							<h5 className="alert-heading mb-2">System Errors Detected</h5>
							<ul className="mb-0">
								{collectedErrors.map((error) => (
									<li key={error.key}>
										<strong>{error.label}:</strong> {formatErrorMessage(error.value)}
									</li>
								))}
							</ul>
						</div>
					</div>
				</div>
			)}

			<LatestRunProgress latestLog={latestServiceLog} isRunning={serviceStatus?.service_running || false} />

			<LogViewer
				api={jobRatingServiceRunnerApi}
				isServiceRunning={serviceStatus?.service_running || false}
				serviceStatus={serviceStatus}
			/>

			<div id="history-filters" className="status-card filter-card mt-4">
				<div className="d-flex align-items-center gap-3 flex-wrap">
					<span className="filter-card-label">
						<i className="bi bi-funnel me-2" />
						Filters
					</span>
					<TimeSelection onDateRangeChange={setDateRange} defaultMode="period" />
				</div>
			</div>

			<RunHistoryChart
				serviceLogData={previousServiceLogs}
				isRunning={serviceStatus?.service_running || false}
				loading={logsLoading}
			/>

			<ErrorSummaryCard
				latestServiceLogs={previousServiceLogs}
				lastRatingErrors={lastRatingErrors}
				latestRatingErrors={previousRatingErrors}
				isRunning={serviceStatus?.service_running || false}
				loading={logsLoading || previousRatingErrorsLoading || lastRatingErrorsLoading}
			/>
		</div>
	);
};

export default JobRatingDashboard;
