import React, { JSX, useState } from "react";
import { Form, InputGroup } from "react-bootstrap";
import { ServiceStatus } from "../../services/api/Services";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { formatDuration } from "../../utils/TimeUtils";
import { HelpBubble } from "../../components/HelpBubble/HelpBubble";
import { SeriesData } from "../../components/Chart/LineChart";
import { Tooltip } from "../../components/Tooltip/Tooltip";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import Spinner from "../../components/Spinner/Spinner";

export const successColor = "#22c55e";
export const failureColor = "#ef4444";
export const skippedColor = "#007cff";
export const copiedColor = "#bcbcbc";

export const formatErrorMessage = (err: unknown): string => {
	if (!err) return "";
	if (typeof err === "string") return err;
	if (err instanceof Error) return err.message;
	try {
		return JSON.stringify(err);
	} catch {
		return String(err);
	}
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

export const RenderLabeledInput = (
	id: string,
	label: string,
	help: string,
	value: number,
	unitText: string = "",
	isRequired: boolean = false,
	onChange?: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void,
	disabled: boolean = false
): JSX.Element => {
	return (
		<Form.Group id={id}>
			<InputGroup>
				<InputGroup.Text className="d-flex align-items-center">
					<span>{label}</span>
					{isRequired && <span className="text-danger">*</span>}
					{help && <HelpBubble helpText={help} />}
				</InputGroup.Text>

				<Form.Control name={id} type="text" value={value} onChange={onChange} disabled={disabled} />

				{unitText && <InputGroup.Text>{unitText}</InputGroup.Text>}
			</InputGroup>
		</Form.Group>
	);
};

export const createSeries = (logs: any[], id: string, getValue: (log: any) => number, color?: string): SeriesData => ({
	id,
	color,
	data: logs
		.slice()
		.reverse()
		.map((log: any): { x: Date; y: number } => ({
			x: log.run_datetime,
			y: getValue(log),
		})),
});

export const useServiceControl = (
	token: string | null,
	fetchStatus: () => Promise<void>,
	doStart: (token: string) => Promise<unknown>,
	doStop: (token: string) => Promise<unknown>
) => {
	const [loading, setLoading] = useState<boolean>(false);

	const run = async (action: (token: string) => Promise<unknown>): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			await action(token);
			await fetchStatus();
		} catch (err: any) {
			console.log(err?.message);
		} finally {
			setLoading(false);
		}
	};

	return {
		loading,
		handleStart: (): Promise<void> => run(doStart),
		handleStop: (): Promise<void> => run(doStop),
	};
};

export const renderStatusIcons = (status: ServiceStatus | null, remainingTime: number | null): JSX.Element => {
	const runnerActive: boolean = !!status && ["started", "starting"].includes(status.service_runner_status);
	const isStopping: boolean = status?.service_runner_status === "stopping";
	const serviceRunning: boolean = !!status?.service_running;
	const showCountdown: boolean = status?.service_runner_status === "started" && !serviceRunning;
	return (
		<div className="service-status-icons">
			<Tooltip
				delay={500}
				content={`Service runner: ${status ? serviceRunnerStatusLabels[status.service_runner_status] : "…"}`}
			>
				<i
					className={`bi bi-cpu-fill service-status-icon service-status-icon--runner ${runnerActive ? "is-on" : "is-off"} ${isStopping ? "is-stopping" : ""}`}
				/>
			</Tooltip>
			<Tooltip delay={500} content={`Service: ${serviceRunning ? "Running" : "Idle"}`}>
				<i className={`bi bi-activity service-status-icon ${serviceRunning ? "is-on is-running" : "is-off"}`} />
			</Tooltip>
			{showCountdown && (
				<Tooltip delay={500} content="Time until next run">
					<span className="service-next-run">({formatDuration(remainingTime)})</span>
				</Tooltip>
			)}
		</div>
	);
};

export const renderControl = (
	status: ServiceStatus | null,
	fields: React.ReactNode,
	loading: boolean,
	onStart: () => void,
	onStop: () => void
): JSX.Element => {
	if (!status) return <Spinner text={"Loading status..."} />;
	return (
		<div className="service-control">
			{fields && <div className="config-fields">{fields}</div>}
			<div className="actions-section">
				<ActionButton
					id="confirm-start-button"
					disabled={loading || ["stopping", "starting"].includes(status.service_runner_status)}
					loading={loading}
					loadingText={
						status.service_runner_status === "stopping" ? "Stopping Service..." : "Starting Service..."
					}
					defaultText={serviceRunnerButtonLabels[status.service_runner_status]}
					fullWidth={true}
					onClick={status.service_runner_status === "started" ? onStop : onStart}
				/>
			</div>
		</div>
	);
};
