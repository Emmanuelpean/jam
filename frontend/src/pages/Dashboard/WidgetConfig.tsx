import React, { ReactNode, JSX } from "react";
import { DashboardCard, EmptyStateProps } from "./DashboardCard";
import { StatCard } from "./StatCard";
import { WidgetSetting } from "./widgetRegistry";
import "./WidgetConfig.scss";

export type { WidgetSetting };

interface WidgetConfigSidebarProps {
	open: boolean;
	settings: WidgetSetting[];
	idPrefix?: string;
}

export const WidgetConfigSidebar: React.FC<WidgetConfigSidebarProps> = ({ open, settings, idPrefix }) => (
	<div className={`widget-config-sidebar ${open ? "open" : ""}`}>
		<div className="widget-config-sidebar-content">
			{settings.map((setting: WidgetSetting): JSX.Element => {
				const inputId = idPrefix ? `${idPrefix}-${setting.key}` : setting.key;
				return (
					<div key={setting.key} className="widget-config-field">
						<label className="widget-config-label" htmlFor={inputId}>
							{setting.label}
						</label>
						<input
							id={inputId}
							type="number"
							className="form-control form-control--sm"
							value={setting.value}
							min={setting.min}
							max={setting.max}
							onChange={(e: React.ChangeEvent<HTMLInputElement>): void => {
								const parsed = Number(e.target.value);
								if (!Number.isNaN(parsed)) setting.onChange(parsed);
							}}
						/>
						{setting.helpText && <small className="widget-config-help">{setting.helpText}</small>}
					</div>
				);
			})}
		</div>
	</div>
);

// --- DashboardCard with a configuration sidebar (tables & timelines) ---
// The toggle button lives in the dashboard grid-item overlay; `open` is controlled by the parent.

interface ConfigurableDashboardCardProps {
	icon: string;
	title: string;
	subtitle?: string;
	badgeValue?: number;
	path?: string;
	id?: string;
	isEmpty?: boolean;
	emptyState?: EmptyStateProps;
	settings: WidgetSetting[];
	isEditMode?: boolean;
	open?: boolean;
	// Horizontal padding around the content. Disable for content that manages its own
	// padding and should scroll flush to the widget edge (e.g. timelines).
	bodyPadding?: boolean;
	// Custom sidebar controls rendered in place of the default numeric settings sidebar
	// (e.g. the graph widget's source/field/chart-type selects).
	sidebarContent?: ReactNode;
	children: ReactNode;
}

export const ConfigurableDashboardCard: React.FC<ConfigurableDashboardCardProps> = ({
	icon,
	title,
	subtitle,
	badgeValue,
	path,
	id,
	isEmpty = false,
	emptyState,
	settings,
	isEditMode = false,
	open = false,
	bodyPadding = true,
	sidebarContent,
	children,
}: ConfigurableDashboardCardProps): JSX.Element => {
	const showConfig = isEditMode && (sidebarContent != null || settings.length > 0);

	const renderEmptyState = (): ReactNode => {
		if (!emptyState) return null;
		return (
			<div className="text-center py-5 px-4 flex-grow-1 d-flex flex-column justify-content-center">
				<div className="mb-3">
					<i className={`bi bi-${emptyState.icon} text-muted`} style={{ fontSize: "3.5rem" }}></i>
				</div>
				<h6 id={id ? `${id}-empty` : undefined} className="text-muted fw-semibold">
					{emptyState.title}
				</h6>
				<p className="text-muted small mb-0">{emptyState.description}</p>
			</div>
		);
	};

	return (
		<DashboardCard
			icon={icon}
			title={title}
			subtitle={subtitle}
			badgeValue={badgeValue}
			path={path}
			id={id}
			bodyPadding={false}
		>
			<div className="widget-config-wrapper">
				<div className={`widget-config-main ${bodyPadding ? "px-3" : ""}`}>
					{isEmpty && emptyState ? renderEmptyState() : children}
				</div>
				{showConfig &&
					(sidebarContent != null ? (
						<div className={`widget-config-sidebar ${open ? "open" : ""}`}>
							<div className="widget-config-sidebar-content">{sidebarContent}</div>
						</div>
					) : (
						<WidgetConfigSidebar open={open} settings={settings} idPrefix={id} />
					))}
			</div>
		</DashboardCard>
	);
};

// --- StatCard with a configuration overlay (metrics) ---
// The toggle button lives in the dashboard grid-item overlay; `open` is controlled by the parent.

interface ConfigurableStatCardProps {
	id?: string;
	name: string;
	value: number | string;
	icon: string;
	variant: string;
	description?: string;
	settings: WidgetSetting[];
	isEditMode?: boolean;
	open?: boolean;
}

export const ConfigurableStatCard: React.FC<ConfigurableStatCardProps> = ({
	id,
	name,
	value,
	icon,
	variant,
	description,
	settings,
	isEditMode = false,
	open = false,
}: ConfigurableStatCardProps): JSX.Element => {
	const showConfig = isEditMode && settings.length > 0;

	return (
		<div className="widget-config-statcard-wrapper">
			<StatCard id={id} name={name} value={value} icon={icon} variant={variant} description={description} />
			{showConfig && <WidgetConfigSidebar open={open} settings={settings} idPrefix={id} />}
		</div>
	);
};
