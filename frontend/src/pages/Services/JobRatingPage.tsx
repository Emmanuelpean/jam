import React, { JSX, useContext, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { jobRatingServiceRunnerApi } from "../../services/api/Services";
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
import { LatestRunProgress } from "./JobRatingDashboard/LatestRunProgress";
import { RunHistoryChart } from "./JobRatingDashboard/RunHistoryChart";
import { ErrorSummaryCard } from "./JobRatingDashboard/ErrorSummaryCard";
import { useJobRatingServiceLogs } from "../../hooks/useJobRatingServiceLog";
import { useJobRatingErrors } from "../../hooks/useJobRatingErrors";
import { DateRange } from "../../utils/TimeUtils";
import { TimeFilterPopover } from "../../components/TimeSelection/TimeFilterPopover";
import "./Service.scss";

const JobRatingPage = (): JSX.Element => {
	const { token } = useAuth();
	const { serviceStatus, remainingTime, fetchStatus, statusError } =
		useServiceRunnerStatus(jobRatingServiceRunnerApi);

	const [ratingForm, setRatingForm] = useState<{ period_hours: number }>({ period_hours: 0 });
	useEffect((): void => {
		setRatingForm({ period_hours: serviceStatus?.period_hours || 0 });
	}, [serviceStatus?.period_hours]);

	const onChangeField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;
		setRatingForm((prev: any) => ({ ...prev, [name]: value === "" ? "" : Number(value) || 3 }));
	};

	const ratingControl = useServiceControl(
		token,
		fetchStatus,
		(t: string) => jobRatingServiceRunnerApi.start(ratingForm.period_hours, t),
		(t: string) => jobRatingServiceRunnerApi.stop(t)
	);

	const ratingDisabled: boolean = serviceStatus?.service_runner_status !== "stopped";
	const ratingFields: React.ReactNode =
		serviceStatus &&
		RenderLabeledInput(
			"period_hours",
			"Scraping Period",
			"Time between rating runs.",
			ratingForm.period_hours,
			"Hour(s)",
			!ratingDisabled,
			onChangeField,
			ratingDisabled
		);

	const headerSlot: HTMLElement | null = useContext(ModalHeaderSlotContext);
	const statusControl: JSX.Element = (
		<Popover trigger={renderStatusIcons(serviceStatus, remainingTime)} ariaLabel="Job rating service controls">
			{(close) =>
				renderControl(
					serviceStatus,
					ratingFields,
					ratingControl.loading,
					() => {
						close();
						ratingControl.handleStart();
					},
					() => {
						close();
						ratingControl.handleStop();
					}
				)
			}
		</Popover>
	);

	// ---- Dashboard data ----
	// Null until the TimeFilterPopover emits its real default range on mount, so we
	// don't fire a throwaway fetch for a placeholder (today-only) window first.
	const [dateRange, setDateRange] = useState<DateRange | null>(null);
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
		<div className="scraped-jobs-page">
			{headerSlot ? (
				createPortal(statusControl, headerSlot)
			) : (
				<PageHeader
					title="Job Rating"
					icon={getTableIcon("Job Rating Dashboard")}
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
				id="rating-log-viewer"
				api={jobRatingServiceRunnerApi}
				isServiceRunning={serviceStatus?.service_running || false}
				serviceStatus={serviceStatus}
				expanded={logsExpanded}
				onExpandedChange={setLogsExpanded}
			/>

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

export default JobRatingPage;
