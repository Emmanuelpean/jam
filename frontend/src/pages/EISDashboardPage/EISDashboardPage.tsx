import React, { JSX, useEffect, useState } from "react";
import { jobScraperApi, ScraperStatus, serviceLogApi } from "../../services/Api";
import { ServiceLog } from "../../services/Schemas";
import { useAuth } from "../../contexts/AuthContext";
import "./EisDashboardPage.css";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { formatDuration } from "../../utils/TimeUtils";
import { getTableIcon } from "../../components/rendering/view/Icons";
import ProgressBar from "./ProgressBar";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { Errors, FormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import LogViewer from "./LogViewer";

export interface FormData {
	period: number;
	timedelta_days: number;
}

const JobScraperDashboard = (): JSX.Element => {
	const { token } = useAuth();
	const [status, setStatus] = useState<ScraperStatus | null>(null);
	const [latestLog, setLatestLog] = useState<ServiceLog | null>(null);
	const [fieldErrors, setFieldErrors] = useState<Errors>({});
	const [formData, setFormData] = useState<FormData>({
		period: 0,
		timedelta_days: 0,
	});
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const [successMessage, setSuccessMessage] = useState<string | null>(null);

	// Fetch the scraper service status
	const fetchStatus = async (): Promise<void> => {
		if (!token) return;
		try {
			const data: ScraperStatus = await jobScraperApi.getStatus(token);
			setStatus(data);
			setError(null);
		} catch (err: any) {
			setError(err.message || "Failed to fetch scraper status");
			console.error(err);
		}
	};

	// Fetch the scraper service status every 5 seconds
	useEffect(() => {
		fetchStatus().then((_: void) => {
			const interval = setInterval(fetchStatus, 5000);
			return (): void => clearInterval(interval);
		});
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

	// Fetch latest service log ever 2/10 s
	useEffect(() => {
		fetchLatestLog().then((_: void) => {
			const pollInterval: 2000 | 10000 = status?.is_running ? 2000 : 10000;
			const interval = setInterval(fetchLatestLog, pollInterval);
			return (): void => clearInterval(interval);
		});
	}, [status?.is_running, token]);

	// Handle start button click
	const handleStart = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		setError(null);
		setSuccessMessage(null);
		try {
			const response = await jobScraperApi.start(formData.period, formData.timedelta_days, token);
			setSuccessMessage(response.detail);
			await fetchStatus();
			await fetchLatestLog();
		} catch (err: any) {
			setError(err.message || "Failed to start scraper");
		} finally {
			setLoading(false);
		}
	};

	// Handle stop button click
	const handleStop = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		setError(null);
		setSuccessMessage(null);
		try {
			const response = await jobScraperApi.stop(token);
			setSuccessMessage(response.detail);
			await fetchStatus();
			await fetchLatestLog();
		} catch (err: any) {
			setError(err.message || "Failed to stop scraper");
		} finally {
			setLoading(false);
		}
	};

	const calculateJobTotal = (log: ServiceLog): number => {
		return log.job_success_n + log.job_fail_n;
	};

	const getStatusIcon = (isRunning: boolean): string => {
		return isRunning ? "bi-check-circle-fill" : "bi-x-circle-fill";
	};

	function createStatusItem(label: string, isAlive: boolean): JSX.Element {
		return (
			<p className="status-item">
				<span className="status-label">{label}:</span>
				<span className={isAlive ? "status-badge badge-success" : "status-badge badge-danger"}>
					<i className={`bi ${getStatusIcon(isAlive)}`}></i> {isAlive ? "Alive" : "Dead"}
				</span>
			</p>
		);
	}

	// Define field configurations
	const periodField: ModalFormField = {
		name: "period",
		type: "text",
		label: "Scraping Period (hours)",
		helpText: "Time between scraping runs (can only be changed when service is stopped)",
	};

	const timedeltaField: ModalFormField = {
		name: "timedelta",
		type: "text",
		label: "Time Delta (days)",
		helpText: "Number of days back to scrape job postings for each run",
	};

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData(
			(prev: FormData): FormData => ({
				...prev,
				[name]: value,
			}),
		);

		if (fieldErrors[name as keyof Errors]) {
			setFieldErrors((prev: Errors) => ({
				...prev,
				[name]: "",
			}));
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
						<h4 className="mb-0 fw-bold text-dark">{"TOAST Dashboard"}</h4>
					</div>
				</div>
			</div>

			{/* Status Display */}
			<div className="status-card">
				<h2 className="card-title">Service Status</h2>
				{status ? (
					<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
						<div>
							{createStatusItem("Service Status", status.is_running)}
							{createStatusItem("Thread Status", status.thread_alive)}
						</div>
						<div>
							{FormField(periodField, formData, handleInputChange, fieldErrors)}
							{FormField(timedeltaField, formData, handleInputChange, fieldErrors)}
						</div>
						<div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
							<ActionButton
								id="confirm-start-button"
								disabled={loading || status?.is_running}
								loading={loading}
								loadingText="Starting Service..."
								defaultText="Start Service"
								fullWidth={true}
								onClick={handleStart}
							/>
							<ActionButton
								id="confirm-stop-button"
								variant="secondary"
								disabled={loading || !status?.is_running}
								loading={loading}
								loadingText="Stopping Service..."
								defaultText="Stop Service"
								fullWidth={true}
								onClick={handleStop}
							/>
						</div>
					</div>
				) : (
					<p className="loading-text">Loading status...</p>
				)}
			</div>

			{/* Progress Display */}
			{latestLog && (
				<div className="progress-card">
					<div className="progress-header">
						<h2 className="card-title">Latest Run Progress</h2>
						{status?.is_running && <span className="live-indicator" title="Live updates"></span>}
					</div>

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
								<span className="status-label">Jobs Scraped:</span> {calculateJobTotal(latestLog)}
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
							current={latestLog.emails_saved_n}
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

			{/* Messages */}
			{error && (
				<div className="alert alert-error">
					<span className="alert-icon">⚠️</span>
					{error}
				</div>
			)}
			{successMessage && (
				<div className="alert alert-success">
					<span className="alert-icon">✓</span>
					{successMessage}
				</div>
			)}
			<LogViewer isServiceRunning={status?.is_running ?? false} />
		</div>
	);
};

export default JobScraperDashboard;
