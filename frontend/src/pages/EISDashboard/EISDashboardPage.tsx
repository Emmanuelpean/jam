import { Form, InputGroup } from "react-bootstrap";
import React, { JSX, useEffect, useState } from "react";
import { jobScraperApi, ScraperStatus, serviceLogApi, ThreadStatus } from "../../services/Api";
import { ServiceLog } from "../../services/Schemas";
import { useAuth } from "../../contexts/AuthContext";
import "./EisDashboardPage.css";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { formatDuration } from "../../utils/TimeUtils";
import { getTableIcon } from "../../components/rendering/view/Icons";
import ProgressBar from "./ProgressBar";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import LogViewer from "./LogViewer";
import { HelpBubble } from "../../components/rendering/widgets/HelpBubble";
import Spinner from "../../components/spinner/Spinner";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { LineChart, SeriesData } from "../../components/charts/LineChart";

export interface FormData {
	period_hours: number;
	timedelta_days: number;
}

const JobScraperDashboard = (): JSX.Element => {
	const { token } = useAuth();
	const { showToastSuccess } = useGlobalToast();
	const [remainingTime, setRemainingTime] = useState<number | null>(null);
	const [status, setStatus] = useState<ScraperStatus | null>(null);
	const [latestLog, setLatestLog] = useState<ServiceLog | null>(null);
	const [logData, setLogData] = useState<SeriesData[][] | null>(null);
	const [formData, setFormData] = useState<FormData>({
		period_hours: 0,
		timedelta_days: 0,
	});
	const [loading, setLoading] = useState<boolean>(false);

	// Fet the 10 latest logs
	useEffect(() => {
		const fetchLatestLogs = async (): Promise<void> => {
			if (!token) return;
			try {
				const logs: ServiceLog[] = await serviceLogApi.getAll(token, { limit: 10 });
				// Prepare data for chart
				const successSeries: SeriesData = {
					id: "Successful Jobs",
					color: "#22c55e",
					data: logs
						.slice()
						.reverse()
						.map((log) => ({
							x: new Date(log.run_datetime),
							y: log.job_success_n,
						})),
				};

				const failSeries: SeriesData = {
					id: "Failed Jobs",
					color: "#ef4444",
					data: logs
						.slice()
						.reverse()
						.map((log) => ({
							x: new Date(log.run_datetime),
							y: log.job_fail_n,
						})),
				};

				const runDurationSeries: SeriesData = {
					id: "Run Duration (s)",
					color: "#3b82f6",
					data: logs
						.slice()
						.reverse()
						.map((log) => ({
							x: new Date(log.run_datetime),
							y: log.run_duration ? log.run_duration / 3600 : 0,
						})),
				};

				setLogData([[successSeries, failSeries], [runDurationSeries]]);
			} catch (err: any) {
				console.error("Failed to fetch latest logs:", err);
			}
		};
		fetchLatestLogs().then();
	}, [token]);

	// Fetch the scraper service status
	const fetchStatus = async (): Promise<void> => {
		if (!token) return;
		try {
			const data: ScraperStatus = await jobScraperApi.getStatus(token);
			setStatus(data);
			setFormData({
				period_hours: data.period_hours || 3,
				timedelta_days: data.timedelta_days || 1,
			});
		} catch (err: any) {
			console.error(err);
		}
	};

	// Calculate and update remaining time every second
	useEffect(() => {
		if (!status?.sleep_until) {
			setRemainingTime(null);
			return;
		}

		const updateTimer = () => {
			if (!status.sleep_until) return;
			const remaining = new Date(status.sleep_until).getTime() - Date.now() / 1000;
			setRemainingTime(remaining > 0 ? Math.round(remaining) : 0);
		};

		updateTimer();
		const interval = setInterval(updateTimer, 1000);
		return () => clearInterval(interval);
	}, [status?.sleep_until]);

	// Fetch the scraper service status every 5 seconds
	useEffect(() => {
		fetchStatus().then();
		const interval = setInterval(fetchStatus, 5000);
		return (): void => clearInterval(interval);
	}, [token]);

	// Fetch the latest service log
	const fetchLatestLog = async (): Promise<void> => {
		if (!token) return;
		try {
			// Fetch all logs and get the most recent one
			const log: ServiceLog = await serviceLogApi.getLatest(token);
			if (log) {
				setLatestLog(log);
			}
		} catch (err: any) {
			console.error("Failed to fetch latest log:", err);
		}
	};

	// Fetch latest service log ever 2s
	useEffect(() => {
		if (!status?.scraper_running) return;
		fetchLatestLog().then();
		const interval = setInterval(fetchLatestLog, 2000);
		return (): void => clearInterval(interval);
	}, [status?.scraper_running, token]);

	// Fetch the latest service log on component mount
	useEffect(() => {
		fetchLatestLog().then();
	}, [token]);

	// Handle start button click
	const handleStart = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await jobScraperApi.start(formData.period_hours, formData.timedelta_days, token);
			await fetchStatus();
			await fetchLatestLog();
			showToastSuccess("Scraper started successfully");
		} catch (err: any) {
			console.log(err.message || "Failed to start scraper");
		} finally {
			setLoading(false);
		}
	};

	// Handle stop button click
	const handleStop = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await jobScraperApi.stop(token);
			await fetchStatus();
			await fetchLatestLog();
			showToastSuccess("Scraper stopped successfully");
		} catch (err: any) {
			console.log(err.message || "Failed to stop scraper");
		} finally {
			setLoading(false);
		}
	};

	const threadStatusIcons: Record<ThreadStatus, string> = {
		started: "bi-check-circle-fill",
		stopped: "bi-x-circle-fill",
		starting: "bi-play-circle-fill",
		stopping: "bi-dash-circle-fill",
	};

	const getScraperStatus = (isRunning: boolean): string => {
		return isRunning ? "bi-check-circle-fill" : "bi-x-circle-fill";
	};

	const threadStatusLabels: Record<string, string> = {
		started: "Active",
		starting: "Starting",
		stopping: "Stopping",
		stopped: "Inactive",
	};

	const threadButtonLabels: Record<string, string> = {
		started: "Stop Service",
		stopping: "Service Stopping",
		starting: "Service Starting",
		stopped: "Start Service",
	};

	const getScraperStatusMessage = (status: ScraperStatus): string => {
		if (status.thread_status === "stopped") {
			return "Stopped";
		}
		if (status.scraper_running) {
			return "Running";
		}
		return `Stopped (${formatDuration(remainingTime)} s before next run)`;
	};

	const onChangeFormField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;
		setFormData((prevData) => ({
			...prevData,
			[name]: Number(value),
		}));
	};

	const RenderLabeledInput = (
		id: string,
		label: string,
		help: string,
		value: number,
		unitText: string = "",
		isRequired: boolean = false,
		onChange?: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void,
	) => {
		return (
			<Form.Group id={id}>
				<InputGroup>
					<InputGroup.Text className="d-flex align-items-center">
						<span>{label}</span>
						{isRequired && <span className="text-danger">*</span>}
						{help && <HelpBubble helpText={help} />}
					</InputGroup.Text>

					<Form.Control type="text" value={value} onChange={onChange} />

					{unitText && <InputGroup.Text>{unitText}</InputGroup.Text>}
				</InputGroup>
			</Form.Group>
		);
	};

	return (
		<div>
			<div className="table-header-section mb-4">
				<div className="d-flex align-items-center justify-content-between p-4 border-0 bg-white shadow-sm rounded-3">
					<div className="d-flex align-items-center">
						<div className="header-icon-wrapper me-3">
							<i className={getTableIcon("TOAST Dashboard")}></i>
						</div>
						<h4 className="mb-0 fw-bold text-dark">{"TOAST Dashboard"}</h4>
					</div>
				</div>
			</div>

			{/* Status Display */}
			<div className="status-card">
				<h2 className="card-title">
					<i className="bi bi-activity me-2"></i>
					Service Status
				</h2>
				{status ? (
					<div className="status-content">
						<div className="status-indicators">
							<div className="indicator-item">
								<span className="indicator-label">Scraper Service</span>
								<span
									className={`status-badge ${status.scraper_running ? "badge-success" : "badge-danger"}`}
								>
									<i className={`bi ${getScraperStatus(status.scraper_running)} me-2`}></i>
									{getScraperStatusMessage(status)}
								</span>
							</div>
							<div className="indicator-item">
								<span className="indicator-label">Service</span>
								<span
									className={`status-badge ${["started", "starting"].includes(status.thread_status) ? "badge-success" : "badge-danger"}`}
								>
									<i className={`bi ${threadStatusIcons[status.thread_status]} me-2`}></i>
									{threadStatusLabels[status.thread_status]}
								</span>
							</div>
						</div>

						<div>
							<div className="config-fields">
								{RenderLabeledInput(
									"period_hours",
									"Scraping Period",
									"Time between scraping runs.",
									formData.period_hours,
									"Hour(s)",
									status.thread_status === "stopped",
									onChangeFormField,
								)}
								{RenderLabeledInput(
									"timedelta_days",
									"Time Delta",
									"Number of days back to scrape job postings for each run.",
									formData.timedelta_days,
									"Day(s)",
									status.thread_status === "stopped",
									onChangeFormField,
								)}
							</div>
						</div>

						<div className="actions-section">
							<ActionButton
								id="confirm-start-button"
								disabled={loading || ["stopping", "starting"].includes(status?.thread_status)}
								loading={loading}
								loadingText={
									status?.thread_status === "stopping" ? "Stopping Service..." : "Starting Service..."
								}
								defaultText={threadButtonLabels[status.thread_status]}
								fullWidth={true}
								onClick={status?.thread_status === "started" ? handleStop : handleStart}
							/>
						</div>
					</div>
				) : (
					<Spinner text={"Loading status..."} />
				)}
			</div>

			{/* Progress Display */}
			{latestLog && (
				<div className="status-card">
					<h2 className="card-title">
						<i className="bi bi-clock-history me-2"></i>
						Latest Run Progress
						{status?.scraper_running && <span className="live-indicator ms-2"></span>}
					</h2>
					<div className="metrics-grid">
						<div className="metric-group">
							<p className="metric-item">
								<span className="status-label">Run Time:</span>
								<br />
								{new Date(latestLog.run_datetime).toLocaleString()}
							</p>
							<p className="metric-item">
								<span className="status-label">Duration:</span> {formatDuration(latestLog.run_duration)}
							</p>
						</div>

						<div className="metric-group">
							<p className="metric-item">
								<span className="status-label">Jobs Extracted:</span> {latestLog.jobs_extracted_n}
							</p>
							<p className="metric-item">
								<span className="status-label">Jobs Scraped:</span> {latestLog.job_total_n}
							</p>
							<p className="metric-item">
								<span className="status-label">Success:</span> {latestLog.job_success_n}
								<span className="metric-divider">|</span>
								<span className="status-label">Failed:</span> {latestLog.job_fail_n}
							</p>
						</div>

						<div className="metric-group">
							<p className="metric-item">
								<span className="status-label">LinkedIn:</span> {latestLog.linkedin_job_n}
							</p>
							<p className="metric-item">
								<span className="status-label">Indeed:</span> {latestLog.indeed_job_n}
							</p>
							<p className="metric-item">
								<span className="status-label">VeganJobs:</span> {latestLog.veganjobs_job_n}
							</p>
						</div>
					</div>

					{latestLog.error_message && (
						<div className="error-message">
							<strong>Error:</strong> {latestLog.error_message}
						</div>
					)}
					<div style={{ display: "flex", width: "100%", gap: "20px", marginBottom: "20px" }}>
						<ProgressBar
							title="Users Processed"
							current={latestLog.users_processed_n}
							total={latestLog.users_found_n}
							width="100%"
						/>
						<ProgressBar
							title="Emails Processed"
							current={latestLog.emails_saved_n + latestLog.emails_skipped_n}
							total={latestLog.emails_found_n}
							width="100%"
						/>
						<ProgressBar
							title="Jobs Scraped"
							current={latestLog.job_success_n + latestLog.job_fail_n}
							total={latestLog.job_total_n}
							width="100%"
						/>
					</div>
				</div>
			)}

			<LogViewer isServiceRunning={status?.scraper_running || false} />

			<div className="status-card mt-4">
				<h2 className="card-title">
					<i className="bi bi-clock-history me-2"></i>
					Latest Run Progress
					{status?.scraper_running && <span className="live-indicator ms-2"></span>}
				</h2>
				<div style={{ display: "flex" }}>
					{logData && logData[0] && (
						<LineChart
							data={logData[0]}
							xAxisLabel="Run date"
							yAxisLabel="Number of scraped jobs"
						></LineChart>
					)}
					{logData && logData[1] && (
						<LineChart data={logData[1]} xAxisLabel="Run date" yAxisLabel="Run duration [h]"></LineChart>
					)}
				</div>
			</div>
		</div>
	);
};

export default JobScraperDashboard;
