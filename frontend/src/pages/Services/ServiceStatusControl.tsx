import React, { JSX, useEffect, useRef, useState } from "react";
import { Popover } from "../../components/Popover/Popover";
import { Tooltip } from "../../components/Tooltip/Tooltip";
import { useAuth } from "../../contexts/AuthContext";
import { useAlert } from "../../contexts/AlertContext";
import { BaseServiceApi, ServiceStatus, ServiceUpdatePayload } from "../../services/api/Services";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import {
	RenderLabeledInput,
	renderControl,
	renderStatusIcons,
	serviceEnabledLabel,
	useServiceControl,
} from "./ServiceUtils";

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
	api: BaseServiceApi;
	buildUpdate?: (values: Record<string, number>) => ServiceUpdatePayload;
}

export const ServiceStatusControl = ({
	status,
	remainingTime,
	fetchStatus,
	ariaLabel,
	configFields = [],
	api,
	buildUpdate,
}: ServiceStatusControlProps): JSX.Element => {
	const { token } = useAuth();
	const { showConfirm } = useAlert();
	const [form, setForm] = useState<Record<string, number>>({});
	const initialised = useRef<boolean>(false);
	const savedValues = useRef<Record<string, number>>({});

	useEffect((): void => {
		if (status && !initialised.current) {
			const seeded = Object.fromEntries(configFields.map((f) => [f.name, f.getValue(status)]));
			setForm(seeded);
			savedValues.current = seeded;
			initialised.current = true;
		}
	}, [status]);

	const { loading, run } = useServiceControl(token, fetchStatus);

	const onChange = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const { name, value } = event.target as HTMLInputElement;
		setForm((prev: any) => ({ ...prev, [name]: value === "" ? "" : Number(value) || 3 }));
	};

	const onToggleEnabled = async (): Promise<void> => {
		if (!status) return;
		// Deactivating stops the service running on its schedule, so confirm first; enabling is immediate.
		if (status.is_enabled) {
			const confirmed = await showConfirm({
				title: "Deactivate service",
				message: `Deactivate ${status.display_name}? It will stop running on its schedule until re-enabled.`,
				confirmText: "Deactivate",
				cancelText: "Cancel",
			});
			if (!confirmed) return;
		}
		void run((t: string) => api.setEnabled(!status.is_enabled, t));
	};

	const saveOnBlur = (): void => {
		if (!buildUpdate) return;
		const allValid = configFields.every((f) => {
			const v = form[f.name];
			return typeof v === "number" && v > 0;
		});
		const changed = configFields.some((f) => form[f.name] !== savedValues.current[f.name]);
		if (!allValid || !changed) return;
		savedValues.current = { ...form };
		void run((t: string) => api.update(buildUpdate(form), t));
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
						true,
						onChange,
						false,
						saveOnBlur
					)
				)}
			</>
		) : null;

	const enabled: boolean = !!status?.is_enabled;

	return (
		<div className="service-status-control" aria-label={ariaLabel}>
			<Popover
				trigger={renderStatusIcons(status, remainingTime)}
				ariaLabel={`${ariaLabel} actions`}
				onClose={saveOnBlur}
			>
				{(close) =>
					renderControl(status, fields, loading, {
						onRunNow: (): void => {
							close();
							void run((t: string) => api.runNow(t));
						},
					})
				}
			</Popover>
			<Tooltip
				delay={500}
				content={
					status
						? `Service: ${serviceEnabledLabel(status)} — click to ${enabled ? "disable" : "enable"}`
						: "…"
				}
			>
				<button
					type="button"
					role="switch"
					className={`service-enabled-toggle ${enabled ? "is-enabled" : "is-disabled"}`}
					disabled={!status || loading}
					aria-checked={enabled}
					aria-label={`${enabled ? "Disable" : "Enable"} service`}
					onClick={onToggleEnabled}
				>
					<span className="service-enabled-toggle__track">
						<span className="service-enabled-toggle__thumb">
							{loading && <span className="service-enabled-toggle__spinner" />}
						</span>
					</span>
				</button>
			</Tooltip>
		</div>
	);
};
