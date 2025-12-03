import React, { JSX } from "react";
import { Form, InputGroup } from "react-bootstrap";
import { ScraperStatus, ThreadStatus } from "../../services/Api";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { formatDuration } from "../../utils/TimeUtils";
import { HelpBubble } from "../../components/rendering/widgets/HelpBubble";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import Spinner from "../../components/spinner/Spinner";
import { FormData } from "./EISDashboardPage";

interface ServiceStatusCardProps {
	status: ScraperStatus | null;
	remainingTime: number | null;
	formData: FormData;
	loading: boolean;
	onFormChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void;
	onStart: () => Promise<void>;
	onStop: () => Promise<void>;
}

const threadStatusIcons: Record<ThreadStatus, string> = {
	started: "bi-check-circle-fill",
	stopped: "bi-x-circle-fill",
	starting: "bi-play-circle-fill",
	stopping: "bi-dash-circle-fill",
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

const getScraperStatus = (isRunning: boolean): string => {
	return isRunning ? "bi-check-circle-fill" : "bi-x-circle-fill";
};

const getScraperStatusMessage = (status: ScraperStatus, remainingTime: number | null): string => {
	if (status.thread_status === "stopped") {
		return "Stopped";
	}
	if (status.scraper_running) {
		return "Running";
	}
	return `Stopped (${formatDuration(remainingTime)} s before next run)`;
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

export const ServiceStatusCard = ({
	status,
	remainingTime,
	formData,
	loading,
	onFormChange,
	onStart,
	onStop,
}: ServiceStatusCardProps): JSX.Element => {
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
							<span className="indicator-label">Scraper Service</span>
							<span
								className={`status-badge ${status.scraper_running ? "badge-success" : "badge-danger"}`}
							>
								<i className={`bi ${getScraperStatus(status.scraper_running)} me-2`}></i>
								{getScraperStatusMessage(status, remainingTime)}
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
								onFormChange,
							)}
							{RenderLabeledInput(
								"timedelta_days",
								"Time Delta",
								"Number of days back to scrape job postings for each run.",
								formData.timedelta_days,
								"Day(s)",
								status.thread_status === "stopped",
								onFormChange,
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
							onClick={status?.thread_status === "started" ? onStop : onStart}
						/>
					</div>
				</div>
			) : (
				<Spinner text={"Loading status..."} />
			)}
		</div>
	);
};
