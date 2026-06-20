import React, { JSX, useContext, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { jobScraperServiceApi } from "../../services/api/Services";
import {
	formatErrorMessage,
	RenderLabeledInput,
	renderControl,
	renderStatusIcons,
	useServiceControl,
} from "./ServiceUtils";
import { Popover } from "../../components/Popover/Popover";
import { useAuth } from "../../contexts/AuthContext";
import { ModalHeaderSlotContext } from "../../contexts/ModalHeaderSlotContext";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import LogViewer, { useLogViewerToggle } from "./LogViewer/LogViewer";
import { LastLogBar } from "./LogViewer/LastLogBar";
import { LatestRunProgress } from "./JobScrapingDashboard/LatestRunProgress";
import { RunHistoryChart } from "./JobScrapingDashboard/RunHistoryChart";
import { ErrorSummaryCard } from "./JobScrapingDashboard/ErrorSummaryCard";
import { useJobScraperServiceLogs } from "../../hooks/useJobScraperServiceLogs";
import { useJobScraperErrors } from "../../hooks/useJobScraperErrors";
import { useServiceErrors } from "../../hooks/useServiceErrors";
import { DateRange } from "../../utils/TimeUtils";
import { TimeFilterPopover } from "../../components/TimeSelection/TimeFilterPopover";
import "./Service.scss";

const JobScrapingPage = (): JSX.Element => {
	const { token } = useAuth();
	const { serviceStatus, remainingTime, fetchStatus, statusError } = useServiceRunnerStatus(jobScraperServiceApi);

	// Scraper config form (initialised once from the service status).
	const [scrapingForm, setScrapingForm] = useState<{ period_hours: number; timedelta_days: number }>({
		period_hours: 0,
		timedelta_days: 0,
	});
	const scrapingFormInitialised = useRef<boolean>(false);
	useEffect(() => {
		if (serviceStatus && !scrapingFormInitialised.current) {
			setScrapingForm({
				period_hours: serviceStatus.period_hours || 0,
				timedelta_days: serviceStatus.service_kwargs?.timedelta_days || 0,
			});
			scrapingFormInitialised.current = true;
		}
	}, [serviceStatus]);

	const onChangeField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;
		setScrapingForm((prev: any) => ({ ...prev, [name]: value === "" ? "" : Number(value) || 3 }));
	};

	const scrapingControl = useServiceControl(
		token,
		fetchStatus,
		(t: string) => jobScraperServiceApi.start(scrapingForm.period_hours, scrapingForm.timedelta_days, t),
		(t: string) => jobScraperServiceApi.stop(t)
	);

	const scrapingDisabled: boolean = serviceStatus?.service_runner_status !== "stopped";
	const scrapingFields: React.ReactNode = serviceStatus && (
		<>
			{RenderLabeledInput(
				"period_hours",
				"Scraping Period",
				"Time between scraping runs.",
				scrapingForm.period_hours,
				"Hour(s)",
				!scrapingDisabled,
				onChangeField,
				scrapingDisabled
			)}
			{RenderLabeledInput(
				"timedelta_days",
				"Time Delta",
				"Number of days back to scrape job postings for each run.",
				scrapingForm.timedelta_days,
				"Day(s)",
				!scrapingDisabled,
				onChangeField,
				scrapingDisabled
			)}
		</>
	);

	const headerSlot: HTMLElement | null = useContext(ModalHeaderSlotContext);
	const statusControl: JSX.Element = (
		<Popover trigger={renderStatusIcons(serviceStatus, remainingTime)} ariaLabel="Job scraping service controls">
			{(close) =>
				renderControl(
					serviceStatus,
					scrapingFields,
					scrapingControl.loading,
					() => {
						close();
						scrapingControl.handleStart();
					},
					() => {
						close();
						scrapingControl.handleStop();
					}
				)
			}
		</Popover>
	);

	// ---- Dashboard data ----
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
			{headerSlot ? (
				createPortal(statusControl, headerSlot)
			) : (
				<PageHeader
					title="Job Scraping"
					icon={getTableIcon("Job Scraping Dashboard")}
					statusContent={statusControl}
				/>
			)}

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
