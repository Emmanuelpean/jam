import React, { JSX } from "react";
import { Form, InputGroup } from "react-bootstrap";
import { ServiceStatus, ThreadStatus } from "../../services/api/Services";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { formatDuration } from "../../utils/TimeUtils";
import { HelpBubble } from "../../components/rendering/widgets/HelpBubble";
import { SeriesData } from "../../components/Charts/LineChart";

export const successColor = "#22c55e";
export const failureColor = "#ef4444";
export const infoColor = "#0d38e3";

export interface ServiceStatusCardProps {
	status: ServiceStatus | null;
	remainingTime: number | null;
	loading: boolean;
	onFormChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void;
	onStart: () => Promise<void>;
	onStop: () => Promise<void>;
}

export const serviceRunnerStatusIcons: Record<ThreadStatus, string> = {
	started: "bi-check-circle-fill",
	stopped: "bi-x-circle-fill",
	starting: "bi-play-circle-fill",
	stopping: "bi-dash-circle-fill",
};

export const serviceRunnerStatusLabels: Record<string, string> = {
	started: "Active",
	starting: "Starting",
	stopping: "Stopping",
	stopped: "Inactive",
};

export const serviceRunnerButtonLabels: Record<string, string> = {
	started: "Stop Service Runner",
	stopping: "Service Runner Stopping",
	starting: "Service Runner Starting",
	stopped: "Start Service Runner",
};

export const getServiceStatus = (isRunning: boolean): string => {
	return isRunning ? "bi-check-circle-fill" : "bi-x-circle-fill";
};

export const getServiceStatusMessage = (status: ServiceStatus, remainingTime: number | null): string => {
	if (status.service_runner_status === "stopped") {
		return "Stopped";
	}
	if (status.service_running) {
		return "Running";
	}
	return `Stopped (${formatDuration(remainingTime)} s before next run)`;
};

export const RenderLabeledInput = (
	id: string,
	label: string,
	help: string,
	value: number,
	unitText: string = "",
	isRequired: boolean = false,
	onChange?: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void,
): JSX.Element => {
	return (
		<Form.Group id={id}>
			<InputGroup>
				<InputGroup.Text className="d-flex align-items-center">
					<span>{label}</span>
					{isRequired && <span className="text-danger">*</span>}
					{help && <HelpBubble helpText={help} />}
				</InputGroup.Text>

				<Form.Control name={id} type="text" value={value} onChange={onChange} />

				{unitText && <InputGroup.Text>{unitText}</InputGroup.Text>}
			</InputGroup>
		</Form.Group>
	);
};

export const createSeries = (logs: any[], id: string, color: string, getValue: (log: any) => number): SeriesData => ({
	id,
	color,
	data: logs
		.slice()
		.reverse()
		.map((log: any): { x: Date; y: number } => ({
			x: new Date(log.run_datetime),
			y: getValue(log),
		})),
});
