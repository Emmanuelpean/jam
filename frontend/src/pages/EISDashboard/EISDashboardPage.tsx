import React, { JSX, useState } from "react";
import { jobScraperServiceApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import "./EisDashboardPage.css";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import LogViewer from "./LogViewer";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ServiceStatusCard } from "./ServiceStatusCard";
import { LatestRunProgress } from "./LatestRunProgress";
import { RunHistoryChart } from "./RunHistoryChart";
import { ErrorSummaryCard } from "./ErrorSummaryCard";
import { useScraperStatus } from "../../hooks/useScraperStatus";
import { useServiceLogs } from "../../hooks/useServiceLogs";
import { useScraperErrors } from "../../hooks/useScraperErrors";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useServiceErrors } from "../../hooks/useServiceErrors";
import { DateRange } from "../../utils/TimeUtils";

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
	const { status, remainingTime, fetchStatus } = useScraperStatus(token);
	const [formData, setFormData] = useState<FormData>({
		period_hours: status?.period_hours || 0,
		timedelta_days: status?.timedelta_days || 0,
	});
	const [loading, setLoading] = useState<boolean>(false);
	const { showToastSuccess } = useGlobalToast();
	const { serviceLogs, latestLog, platformOptions, fetchLatestLog } = useServiceLogs(
		token,
		status?.scraper_running || false,
		dateRange,
	);
	const { scraperErrors } = useScraperErrors(latestLog, token, selectedPlatform);
	const { scraperErrors: latestScraperErrors } = useScraperErrors(serviceLogs, token, selectedPlatform);
	const { serviceErrors } = useServiceErrors(latestLog, token);
	const { serviceErrors: latestServiceErrors } = useServiceErrors(serviceLogs, token);

	React.useEffect(() => {
		if (status) {
			setFormData({
				period_hours: status.period_hours || 3,
				timedelta_days: status.timedelta_days || 1,
			});
		}
	}, [status?.period_hours, status?.timedelta_days]);

    const onChangeFormField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
        const target = event.target as HTMLInputElement;
        const { name, value } = target;

        setFormData((prevData) => ({
            ...prevData,
            [name]: value === '' ? '' : Number(value) || 3,
        }));
    };

	const handleStart = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await jobScraperServiceApi.start(formData.period_hours, formData.timedelta_days, token);
			await fetchStatus();
			await fetchLatestLog();
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
			await fetchLatestLog();
			showToastSuccess("Scraper stopped successfully");
		} catch (err: any) {
			console.log(err.message || "Failed to stop scraper");
		} finally {
			setLoading(false);
		}
	};

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
				status={status}
				remainingTime={remainingTime}
				formData={formData}
				loading={loading}
				onFormChange={onChangeFormField}
				onStart={handleStart}
				onStop={handleStop}
			/>

			<LatestRunProgress latestLog={latestLog} isRunning={status?.scraper_running || false} />

			<LogViewer isServiceRunning={status?.scraper_running || false} />

			<RunHistoryChart
				serviceLogData={serviceLogs}
				selectedPlatform={selectedPlatform}
				platformOptions={platformOptions}
				onPlatformChange={setSelectedPlatform}
				onDateRangeChange={setDateRange}
				isRunning={status?.scraper_running || false}
			/>

			<ErrorSummaryCard
				latestServiceLogs={serviceLogs}
				lastScraperErrors={scraperErrors}
				latestScraperErrors={latestScraperErrors}
				lastServiceErrors={serviceErrors}
				latestServiceErrors={latestServiceErrors}
				isRunning={status?.scraper_running || false}
			/>
		</div>
	);
};

export default JobScraperDashboard;
