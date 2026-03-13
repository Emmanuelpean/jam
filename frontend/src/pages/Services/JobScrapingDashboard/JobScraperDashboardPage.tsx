import React, { JSX, useEffect, useRef, useState } from "react";
import { jobScraperServiceApi } from "../../../services/api/Services";
import { useAuth } from "../../../contexts/AuthContext";
import { SyntheticEvent } from "../../../components/rendering/widgets/WidgetRenders";
import LogViewer from "../LogViewer/LogViewer";
import { useGlobalToast } from "../../../hooks/useNotificationToast";
import { ServiceStatusCard } from "./ServiceStatusCard";
import { LatestRunProgress } from "./LatestRunProgress";
import { RunHistoryChart } from "./RunHistoryChart";
import { ErrorSummaryCard } from "./ErrorSummaryCard";
import { useServiceRunnerStatus } from "../../../hooks/useServiceRunnerStatus";
import { useJobScraperServiceLogs } from "../../../hooks/useJobScraperServiceLogs";
import { useJobScraperErrors } from "../../../hooks/useJobScraperErrors";
import { getTableIcon } from "../../../components/rendering/view/Icons";
import { useServiceErrors } from "../../../hooks/useServiceErrors";
import { DateRange } from "../../../utils/TimeUtils";
import TimeSelection from "../../../components/TimeSelection/TimeSelection";
import "../Service.scss";
import PageHeader from "../../PageHeader/PageHeader";

export interface FormData {
	period_hours: number;
	timedelta_days: number;
}

const JobScraperDashboard = (): JSX.Element => {
	const { token } = useAuth();
	const [dateRange, setDateRange] = useState<DateRange>({
		start: new Date(),
		end: new Date(),
	});
	const [selectedPlatform, setSelectedPlatform] = useState("all");
	const { serviceStatus, remainingTime, fetchStatus, statusError } = useServiceRunnerStatus(jobScraperServiceApi);
	const [formData, setFormData] = useState<FormData>({
		period_hours: 0,
		timedelta_days: 0,
	});
	const hasInitializedForm = useRef(false);
	const [loading, setLoading] = useState<boolean>(false);

	useEffect(() => {
		if (serviceStatus && !hasInitializedForm.current) {
			setFormData({
				period_hours: serviceStatus.period_hours || 0,
				timedelta_days: serviceStatus.service_kwargs?.timedelta_days || 0,
			});
			hasInitializedForm.current = true;
		}
	}, [serviceStatus]);

	const { showToastSuccess } = useGlobalToast();
	const {
		previousServiceLogs,
		latestServiceLog,
		platformOptions,
		fetchLatestServiceLog,
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

	const onChangeFormField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;

		setFormData((prevData: FormData) => ({
			...prevData,
			[name]: value === "" ? "" : Number(value) || 3,
		}));
	};

	const handleStart = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await jobScraperServiceApi.start(formData.period_hours, formData.timedelta_days, token);
			await fetchStatus();
			await fetchLatestServiceLog();
			showToastSuccess("Scraper started successfully");
		} catch (err: any) {
			console.log(err.message || "Failed to start scraper");
		} finally {
			setLoading(false);
		}
	};

	const handleStop = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await jobScraperServiceApi.stop(token);
			await fetchStatus();
			await fetchLatestServiceLog();
			showToastSuccess("Scraper stopped successfully");
		} catch (err: any) {
			console.log(err.message || "Failed to stop scraper");
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
		{
			key: "lastestScraperRequestError",
			label: "Last rating error",
			value: lastestScraperRequestError,
		},
		{
			key: "previousScraperRequestError",
			label: "Latest rating error",
			value: previousScraperRequestError,
		},
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

			<LogViewer
				api={jobScraperServiceApi}
				isServiceRunning={serviceStatus?.service_running || false}
				serviceStatus={serviceStatus}
			/>

			<div className="status-card mt-4">
				<h2 className="card-title">
					<i className="bi bi-funnel me-2"></i>
					History Filters
				</h2>
				<TimeSelection onDateRangeChange={setDateRange} defaultMode="period" />
			</div>

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

export default JobScraperDashboard;
