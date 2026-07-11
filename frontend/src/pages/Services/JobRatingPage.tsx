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
import { DateRange, toDdMmYyyyHhMm } from "../../utils/TimeUtils";
import { TimeFilterPopover } from "../../components/TimeSelection/TimeFilterPopover";
import { ServiceFilterSlot } from "./ServiceFilterSlot";
import { JobRatingServiceLogData, ServiceError } from "../../services/schemas/Services";
import "./Service.scss";

const JobRatingPage = (): JSX.Element => {
	const { serviceStatus, statusError } = useServiceRunnerStatus(jobRatingServiceRunnerApi);
	const [dateRange, setDateRange] = useState<DateRange | null>(null);
	const [showAcknowledged, setShowAcknowledged] = useState(false);
	const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
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
		errors,
		requestError: errorsRequestError,
		loading: errorsLoading,
		setAcknowledged,
	} = useServiceErrors(previousServiceLogs, "job_rating_service_log_id", showAcknowledged, true);

	const collectedErrors = [
		{ key: "status", label: "Service status", value: statusError },
		{ key: "serviceLogs", label: "Service logs", value: serviceLogError },
		{ key: "errorsRequestError", label: "Service errors", value: errorsRequestError },
	].filter((e) => e.value);

	const selectedLog: JobRatingServiceLogData | null =
		(previousServiceLogs || []).find((log: JobRatingServiceLogData): boolean => log.id === selectedLogId) ?? null;
	const displayedErrors: ServiceError[] = selectedLog
		? errors.filter((e: ServiceError): boolean => e.job_rating_service_log_id === selectedLog.id)
		: errors;
	const selectedRunLabel: string | null = selectedLog ? toDdMmYyyyHhMm(new Date(selectedLog.run_datetime)) : null;

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

			<ServiceFilterSlot>
				<TimeFilterPopover id="history-filters" onDateRangeChange={setDateRange} defaultMode="period" />
			</ServiceFilterSlot>

			<LastLogBar serviceStatus={serviceStatus} onClick={openLogViewer} className="mb-4" />

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
				selectedLogId={selectedLog?.id ?? null}
				onSelectLog={setSelectedLogId}
			/>

			<ErrorSummaryCard
				current={{ errors: displayedErrors, setAcknowledged }}
				perJob={{
					title: "Job Rating Errors",
					discriminatorKey: "job_rating_id",
					emptyText: "No rating errors",
				}}
				showAcknowledged={showAcknowledged}
				onToggleAcknowledged={setShowAcknowledged}
				isRunning={serviceStatus?.is_running || false}
				loading={logsLoading || errorsLoading}
				selectedRunLabel={selectedRunLabel}
				onClearSelectedRun={() => setSelectedLogId(null)}
			/>
		</div>
	);
};

export default JobRatingPage;
