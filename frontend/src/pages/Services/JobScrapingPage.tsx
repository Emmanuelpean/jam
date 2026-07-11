import React, { JSX, useState } from "react";
import { jobScraperServiceApi } from "../../services/api/Services";
import { formatErrorMessage } from "./ServiceUtils";
import LogViewer, { useLogViewerToggle } from "./LogViewer/LogViewer";
import { LastLogBar } from "./LogViewer/LastLogBar";
import { LatestRunProgress } from "./JobScrapingDashboard/LatestRunProgress";
import { RunHistoryChart } from "./JobScrapingDashboard/RunHistoryChart";
import { ErrorSummaryCard } from "./ErrorSummaryCard";
import { useJobScraperServiceLogs } from "../../hooks/useJobScraperServiceLogs";
import { useServiceErrors } from "../../hooks/useServiceErrors";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { DateRange, toDdMmYyyyHhMm } from "../../utils/TimeUtils";
import { TimeFilterPopover } from "../../components/TimeSelection/TimeFilterPopover";
import { JobScrapingServiceLogData, PlatformStat, ServiceError } from "../../services/schemas/Services";
import "./Service.scss";

const buildPlatformByJobId = (logs: JobScrapingServiceLogData[] | null): Record<number, string | null> => {
	const map: Record<number, string | null> = {};
	(logs || []).forEach((log: JobScrapingServiceLogData): void => {
		log.platform_stats.forEach((stat: PlatformStat): void => {
			stat.job_scrape_failed_ids.forEach((jobId: number): void => {
				map[jobId] = stat.name;
			});
		});
	});
	return map;
};

const JobScrapingPage = (): JSX.Element => {
	const { serviceStatus, statusError } = useServiceRunnerStatus(jobScraperServiceApi);

	// Null until the TimeFilterPopover emits its real default range on mount, so we
	// don't fire a throwaway fetch for a placeholder (today-only) window first.
	const [dateRange, setDateRange] = useState<DateRange | null>(null);
	const [selectedPlatform, setSelectedPlatform] = useState("all");
	const [showAcknowledged, setShowAcknowledged] = useState(false);
	const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
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
	} = useJobScraperServiceLogs(serviceStatus?.is_running || false, dateRange);

	const {
		errors,
		requestError: errorsRequestError,
		loading: errorsLoading,
		setAcknowledged,
	} = useServiceErrors(previousServiceLogs, "job_email_scraping_service_log_id", showAcknowledged, true);

	const collectedErrors = [
		{ key: "status", label: "Service status", value: statusError },
		{ key: "serviceLogs", label: "Service logs", value: serviceLogError },
		{ key: "errorsRequestError", label: "Service errors", value: errorsRequestError },
	].filter((e) => e.value);

	const selectedLog: JobScrapingServiceLogData | null =
		(previousServiceLogs || []).find((log: JobScrapingServiceLogData): boolean => log.id === selectedLogId) ?? null;
	const displayedErrors: ServiceError[] = selectedLog
		? errors.filter((e: ServiceError): boolean => e.job_email_scraping_service_log_id === selectedLog.id)
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

			<div className="d-flex align-items-center gap-3 mb-4 service-filter-row">
				<LastLogBar serviceStatus={serviceStatus} onClick={openLogViewer} />
				<div className="ms-auto">
					<TimeFilterPopover id="history-filters" onDateRangeChange={setDateRange} defaultMode="period" />
				</div>
			</div>

			<LatestRunProgress latestLog={latestServiceLog} isRunning={serviceStatus?.is_running || false} />

			<LogViewer
				id="scraper-log-viewer"
				api={jobScraperServiceApi}
				isServiceRunning={serviceStatus?.is_running || false}
				expanded={logsExpanded}
				onExpandedChange={setLogsExpanded}
			/>

			<RunHistoryChart
				serviceLogData={previousServiceLogs}
				selectedPlatform={selectedPlatform}
				platformOptions={platformOptions}
				onPlatformChange={setSelectedPlatform}
				isRunning={serviceStatus?.is_running || false}
				loading={logsLoading}
				selectedLogId={selectedLog?.id ?? null}
				onSelectLog={setSelectedLogId}
			/>

			<ErrorSummaryCard
				current={{
					errors: displayedErrors,
					setAcknowledged,
					platformByJobId: buildPlatformByJobId(previousServiceLogs),
				}}
				perJob={{
					title: "Scraping Errors",
					discriminatorKey: "scraped_job_id",
					emptyText: "No scrape errors",
					showJobs: true,
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

export default JobScrapingPage;
