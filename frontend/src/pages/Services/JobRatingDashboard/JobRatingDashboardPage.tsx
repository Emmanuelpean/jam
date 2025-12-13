import React, { JSX, useState } from "react";
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

export interface FormData {
	period_hours: number;
}

const JobRatingDashboard = (): JSX.Element => {
	const { token } = useAuth();
	const [dateRange, setDateRange] = useState<DateRange>({
		start: new Date(),
		end: new Date(),
	});
	const {
		serviceStatus,
		remainingTime,
		fetchStatus,
		error: statusError,
	} = useServiceRunnerStatus(jobRatingServiceRunnerApi, token);
	const [formData, setFormData] = useState<FormData>({
		period_hours: serviceStatus?.period_hours || 0,
	});
	const [loading, setLoading] = useState<boolean>(false);
	const { showToastSuccess } = useGlobalToast();
	const {
		serviceLogs,
		latestLog,
		fetchLatestLog,
		error: serviceLogError,
	} = useJobRatingServiceLogs(token, serviceStatus?.service_running || false, dateRange);
	const { scraperErrors: lastRatingErrors, error: lastRatingError } = useJobRatingErrors(latestLog, token);
	const { scraperErrors: latestRatingErrors, error: latestRatingError } = useJobRatingErrors(serviceLogs, token);

	React.useEffect(() => {
		if (serviceStatus) {
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
			await fetchLatestLog();
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
			await fetchLatestLog();
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
		{ key: "lastRatingError", label: "Last rating error", value: lastRatingError },
		{ key: "latestRatingError", label: "Latest rating error", value: latestRatingError },
	].filter((e) => e.value);

	return (
		<div>
			<div className="table-header-section mb-4">
				<div className="d-flex align-items-center justify-content-between p-4 border-0 bg-white shadow-sm rounded-3">
					<div className="d-flex align-items-center">
						<div className="header-icon-wrapper me-3">
							<i className={getTableIcon("TOAST Dashboard")}></i>
						</div>
						<h4 className="mb-0 fw-bold text-dark">TOAST Dashboard</h4>
					</div>
				</div>
			</div>

			<ServiceStatusCard
				status={serviceStatus}
				remainingTime={remainingTime}
				formData={formData}
				loading={loading}
				onFormChange={onChangeFormField}
				onStart={handleStart}
				onStop={handleStop}
			/>

			<LatestRunProgress latestLog={latestLog} isRunning={serviceStatus?.service_running || false} />

			<LogViewer api={jobRatingServiceRunnerApi} isServiceRunning={serviceStatus?.service_running || false} />

			<RunHistoryChart
				serviceLogData={serviceLogs}
				onDateRangeChange={setDateRange}
				isRunning={serviceStatus?.service_running || false}
			/>

			<ErrorSummaryCard
				latestServiceLogs={serviceLogs}
				lastRatingErrors={lastRatingErrors}
				latestRatingErrors={latestRatingErrors}
				isRunning={serviceStatus?.service_running || false}
			/>
		</div>
	);
};

export default JobRatingDashboard;
