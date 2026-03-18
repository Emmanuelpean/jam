import React, { JSX } from "react";
import { JobRatingServiceLogData } from "../../../services/schemas/Services";
import { formatDuration } from "../../../utils/TimeUtils";
import ProgressBar from "../ProgressBar/ProgressBar";

interface LatestRunProgressProps {
	latestLog: JobRatingServiceLogData | null;
	isRunning: boolean;
}

export const LatestRunProgress = ({ latestLog, isRunning }: LatestRunProgressProps): JSX.Element | null => {
	if (!latestLog) return null;

	return (
		<div id="latest-run-progress" className="status-card">
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
						<span className="status-label">Jobs Found:</span> {latestLog.job_found_ids.length}
					</p>
					<p className="metric-item">
						<span className="status-label">Rating Succeeded:</span> {latestLog.job_succeeded_ids.length}
					</p>
					<p className="metric-item">
						<span className="status-label">Rating Failed:</span> {latestLog.job_failed_ids.length}
					</p>
					<p className="metric-item">
						<span className="status-label">Rating Skipped:</span> {latestLog.job_skipped_ids.length}
					</p>
				</div>
			</div>

			{latestLog.error_message && (
				<div className="error-message">
					<strong>Error:</strong> {latestLog.error_message}
				</div>
			)}
			<div style={{ display: "flex", width: "100%", gap: "18px", marginBottom: "18px" }}>
				<ProgressBar
					title="Users Processed"
					current={latestLog.user_processed_ids.length}
					total={latestLog.user_found_ids.length}
				/>
				<ProgressBar
					title="Jobs Processed"
					current={
						latestLog.job_succeeded_ids.length +
						latestLog.job_failed_ids.length +
						latestLog.job_skipped_ids.length
					}
					total={latestLog.job_found_ids.length}
				/>
			</div>
		</div>
	);
};
