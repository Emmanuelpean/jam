import { LayoutItem } from "react-grid-layout";

// Default positions for the built-in layout (replaces legacy cardRegistry)
const DEFAULT_POSITIONS: Record<string, Omit<LayoutItem, "i">> = {
	"stat-total-jobs": { x: 0, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
	"stat-applications": { x: 3, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
	"stat-pending": { x: 6, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
	"stat-follow-up": { x: 9, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
	"recent-activity": { x: 0, y: 8, w: 4, h: 12, minW: 3, minH: 8 },
	"follow-up-table": { x: 4, y: 8, w: 8, h: 12, minW: 4, minH: 8 },
	"upcoming-deadlines": { x: 0, y: 20, w: 8, h: 12, minW: 4, minH: 8 },
	"upcoming-interviews": { x: 8, y: 20, w: 4, h: 12, minW: 3, minH: 8 },
	"job-alerts": { x: 0, y: 32, w: 12, h: 16, minW: 6, minH: 8 },
};

export type MetricVariant =
	| "total_jobs"
	| "applications"
	| "pending"
	| "follow_up"
	| "active_applications"
	| "interview_rate"
	| "avg_response_time";
export type TableVariant =
	| "follow_up"
	| "upcoming_deadlines"
	| "job_alerts"
	| "favourites"
	| "favourite_jobs"
	| "error_jobs"
	| "recent_updates";
export type TimelineVariant =
	| "recent_activity"
	| "upcoming_interviews"
	| "status_updates"
	| "upcoming_deadlines_timeline"
	| "past_interviews";
export type GraphSource = "jobs" | "interviews" | "updates" | "scraped_jobs";
export type GraphField =
	| "application_date"
	| "application_status"
	| "source_aggregator"
	| "salary"
	| "attendance_type"
	| "personal_rating"
	| "city"
	| "country"
	| "interview_date"
	| "applied_via"
	| "application_funnel"
	| "interview_type"
	| "interview_attendance"
	| "update_date"
	| "update_type"
	| "scraped_count"
	| "imported_count"
	| "applied_count"
	| "import_rate"
	| "applied_rate";

export type WidgetType = "metric" | "table" | "timeline" | "graph" | "map";

// --- Per-widget numeric settings (previously stored as user preferences) ---

// A resolved setting handed to the configuration sidebar.
export interface WidgetSetting {
	key: string;
	label: string;
	value: number;
	onChange: (value: number) => void;
	min?: number;
	max?: number;
	helpText?: string;
}

// A reusable definition for a numeric setting. `key` is the config field it reads/writes.
export interface WidgetSettingTemplate {
	key: string;
	label: string;
	default: number;
	min: number;
	max: number;
	helpText?: string;
}

// Defined once and shared across every widget that uses them.
export const WIDGET_SETTING_TEMPLATES: Record<string, WidgetSettingTemplate> = {
	chaseThreshold: {
		key: "chaseThreshold",
		label: "Chase threshold (days)",
		default: 14,
		min: 1,
		max: 365,
		helpText: "Applications with no update for longer than this are flagged.",
	},
	deadlineThreshold: {
		key: "deadlineThreshold",
		label: "Deadline threshold (days)",
		default: 7,
		min: 1,
		max: 365,
		helpText: "Jobs with a deadline within this many days are shown.",
	},
	updateLimit: {
		key: "updateLimit",
		label: "Items shown",
		default: 10,
		min: 1,
		max: 1000,
		helpText: "Maximum number of items to display.",
	},
};

// Which setting templates apply to each widget variant (keyed by configToVariantKey).
export const WIDGET_VARIANT_SETTINGS: Record<string, string[]> = {
	follow_up: ["chaseThreshold"], // shared by the follow_up metric and table
	upcoming_deadlines: ["deadlineThreshold"],
	upcoming_deadlines_timeline: ["deadlineThreshold"],
	recent_activity: ["updateLimit"],
	status_updates: ["updateLimit"],
};

export interface MetricConfig {
	type: "metric";
	metric: MetricVariant;
	// Only used by the "follow_up" metric
	chaseThreshold?: number;
}
export interface TableConfig {
	type: "table";
	source: TableVariant;
	// Only used by the "follow_up" table
	chaseThreshold?: number;
	// Only used by the "upcoming_deadlines" table
	deadlineThreshold?: number;
}
export interface TimelineConfig {
	type: "timeline";
	feed: TimelineVariant;
	// Only used by the "upcoming_deadlines_timeline" feed
	deadlineThreshold?: number;
	// Only used by the "recent_activity" and "status_updates" feeds
	updateLimit?: number;
}

export type ChartType = "line" | "bar" | "pie";

export interface GraphConfig {
	type: "graph";
	source: GraphSource;
	field: GraphField;
	chartType?: ChartType;
	granularity?: "week" | "month";
	groupBy?: "platform" | "alert_name" | "platform_and_alert";
}
export type MapMetric = "job_count" | "avg_salary" | "keywords";
export type MapGranularity = "city" | "country";
export interface MapConfig {
	type: "map";
	metric: MapMetric;
	granularity?: MapGranularity;
}
export type WidgetConfig = MetricConfig | TableConfig | TimelineConfig | GraphConfig | MapConfig;

export interface WidgetInstance {
	id: string;
	config: WidgetConfig;
}

export interface DashboardLayoutData {
	widgets: WidgetInstance[];
	layout: LayoutItem[];
}

// --- Widget type definitions ---

export interface VariantDef {
	key: string;
	label: string;
	icon: string;
	description?: string;
	premiumOnly: boolean;
	group?: string;
	featured?: boolean;
}

export interface WidgetTypeDef {
	type: WidgetType;
	label: string;
	icon: string;
	description: string;
	variants: VariantDef[];
	defaultLayout: Omit<LayoutItem, "i">;
}

export const WIDGET_TYPE_DEFS: WidgetTypeDef[] = [
	{
		type: "metric",
		label: "Metric",
		icon: "speedometer2",
		description: "Key numbers at a glance",
		variants: [
			{
				key: "total_jobs",
				label: "Total Jobs",
				icon: "briefcase",
				description: "Total jobs in your database",
				premiumOnly: false,
			},
			{
				key: "applications",
				label: "Applications",
				icon: "send",
				description: "Total applications submitted",
				premiumOnly: false,
			},
			{
				key: "pending",
				label: "Pending",
				icon: "clock",
				description: "Applications awaiting a response",
				premiumOnly: false,
			},
			{
				key: "follow_up",
				label: "Need Follow-up",
				icon: "telephone",
				description: "Applications overdue for a chase",
				premiumOnly: false,
			},
			{
				key: "active_applications",
				label: "Active Applications",
				icon: "send-check",
				description: "Applications not yet rejected or withdrawn",
				premiumOnly: false,
			},
			{
				key: "interview_rate",
				label: "Interview Rate",
				icon: "person-check",
				description: "% of applications that led to an interview",
				premiumOnly: false,
			},
			{
				key: "avg_response_time",
				label: "Avg. Response Time",
				icon: "hourglass-split",
				description: "Average days from application to first update",
				premiumOnly: false,
			},
		],
		defaultLayout: { x: 0, y: 0, w: 2, h: 4, minW: 2, minH: 4 },
	},
	{
		type: "table",
		label: "Table",
		icon: "table",
		description: "Data tables and lists",
		variants: [
			{
				key: "follow_up",
				label: "Follow-up Required",
				icon: "telephone",
				description: "Applications that need chasing",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "upcoming_deadlines",
				label: "Upcoming Deadlines",
				icon: "clock",
				description: "Jobs with approaching deadlines",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "favourite_jobs",
				label: "Favourite Jobs",
				icon: "star",
				description: "Jobs you have marked as favourite",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "recent_updates",
				label: "Recent Updates",
				icon: "clock-history",
				description: "Jobs with the most recent interview or application activity",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "job_alerts",
				label: "Job Alerts",
				icon: "bell",
				description: "Jobs received from your scrapers",
				premiumOnly: true,
				group: "Job Scraping",
			},
			{
				key: "favourites",
				label: "Favourite Job Alerts",
				icon: "star-fill",
				description: "Job alerts matching your favourite filters",
				premiumOnly: false,
				group: "Job Scraping",
			},
			{
				key: "error_jobs",
				label: "Failed Jobs",
				icon: "exclamation-triangle",
				description: "Jobs that failed to be scraped or rated",
				premiumOnly: true,
				group: "Job Scraping",
			},
		],
		defaultLayout: { x: 0, y: 0, w: 8, h: 12, minW: 4, minH: 8 },
	},
	{
		type: "timeline",
		label: "Timeline",
		icon: "clock-history",
		description: "Activity feeds and schedules",
		variants: [
			{
				key: "recent_activity",
				label: "Recent Activity",
				icon: "clock-history",
				description: "Your latest applications and interviews",
				premiumOnly: false,
				group: "Applications",
			},
			{
				key: "status_updates",
				label: "Status Updates",
				icon: "envelope-open",
				description: "Replies and notes on your applications",
				premiumOnly: false,
				group: "Applications",
			},
			{
				key: "upcoming_deadlines_timeline",
				label: "Upcoming Deadlines",
				icon: "alarm",
				description: "Approaching application deadlines",
				premiumOnly: false,
				group: "Applications",
			},
			{
				key: "upcoming_interviews",
				label: "Upcoming Interviews",
				icon: "calendar-event",
				description: "Scheduled interviews coming up",
				premiumOnly: false,
				group: "Interviews",
			},
			{
				key: "past_interviews",
				label: "Past Interviews",
				icon: "calendar-check",
				description: "Interviews you have already attended",
				premiumOnly: false,
				group: "Interviews",
			},
		],
		defaultLayout: { x: 0, y: 0, w: 4, h: 12, minW: 3, minH: 8 },
	},
	{
		type: "graph",
		label: "Graph",
		icon: "bar-chart-line",
		description: "Charts and visualizations",
		variants: [
			{
				key: "application_date",
				label: "Applications Over Time",
				icon: "graph-up",
				description: "Application volume by date",
				premiumOnly: false,
				group: "Jobs",
				featured: true,
			},
			{
				key: "application_status",
				label: "Status Breakdown",
				icon: "pie-chart",
				description: "Applications split by status",
				premiumOnly: false,
				group: "Jobs",
				featured: true,
			},
			{
				key: "source_aggregator",
				label: "By Source",
				icon: "signpost-split",
				description: "Jobs grouped by job board",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "salary",
				label: "Salary Distribution",
				icon: "cash-stack",
				description: "Salary ranges across your jobs",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "attendance_type",
				label: "By Attendance",
				icon: "building",
				description: "Remote vs on-site breakdown",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "personal_rating",
				label: "By Rating",
				icon: "star",
				description: "Jobs grouped by your rating",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "city",
				label: "By City",
				icon: "geo-alt",
				description: "Jobs grouped by city",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "country",
				label: "By Country",
				icon: "globe2",
				description: "Jobs grouped by country",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "interview_date",
				label: "Interviews Over Time",
				icon: "graph-up-arrow",
				description: "Interview volume by date",
				premiumOnly: false,
				group: "Interviews",
				featured: true,
			},
			{
				key: "interview_type",
				label: "Interview Types",
				icon: "person-badge",
				description: "Interviews split by type",
				premiumOnly: false,
				group: "Interviews",
				featured: true,
			},
			{
				key: "interview_attendance",
				label: "Interview Attendance",
				icon: "building",
				description: "Remote vs on-site for interviews",
				premiumOnly: false,
				group: "Interviews",
				featured: true,
			},
			{
				key: "applied_via",
				label: "Applied Via",
				icon: "cursor-fill",
				description: "How you submitted each application",
				premiumOnly: false,
				group: "Jobs",
			},
			{
				key: "application_funnel",
				label: "Application Funnel",
				icon: "funnel",
				description: "Pipeline from applied to offer",
				premiumOnly: false,
				group: "Jobs",
				featured: true,
			},
			{
				key: "update_date",
				label: "Updates Over Time",
				icon: "chat-left-text",
				description: "Application update frequency over time",
				premiumOnly: false,
				group: "Updates",
				featured: true,
			},
			{
				key: "update_type",
				label: "Update Types",
				icon: "arrow-left-right",
				description: "Received vs sent updates",
				premiumOnly: false,
				group: "Updates",
				featured: true,
			},
			{
				key: "scraped_count",
				label: "Job Alerts Received",
				icon: "inbox",
				description: "Total job alerts by platform or alert",
				premiumOnly: true,
				group: "Job Alerts",
				featured: true,
			},
			{
				key: "imported_count",
				label: "Jobs Imported",
				icon: "box-arrow-in-down",
				description: "Job alerts imported as job entries",
				premiumOnly: true,
				group: "Job Alerts",
				featured: true,
			},
			{
				key: "applied_count",
				label: "Jobs Applied",
				icon: "send-check",
				description: "Imported jobs that were applied to",
				premiumOnly: true,
				group: "Job Alerts",
				featured: true,
			},
			{
				key: "import_rate",
				label: "Import Rate",
				icon: "percent",
				description: "% of job alerts imported",
				premiumOnly: true,
				group: "Job Alerts",
			},
			{
				key: "applied_rate",
				label: "Application Rate",
				icon: "percent",
				description: "% of job alerts applied to",
				premiumOnly: true,
				group: "Job Alerts",
			},
		],
		defaultLayout: { x: 0, y: 0, w: 6, h: 12, minW: 3, minH: 8 },
	},
	{
		type: "map",
		label: "Map",
		icon: "pin-map",
		description: "Geographic view of your jobs",
		variants: [
			{
				key: "job_count",
				label: "Jobs by Location",
				icon: "pin-map-fill",
				description: "Number of jobs at each location",
				premiumOnly: false,
			},
			{
				key: "avg_salary",
				label: "Salary by Location",
				icon: "cash-stack",
				description: "Average salary at each location",
				premiumOnly: false,
			},
			{
				key: "keywords",
				label: "Keywords by Location",
				icon: "tags",
				description: "Top tags at each location",
				premiumOnly: false,
			},
		],
		defaultLayout: { x: 0, y: 0, w: 8, h: 14, minW: 4, minH: 10 },
	},
];

// --- Helpers ---

export function generateWidgetId(): string {
	return `w-${crypto.randomUUID()}`;
}

export function configToVariantKey(config: WidgetConfig): string {
	switch (config.type) {
		case "metric":
			return config.metric;
		case "table":
			return config.source;
		case "timeline":
			return config.feed;
		case "graph":
			return config.field;
		case "map":
			return config.metric;
	}
}

// Effective value of a numeric setting for a widget, falling back to the template default.
export function getWidgetSettingValue(config: WidgetConfig, key: string): number {
	const value = (config as unknown as Record<string, unknown>)[key];
	return typeof value === "number" ? value : (WIDGET_SETTING_TEMPLATES[key]?.default ?? 0);
}

// Build the settings shown in a widget's configuration sidebar from its templates.
export function buildWidgetSettings(
	config: WidgetConfig,
	onConfigChange: (updated: WidgetConfig) => void
): WidgetSetting[] {
	const keys = WIDGET_VARIANT_SETTINGS[configToVariantKey(config)] ?? [];
	return keys.map((key: string): WidgetSetting => {
		const template = WIDGET_SETTING_TEMPLATES[key]!;
		return {
			key,
			label: template.label,
			min: template.min,
			max: template.max,
			helpText: template.helpText,
			value: getWidgetSettingValue(config, key),
			onChange: (v: number): void => onConfigChange({ ...config, [key]: v } as WidgetConfig),
		};
	});
}

// Whether a widget exposes any configurable settings (i.e. should show the config button).
export function widgetHasSettings(config: WidgetConfig): boolean {
	// Graphs are always configurable (source, field, chart type, …) via their own sidebar controls.
	if (config.type === "graph") return true;
	return (WIDGET_VARIANT_SETTINGS[configToVariantKey(config)] ?? []).length > 0;
}

export function isWidgetPremium(config: WidgetConfig): boolean {
	const typeDef = WIDGET_TYPE_DEFS.find((t) => t.type === config.type);
	if (!typeDef) return false;
	const variant = typeDef.variants.find((v) => v.key === configToVariantKey(config));
	return variant?.premiumOnly ?? false;
}

function filterPremium(data: DashboardLayoutData, isPremium: boolean): DashboardLayoutData {
	if (isPremium) return data;
	const filteredWidgets = data.widgets.filter((w) => !isWidgetPremium(w.config));
	const widgetIds = new Set(filteredWidgets.map((w) => w.id));
	return {
		...data,
		widgets: filteredWidgets,
		layout: data.layout.filter((l) => widgetIds.has(l.i)),
	};
}

// --- Default layout ---

export function getDefaultLayout(isPremium: boolean): DashboardLayoutData {
	const defaultWidgets: { config: WidgetConfig; oldId: string }[] = [
		{ config: { type: "metric", metric: "total_jobs" }, oldId: "stat-total-jobs" },
		{ config: { type: "metric", metric: "applications" }, oldId: "stat-applications" },
		{ config: { type: "metric", metric: "pending" }, oldId: "stat-pending" },
		{ config: { type: "metric", metric: "follow_up" }, oldId: "stat-follow-up" },
		{ config: { type: "timeline", feed: "recent_activity" }, oldId: "recent-activity" },
		{ config: { type: "table", source: "follow_up" }, oldId: "follow-up-table" },
		{ config: { type: "table", source: "upcoming_deadlines" }, oldId: "upcoming-deadlines" },
		{ config: { type: "timeline", feed: "upcoming_interviews" }, oldId: "upcoming-interviews" },
		{ config: { type: "table", source: "job_alerts" }, oldId: "job-alerts" },
	];

	const widgets: WidgetInstance[] = [];
	const layout: LayoutItem[] = [];

	for (const { config, oldId } of defaultWidgets) {
		if (isWidgetPremium(config) && !isPremium) continue;
		const id = `w-default-${oldId}`;
		widgets.push({ id, config });
		const pos = DEFAULT_POSITIONS[oldId];
		if (pos) {
			layout.push({ ...pos, i: id });
		}
	}

	return { widgets, layout };
}

// --- Parse layout data ---

export function parseLayoutData(data: string | null, isPremium: boolean): DashboardLayoutData {
	if (!data) return getDefaultLayout(isPremium);
	try {
		const parsed = JSON.parse(data) as Record<string, unknown>;
		if (parsed.widgets && parsed.layout) {
			return filterPremium(parsed as unknown as DashboardLayoutData, isPremium);
		}
		return getDefaultLayout(isPremium);
	} catch {
		return getDefaultLayout(isPremium);
	}
}

export function getDefaultLayoutForConfig(config: WidgetConfig): Omit<LayoutItem, "i"> {
	const typeDef = WIDGET_TYPE_DEFS.find((t) => t.type === config.type)!;
	return typeDef.defaultLayout;
}
