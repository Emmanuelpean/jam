import React, { JSX, useEffect, useRef, useState } from "react";
import { Popover } from "../../components/Popover/Popover";
import { useAuth } from "../../contexts/AuthContext";
import { ServiceStatus } from "../../services/api/Services";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { RenderLabeledInput, renderControl, renderStatusIcons, useServiceControl } from "./ServiceUtils";

// A single configurable field of a service runner (e.g. its run period), with how to
// read its current value from the service status.
export interface ServiceConfigField {
	name: string;
	label: string;
	help: string;
	unit: string;
	getValue: (status: ServiceStatus) => number;
}

interface ServiceStatusControlProps {
	status: ServiceStatus | null;
	remainingTime: number | null;
	fetchStatus: () => Promise<void>;
	ariaLabel: string;
	configFields?: ServiceConfigField[];
	start: (values: Record<string, number>, token: string) => Promise<unknown>;
	stop: (token: string) => Promise<unknown>;
}

// The service status icons that open a popover to configure and start/stop the
// service runner. The status is supplied by the parent so it is only polled once.
export const ServiceStatusControl = ({
	status,
	remainingTime,
	fetchStatus,
	ariaLabel,
	configFields = [],
	start,
	stop,
}: ServiceStatusControlProps): JSX.Element => {
	const { token } = useAuth();
	const [form, setForm] = useState<Record<string, number>>({});
	const initialised = useRef<boolean>(false);

	// Seed the config form once from the status, so polling doesn't clobber edits.
	useEffect((): void => {
		if (status && !initialised.current) {
			setForm(Object.fromEntries(configFields.map((f) => [f.name, f.getValue(status)])));
			initialised.current = true;
		}
	}, [status]);

	const control = useServiceControl(
		token,
		fetchStatus,
		(t: string) => start(form, t),
		(t: string) => stop(t)
	);

	const disabled: boolean = status?.service_runner_status !== "stopped";

	const onChange = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const { name, value } = event.target as HTMLInputElement;
		setForm((prev: any) => ({ ...prev, [name]: value === "" ? "" : Number(value) || 3 }));
	};

	const fields: React.ReactNode =
		status && configFields.length > 0 ? (
			<>
				{configFields.map((f) =>
					RenderLabeledInput(
						f.name,
						f.label,
						f.help,
						form[f.name] ?? 0,
						f.unit,
						!disabled,
						onChange,
						disabled
					)
				)}
			</>
		) : null;

	return (
		<Popover trigger={renderStatusIcons(status, remainingTime)} ariaLabel={ariaLabel}>
			{(close) =>
				renderControl(
					status,
					fields,
					control.loading,
					() => {
						close();
						void control.handleStart();
					},
					() => {
						close();
						void control.handleStop();
					}
				)
			}
		</Popover>
	);
};
