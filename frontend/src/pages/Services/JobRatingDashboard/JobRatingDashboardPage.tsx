import React, { JSX, useState, useEffect } from "react";
import { jobRatingServiceRunnerApi } from "../../../services/api/Services";
import { useAuth } from "../../../contexts/AuthContext";
import { SyntheticEvent } from "../../../components/rendering/widgets/WidgetRenders";
import LogViewer from "../LogViewer/LogViewer";
import { useGlobalToast } from "../../../hooks/useNotificationToast";
import { ServiceStatusCard } from "./ServiceStatusCard";
import { LatestRunProgress } from "./LatestRunProgress";
import { RunHistoryChart } from "./RunHistoryChart";
import { ErrorSummaryCard } from "./ErrorSummaryCard";
import { useServiceRunnerStatus } from "../../../hooks/useServiceRunnerStatus";
import { getTableIcon } from "../../../components/rendering/view/Icons";
import { DateRange } from "../../../utils/TimeUtils";
import { useJobRatingServiceLogs } from "../../../hooks/useJobRatingServiceLog";
import { useJobRatingErrors } from "../../../hooks/useJobRatingErrors";
import "../Service.css";
import PageHeader from "../../PageHeader/PageHeader";

export interface FormData {
	period_hours: number;
}

const JobRatingDashboard = (): JSX.Element => {
	const { token } = useAuth();
	const [dateRange, setDateRange] = useState<DateRange>({
		start: new Date(),
		end: new Date(),
	});
	const { serviceStatus, remainingTime, fetchStatus, statusError } =
		useServiceRunnerStatus(jobRatingServiceRunnerApi);
	const [formData, setFormData] = useState<FormData>({
		period_hours: serviceStatus?.period_hours || 0,
	});
	const [loading, setLoading] = useState<boolean>(false);
	const { showToastSuccess } = useGlobalToast();
	const { previousServiceLogs, latestServiceLog, fetchLatestServiceLog, serviceLogError } = useJobRatingServiceLogs(
		serviceStatus?.service_running || false,
		dateRange,
	);
	const { scraperErrors: previousRatingErrors, error: previousRatingRequestError } =
		useJobRatingErrors(previousServiceLogs);
	const { scraperErrors: lastRatingErrors, error: latestRatingRequestError } = useJobRatingErrors(latestServiceLog);

	useEffect((): void => {
		if (serviceStatus && serviceStatus?.service_runner_status === "stopped") {
			setFormData({
				period_hours: serviceStatus.period_hours || 3,
			});
		}
	}, [serviceStatus]);

	const onChangeFormField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;

		setFormData((prevData) => ({
			...prevData,
			[name]: value === "" ? "" : Number(value) || 3,
		}));
	};

	const handleStart = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await jobRatingServiceRunnerApi.start(formData.period_hours, token);
			await fetchStatus();
			await fetchLatestServiceLog();
			showToastSuccess("Service runner started successfully");
		} catch (err: any) {
			console.log(err.message || "Failed to start service runner");
		} finally {
			setLoading(false);
		}
	};

	const handleStop = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await jobRatingServiceRunnerApi.stop(token);
			await fetchStatus();
			await fetchLatestServiceLog();
			showToastSuccess("Service runner stopped successfully");
		} catch (err: any) {
			console.log(err.message || "Failed to stop service runner");
		} finally {
			setLoading(false);
		}
	};

	const formatErrorMessage = (err: unknown): string => {
		if (!err) return "";
		if (typeof err === "string") return err;
		if (err instanceof Error) return err.message;
		try {
			return JSON.stringify(err);
		} catch {
			return String(err);
		}
	};

	const collectedErrors = [
		{ key: "status", label: "Service status", value: statusError },
		{ key: "serviceLogs", label: "Service logs", value: serviceLogError },
		{ key: "lastRatingError", label: "Last rating error", value: latestRatingRequestError },
		{ key: "latestRatingError", label: "Latest rating error", value: previousRatingRequestError },
	].filter((e) => e.value);

	return (
		<div>
			<PageHeader title={"Job Rating Dashboard"} icon={getTableIcon("Job Rating Dashboard")} />
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

			<ServiceStatusCard
				status={serviceStatus}
				remainingTime={remainingTime}
				formData={formData}
				loading={loading}
				onFormChange={onChangeFormField}
				onStart={handleStart}
				onStop={handleStop}
			/>

			<LatestRunProgress latestLog={latestServiceLog} isRunning={serviceStatus?.service_running || false} />

			<LogViewer api={jobRatingServiceRunnerApi} isServiceRunning={serviceStatus?.service_running || false} />

			<RunHistoryChart
				serviceLogData={previousServiceLogs}
				onDateRangeChange={setDateRange}
				isRunning={serviceStatus?.service_running || false}
			/>

			<ErrorSummaryCard
				latestServiceLogs={previousServiceLogs}
				lastRatingErrors={lastRatingErrors}
				latestRatingErrors={previousRatingErrors}
				isRunning={serviceStatus?.service_running || false}
			/>
		</div>
	);
};

export default JobRatingDashboard;
