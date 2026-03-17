import React, { JSX } from "react";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import Spinner from "../../components/Spinner/Spinner";
import { ServiceStatus } from "../../services/api/Services";
import {
	getServiceStatus,
	getServiceStatusMessage,
	serviceRunnerButtonLabels,
	serviceRunnerStatusIcons,
	serviceRunnerStatusLabels,
	ServiceStatusCardProps,
} from "./ServiceUtils";

interface SharedServiceStatusCardProps extends ServiceStatusCardProps {
	serviceLabel?: string;
	renderFields?: (status: ServiceStatus) => React.ReactNode;
}

export const ServiceStatusCard = ({
	status,
	remainingTime,
	loading,
	onStart,
	onStop,
	serviceLabel = "Service",
	renderFields,
}: SharedServiceStatusCardProps): JSX.Element => {
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
							<span className="indicator-label">{serviceLabel}</span>
							<span
								className={`status-badge ${status.service_running ? "badge-success" : "badge-danger"}`}
							>
								<i className={`bi ${getServiceStatus(status.service_running)} me-2`}></i>
								{getServiceStatusMessage(status, remainingTime)}
							</span>
						</div>
					</div>

					{renderFields && (
						<div>
							<div className="config-fields">{renderFields(status)}</div>
						</div>
					)}

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
