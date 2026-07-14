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

export const serviceEnabledLabel = (status: ServiceStatus | null): string =>
	!status ? "…" : status.is_enabled ? "Enabled" : "Disabled";

export const RenderLabeledInput = (
	id: string,
	label: string,
	help: string,
	value: number,
	unitText: string = "",
	isRequired: boolean = false,
	onChange?: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void,
	disabled: boolean = false,
	onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
): JSX.Element => {
	return (
		<Form.Group id={id}>
			<InputGroup>
				<InputGroup.Text className="d-flex align-items-center">
					<span>{label}</span>
					{isRequired && <span className="text-danger">*</span>}
					{help && <HelpBubble helpText={help} />}
				</InputGroup.Text>

				<Form.Control
					name={id}
					type="text"
					value={value}
					onChange={onChange}
					onBlur={onBlur}
					disabled={disabled}
				/>

				{unitText && <InputGroup.Text>{unitText}</InputGroup.Text>}
			</InputGroup>
		</Form.Group>
	);
};

export const runDatetimeMs = (log: { run_datetime: any }): number => new Date(log.run_datetime).getTime();

export const findLogByX = <T extends { id: number; run_datetime: any }>(logs: T[], xMs: number): T | undefined =>
	logs.find((log: T): boolean => runDatetimeMs(log) === xMs);

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

export const useServiceControl = (token: string | null, fetchStatus: () => Promise<void>) => {
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

	return { loading, run };
};

export const formatNextRun = (remainingTime: number | null): string | null => {
	if (remainingTime === null) return null;
	return remainingTime <= 0 ? "Due now" : formatDuration(remainingTime);
};

export const renderStatusIcons = (status: ServiceStatus | null, remainingTime: number | null): JSX.Element => {
	const running: boolean = !!status?.is_running;
	const nextRunLabel: string | null = formatNextRun(remainingTime);
	const isDue: boolean = remainingTime !== null && remainingTime <= 0 && !running;
	return (
		<div className="service-status-icons">
			<Tooltip delay={500} content={`Run: ${running ? "In progress" : "Idle"}`}>
				<i className={`bi bi-activity service-status-icon ${running ? "is-on is-running" : "is-off"}`} />
			</Tooltip>
			{nextRunLabel && !running && (
				<Tooltip delay={500} content={isDue ? "Next run is due" : "Time until next run"}>
					<span className="service-next-run">({nextRunLabel})</span>
				</Tooltip>
			)}
		</div>
	);
};

export interface ServiceControlHandlers {
	onRunNow: () => void;
}

export const renderControl = (
	status: ServiceStatus | null,
	fields: React.ReactNode,
	loading: boolean,
	handlers: ServiceControlHandlers
): JSX.Element => {
	if (!status) return <Spinner text={"Loading status..."} />;
	return (
		<div className="service-control">
			{fields && <div className="config-fields">{fields}</div>}
			<div className="actions-section">
				<ActionButton
					id="run-now-button"
					disabled={loading || status.is_running}
					loading={false}
					defaultText={status.is_running ? "Run In Progress" : "Run Now"}
					fullWidth={true}
					onClick={handlers.onRunNow}
				/>
			</div>
		</div>
	);
};
