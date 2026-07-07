import React, { JSX, useState } from "react";
import { jobRatingServiceRunnerApi } from "../../services/api/Services";
import { formatErrorMessage } from "./ServiceUtils";
import LogViewer, { useLogViewerToggle } from "./LogViewer/LogViewer";
import { LastLogBar } from "./LogViewer/LastLogBar";
import { LatestRunProgress } from "./JobRatingDashboard/LatestRunProgress";
import { RunHistoryChart } from "./JobRatingDashboard/RunHistoryChart";
import { ErrorSummaryCard } from "./ErrorSummaryCard";
import { useJobRatingServiceLogs } from "../../hooks/useJobRatingServiceLog";
import { useServiceErrors } from "../../hooks/useServiceErrors";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { DateRange } from "../../utils/TimeUtils";
import { TimeFilterPopover } from "../../components/TimeSelection/TimeFilterPopover";
import "./Service.scss";

const JobRatingPage = (): JSX.Element => {
	const { serviceStatus, statusError } = useServiceRunnerStatus(jobRatingServiceRunnerApi);
	const [dateRange, setDateRange] = useState<DateRange | null>(null);
	const [showAcknowledged, setShowAcknowledged] = useState(false);
	const {
		expanded: logsExpanded,
		setExpanded: setLogsExpanded,
		open: openLogViewer,
	} = useLogViewerToggle("rating-log-viewer");

	const {
		previousServiceLogs,
		latestServiceLog,
		serviceLogError,
		loading: logsLoading,
	} = useJobRatingServiceLogs(serviceStatus?.is_running || false, dateRange);

	const {
		errors: currentErrors,
		requestError: currentErrorsRequestError,
		loading: currentErrorsLoading,
		acknowledge: acknowledgeCurrent,
	} = useServiceErrors(latestServiceLog, "job_rating_service_log_id", showAcknowledged);
	const {
		errors: previousErrors,
		requestError: previousErrorsRequestError,
		loading: previousErrorsLoading,
		acknowledge: acknowledgePrevious,
	} = useServiceErrors(previousServiceLogs, "job_rating_service_log_id", showAcknowledged, true);

	const collectedErrors = [
		{ key: "status", label: "Service status", value: statusError },
		{ key: "serviceLogs", label: "Service logs", value: serviceLogError },
		{ key: "currentErrorsRequestError", label: "Latest run errors", value: currentErrorsRequestError },
		{ key: "previousErrorsRequestError", label: "Previous run errors", value: previousErrorsRequestError },
	].filter((e) => e.value);

	return (
		<div className="scraped-jobs-page">
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

			<div className="d-flex align-items-center gap-3 mb-4 service-filter-row">
				<LastLogBar serviceStatus={serviceStatus} onClick={openLogViewer} />
				<div className="ms-auto">
					<TimeFilterPopover id="history-filters" onDateRangeChange={setDateRange} defaultMode="period" />
				</div>
			</div>

			<LatestRunProgress latestLog={latestServiceLog} isRunning={serviceStatus?.is_running || false} />

			<LogViewer
				id="rating-log-viewer"
				api={jobRatingServiceRunnerApi}
				isServiceRunning={serviceStatus?.is_running || false}
				expanded={logsExpanded}
				onExpandedChange={setLogsExpanded}
			/>

			<RunHistoryChart
				serviceLogData={previousServiceLogs}
				isRunning={serviceStatus?.is_running || false}
				loading={logsLoading}
			/>

			<ErrorSummaryCard
				current={{ errors: currentErrors, acknowledge: acknowledgeCurrent }}
				previous={{ errors: previousErrors, acknowledge: acknowledgePrevious }}
				perJob={{ title: "Job Rating Errors", discriminatorKey: "job_rating_id", emptyText: "No rating errors" }}
				showAcknowledged={showAcknowledged}
				onToggleAcknowledged={setShowAcknowledged}
				isRunning={serviceStatus?.is_running || false}
				loading={logsLoading || currentErrorsLoading || previousErrorsLoading}
			/>
		</div>
	);
};

export default JobRatingPage;
