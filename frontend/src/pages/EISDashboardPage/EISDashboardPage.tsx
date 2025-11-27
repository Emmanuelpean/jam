import React, { JSX, useEffect, useState } from "react";
import { jobScraperApi, LogResponse, ScraperStatus, serviceLogApi } from "../../services/Api";
import { ServiceLog } from "../../services/Schemas";
import { useAuth } from "../../contexts/AuthContext";
import "./EisDashboardPage.css";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { formatDuration } from "../../utils/TimeUtils";
import { getTableIcon } from "../../components/rendering/view/Icons";

const JobScraperDashboard = (): JSX.Element => {
	const { token } = useAuth();
	const [status, setStatus] = useState<ScraperStatus | null>(null);
	const [latestLog, setLatestLog] = useState<ServiceLog | null>(null);
	const [periodHours, setPeriodHours] = useState<number>(3.0);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const [successMessage, setSuccessMessage] = useState<string | null>(null);
	const [logs, setLogs] = useState<LogResponse | null>(null);
	const [logsExpanded, setLogsExpanded] = useState<boolean>(false);
	const [logLines, setLogLines] = useState<number>(100);

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
				console.log(log);
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
			const response = await jobScraperApi.start(periodHours, token);
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

	// Fetch logs
	const fetchLogs = async (): Promise<void> => {
		if (!token) return;
		try {
			const data = await jobScraperApi.getLogs(logLines, token);
			setLogs(data);
		} catch (err: any) {
			console.error("Failed to fetch logs:", err);
		}
	};

	// Handle show more logs
	const handleShowMoreLogs = (): void => {
		setLogLines((prev) => Math.min(prev + 100, logs?.total_lines || prev));
	};

	useEffect(() => {
		if (logsExpanded) {
			fetchLogs().then((_) => {
				const interval = setInterval(fetchLogs, 3000);
				return () => clearInterval(interval);
			});
		}
	}, [logsExpanded, logLines, token]);

	const calculateJobTotal = (log: ServiceLog): number => {
		return log.job_success_n + log.job_fail_n;
	};

	const getStatusIcon = (isRunning: boolean): string => {
		return isRunning ? "bi-check-circle-fill" : "bi-x-circle-fill";
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
			<div className={`status-card ${status?.is_running ? "status-running" : "status-stopped"}`}>
				<h2 className="card-title">Service Status</h2>
				{status ? (
					<div className="status-grid">
						<p className="status-item">
							<span className="status-label">Service Status:</span>
							<span
								className={
									status.is_running ? "status-badge badge-success" : "status-badge badge-danger"
								}
							>
								<i className={`bi ${getStatusIcon(status.is_running)}`}></i>{" "}
								{status.is_running ? "Active" : "Inactive"}
							</span>
						</p>
						<p className="status-item">
							<span className="status-label">Thread Status:</span>
							<span
								className={
									status.thread_alive ? "status-badge badge-success" : "status-badge badge-danger"
								}
							>
								<i className={`bi ${getStatusIcon(status.thread_alive)}`}></i>{" "}
								{status.thread_alive ? "Alive" : "Dead"}
							</span>
						</p>
						{status.thread_name && (
							<p className="status-item">
								<span className="status-label">Thread Name:</span> {status.thread_name}
							</p>
						)}
					</div>
				) : (
					<p className="loading-text">Loading status...</p>
				)}
			</div>
			{/* Email Progress Bar */}
			{latestLog && (
				<>
					<div className="metric-group">
						<p className="metric-item">
							<span className="status-label">Users Processing Progress</span>
						</p>
						<div className="progress-bar-container">
							<div
								className="progress-bar-fill"
								style={{
									width: `${latestLog.users_found_n > 0 ? (latestLog.users_processed_n / latestLog.users_found_n) * 100 : 0}%`,
								}}
							/>
						</div>
						<p className="metric-item progress-text">
							{latestLog?.emails_saved_n ?? 0} / {latestLog?.emails_found_n ?? 0} emails saved
						</p>
					</div>
					<div className="metric-group">
						<p className="metric-item">
							<span className="status-label">Email Processing Progress</span>
						</p>
						<div className="progress-bar-container">
							<div
								className="progress-bar-fill"
								style={{
									width: `${latestLog?.emails_found_n && latestLog.emails_found_n > 0 ? (latestLog.emails_saved_n / latestLog.emails_found_n) * 100 : 0}%`,
								}}
							/>
						</div>
						<p className="metric-item progress-text">
							{latestLog?.emails_saved_n ?? 0} / {latestLog?.emails_found_n ?? 0} emails saved
						</p>
					</div>

					{/* Job Scraping Progress Bar */}
					<div className="metric-group">
						<p className="metric-item">
							<span className="status-label">Job Scraping Progress</span>
						</p>
						<div className="progress-bar-container">
							<div
								className="progress-bar-fill"
								style={{
									width: `${latestLog?.jobs_extracted_n && latestLog.jobs_extracted_n > 0 ? (calculateJobTotal(latestLog) / latestLog.jobs_extracted_n) * 100 : 0}%`,
								}}
							/>
						</div>
						<p className="metric-item progress-text">
							{latestLog ? calculateJobTotal(latestLog) : 0} / {latestLog?.jobs_extracted_n ?? 0} jobs
							scraped
						</p>
					</div>
				</>
			)}

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
								<span className="status-label">Users Processed:</span> {latestLog.users_processed_n}
							</p>
							<p className="metric-item">
								<span className="status-label">Emails Found:</span> {latestLog.emails_found_n}
							</p>
							<p className="metric-item">
								<span className="status-label">Emails Saved:</span> {latestLog.emails_saved_n}
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
				</div>
			)}

			{/* Configuration */}
			<div className="config-section">
				<label htmlFor="period-hours" className="config-label">
					Scraping Period (hours)
				</label>
				<input
					id="period-hours"
					type="number"
					min="0.5"
					step="0.5"
					value={periodHours}
					onChange={(e) => setPeriodHours(parseFloat(e.target.value))}
					disabled={status?.is_running || loading}
					className="config-input"
				/>
				<small className="config-hint">
					Time between scraping runs (can only be changed when service is stopped)
				</small>
			</div>

			{/* Control Buttons */}
			<div className="button-group">
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
			<div className="log-section">
				<button className="log-toggle" onClick={() => setLogsExpanded(!logsExpanded)}>
					{logsExpanded ? "▼" : "▶"} View Log File
					{logs && <span className="log-count"> ({logs.total_lines} total lines)</span>}
				</button>

				{logsExpanded && (
					<div className="log-viewer">
						{logs ? (
							<>
								<div className="log-header">
									<span>
										Showing last {logs.lines.length} of {logs.total_lines} lines
									</span>
									{logs.lines.length < logs.total_lines && (
										<button className="log-load-more" onClick={handleShowMoreLogs}>
											Load 100 More
										</button>
									)}
								</div>
								<pre className="log-content">
									{logs.lines.map((line, idx) => (
										<div key={idx} className="log-line">
											{line}
										</div>
									))}
								</pre>
							</>
						) : (
							<p className="loading-text">Loading logs...</p>
						)}
					</div>
				)}
			</div>
		</div>
	);
};

export default JobScraperDashboard;
