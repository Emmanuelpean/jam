import React, { JSX, useState } from "react";
import { jobScraperServiceApi } from "../../services/api/Services";
import { formatErrorMessage } from "./ServiceUtils";
import LogViewer, { useLogViewerToggle } from "./LogViewer/LogViewer";
import { LastLogBar } from "./LogViewer/LastLogBar";
import { LatestRunProgress } from "./JobScrapingDashboard/LatestRunProgress";
import { RunHistoryChart } from "./JobScrapingDashboard/RunHistoryChart";
import { ErrorSummaryCard } from "./JobScrapingDashboard/ErrorSummaryCard";
import { useJobScraperServiceLogs } from "../../hooks/useJobScraperServiceLogs";
import { useJobScraperErrors } from "../../hooks/useJobScraperErrors";
import { useServiceErrors } from "../../hooks/useServiceErrors";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { DateRange } from "../../utils/TimeUtils";
import { TimeFilterPopover } from "../../components/TimeSelection/TimeFilterPopover";
import "./Service.scss";

const JobScrapingPage = (): JSX.Element => {
	const { serviceStatus, statusError } = useServiceRunnerStatus(jobScraperServiceApi);

	// Null until the TimeFilterPopover emits its real default range on mount, so we
	// don't fire a throwaway fetch for a placeholder (today-only) window first.
	const [dateRange, setDateRange] = useState<DateRange | null>(null);
	const [selectedPlatform, setSelectedPlatform] = useState("all");
	const {
		expanded: logsExpanded,
		setExpanded: setLogsExpanded,
		open: openLogViewer,
	} = useLogViewerToggle("scraper-log-viewer");

	const {
		previousServiceLogs,
		latestServiceLog,
		platformOptions,
		serviceLogError,
		loading: logsLoading,
	} = useJobScraperServiceLogs(serviceStatus?.service_running || false, dateRange);

	const {
		scraperErrors: latestScraperErrors,
		error: lastestScraperRequestError,
		loading: latestScraperErrorsLoading,
	} = useJobScraperErrors(latestServiceLog, selectedPlatform);
	const {
		scraperErrors: previousScraperErrors,
		error: previousScraperRequestError,
		loading: previousScraperErrorsLoading,
	} = useJobScraperErrors(previousServiceLogs, selectedPlatform, true);
	const { serviceErrors: lastServiceErrors, loading: lastServiceErrorsLoading } = useServiceErrors(latestServiceLog);
	const { serviceErrors: previousServiceErrors, loading: previousServiceErrorsLoading } = useServiceErrors(
		previousServiceLogs,
		true
	);

	const collectedErrors = [
		{ key: "status", label: "Service status", value: statusError },
		{ key: "serviceLogs", label: "Service logs", value: serviceLogError },
		{ key: "lastestScraperRequestError", label: "Last rating error", value: lastestScraperRequestError },
		{ key: "previousScraperRequestError", label: "Latest rating error", value: previousScraperRequestError },
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

			<LatestRunProgress latestLog={latestServiceLog} isRunning={serviceStatus?.service_running || false} />

			<LogViewer
				id="scraper-log-viewer"
				api={jobScraperServiceApi}
				isServiceRunning={serviceStatus?.service_running || false}
				serviceStatus={serviceStatus}
				expanded={logsExpanded}
				onExpandedChange={setLogsExpanded}
			/>

			<RunHistoryChart
				serviceLogData={previousServiceLogs}
				selectedPlatform={selectedPlatform}
				platformOptions={platformOptions}
				onPlatformChange={setSelectedPlatform}
				isRunning={serviceStatus?.service_running || false}
				loading={logsLoading}
			/>

			<ErrorSummaryCard
				latestServiceLogs={previousServiceLogs}
				lastScraperErrors={latestScraperErrors}
				latestScraperErrors={previousScraperErrors}
				lastServiceErrors={lastServiceErrors}
				latestServiceErrors={previousServiceErrors}
				isRunning={serviceStatus?.service_running || false}
				loading={
					logsLoading ||
					latestScraperErrorsLoading ||
					previousScraperErrorsLoading ||
					lastServiceErrorsLoading ||
					previousServiceErrorsLoading
				}
			/>
		</div>
	);
};

export default JobScrapingPage;
