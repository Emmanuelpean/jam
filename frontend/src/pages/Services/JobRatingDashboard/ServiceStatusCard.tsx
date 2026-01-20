import React, { JSX } from "react";
import { ActionButton } from "../../../components/rendering/form/ActionButton";
import Spinner from "../../../components/spinner/Spinner";
import { FormData } from "./JobRatingDashboardPage";
import {
	getServiceStatus,
	getServiceStatusMessage,
	RenderLabeledInput,
	serviceRunnerButtonLabels,
	serviceRunnerStatusIcons,
	serviceRunnerStatusLabels,
	ServiceStatusCardProps,
} from "../ServiceUtils";

interface JobRatingServiceStatusCardProps extends ServiceStatusCardProps {
	formData: FormData;
}

export const ServiceStatusCard = ({
	status,
	remainingTime,
	formData,
	loading,
	onFormChange,
	onStart,
	onStop,
}: JobRatingServiceStatusCardProps): JSX.Element => {
	return (
		<div className="status-card">
			<h2 className="card-title">
				<i className="bi bi-activity me-2"></i>
				Service Status
			</h2>
			{status ? (
				<div className="status-content">
					<div className="status-indicators">
						<div className="indicator-item">
							<span className="indicator-label">Service Runner</span>
							<span
								className={`status-badge ${["started", "starting"].includes(status.service_runner_status) ? "badge-success" : "badge-danger"}`}
							>
								<i className={`bi ${serviceRunnerStatusIcons[status.service_runner_status]} me-2`}></i>
								{serviceRunnerStatusLabels[status.service_runner_status]}
							</span>
						</div>
						<div className="indicator-item">
							<span className="indicator-label">Scraper Service</span>
							<span
								className={`status-badge ${status.service_running ? "badge-success" : "badge-danger"}`}
							>
								<i className={`bi ${getServiceStatus(status.service_running)} me-2`}></i>
								{getServiceStatusMessage(status, remainingTime)}
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
								status.service_runner_status === "stopped",
								onFormChange
							)}
						</div>
					</div>

					<div className="actions-section">
						<ActionButton
							id="confirm-start-button"
							disabled={loading || ["stopping", "starting"].includes(status?.service_runner_status)}
							loading={loading}
							loadingText={
								status?.service_runner_status === "stopping"
									? "Stopping Service..."
									: "Starting Service..."
							}
							defaultText={serviceRunnerButtonLabels[status.service_runner_status]}
							fullWidth={true}
							onClick={status?.service_runner_status === "started" ? onStop : onStart}
						/>
					</div>
				</div>
			) : (
				<Spinner text={"Loading status..."} />
			)}
		</div>
	);
};
