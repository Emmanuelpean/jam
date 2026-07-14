import React, { JSX } from "react";
import { schedulerApi } from "../../services/api/Services";
import { useSchedulerStatus } from "../../hooks/useSchedulerStatus";
import LogViewer, { useLogViewerToggle } from "./LogViewer/LogViewer";
import { formatErrorMessage } from "./ServiceUtils";
import "./Service.scss";

const SchedulerPage = (): JSX.Element => {
	const { schedulerStatus, statusError } = useSchedulerStatus();
	const { expanded, setExpanded } = useLogViewerToggle("scheduler-log-viewer", true);
	const running: boolean = !!schedulerStatus?.running;

	return (
		<div className="scraped-jobs-page">
			{statusError && (
				<div className="alert alert-danger mb-4 shadow-sm rounded-3" role="alert">
					<i className="bi bi-exclamation-triangle-fill me-2" />
					{formatErrorMessage(statusError)}
				</div>
			)}

			<div className="status-card mb-4">
				<div className="d-flex justify-content-between admin-card-stat">
					<span className="text-muted">Scheduler</span>
					<span className="admin-card-status-value">
						<i className={`bi bi-activity service-status-icon ${running ? "is-on is-running" : "is-off"}`} />
						{schedulerStatus ? (running ? "Running" : "Stopped") : "…"}
					</span>
				</div>
				<div className="d-flex justify-content-between admin-card-stat">
					<span className="text-muted">Poll interval</span>
					<span className="fw-bold">
						{schedulerStatus ? `${schedulerStatus.poll_interval_seconds}s` : "…"}
					</span>
				</div>
			</div>

			<LogViewer
				id="scheduler-log-viewer"
				api={schedulerApi}
				isServiceRunning={running}
				expanded={expanded}
				onExpandedChange={setExpanded}
			/>
		</div>
	);
};

export default SchedulerPage;
