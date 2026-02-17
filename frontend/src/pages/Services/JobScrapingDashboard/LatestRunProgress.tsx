import React, { JSX } from "react";
import { JobScrapingServiceLogData } from "../../../services/schemas/Services";
import { formatDuration } from "../../../utils/TimeUtils";
import ProgressBar from "../ProgressBar/ProgressBar";
import { PlatformStatsTable } from "./PlatformStatsTable";

interface LatestRunProgressProps {
	latestLog: JobScrapingServiceLogData | null;
	isRunning: boolean;
}

export const LatestRunProgress = ({ latestLog, isRunning }: LatestRunProgressProps): JSX.Element | null => {
	if (!latestLog) return null;

	return (
		<div className="status-card">
			<h2 className="card-title">
				<i className="bi bi-clock-history me-2"></i>
				Latest Run Progress
				{isRunning && <span className="live-indicator ms-2"></span>}
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
						<span className="status-label">Jobs Found:</span> {latestLog.job_found_n}
					</p>
					<p className="metric-item">
						<span className="status-label">Scraping Succeeded:</span> {latestLog.job_scrape_succeeded_n}
					</p>
					<p className="metric-item">
						<span className="status-label">Scraping Failed:</span> {latestLog.job_scrape_failed_n}
					</p>
					<p className="metric-item"></p>
				</div>

				<div className="metric-group">
					<PlatformStatsTable platformStats={latestLog.platform_stats} latestLog={latestLog} />
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
					current={latestLog.user_processed_ids.length}
					total={latestLog.user_found_ids.length}
				/>
				<ProgressBar
					title="Emails Processed"
					current={latestLog.email_saved_n + latestLog.email_skipped_n}
					total={latestLog.email_found_n}
				/>
				<ProgressBar
					title="Jobs Scraped"
					current={
						latestLog.job_scrape_succeeded_n +
						latestLog.job_scrape_copied_n +
						latestLog.job_scrape_failed_n +
						latestLog.job_scrape_skipped_n
					}
					total={latestLog.job_to_process_n}
				/>
			</div>
		</div>
	);
};
