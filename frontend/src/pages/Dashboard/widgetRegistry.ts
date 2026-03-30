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
	"job-alerts": { x: 0, y: 32, w: 12, h: 12, minW: 6, minH: 8 },
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
	| "error_jobs";
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

export interface MetricConfig {
	type: "metric";
	metric: MetricVariant;
}
export interface TableConfig {
	type: "table";
	source: TableVariant;
}
export interface TimelineConfig {
	type: "timeline";
	feed: TimelineVariant;
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
export interface MapConfig {
	type: "map";
	metric: MapMetric;
}
export type WidgetConfig = MetricConfig | TableConfig | TimelineConfig | GraphConfig | MapConfig;

export interface WidgetInstance {
	id: string;
	config: WidgetConfig;
}

export interface DashboardLayoutDataV3 {
	version: 3;
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
			},
			{
				key: "upcoming_deadlines",
				label: "Upcoming Deadlines",
				icon: "clock",
				description: "Jobs with approaching deadlines",
				premiumOnly: false,
			},
			{
				key: "job_alerts",
				label: "Job Alerts",
				icon: "bell",
				description: "Jobs received from your scrapers",
				premiumOnly: true,
			},
			{
				key: "favourites",
				label: "Favourite Job Alerts",
				icon: "star-fill",
				description: "Scraped job alerts matching your favourite filters",
				premiumOnly: false,
			},
			{
				key: "favourite_jobs",
				label: "Favourite Jobs",
				icon: "star",
				description: "Jobs you have marked as favourite",
				premiumOnly: false,
			},
			{
				key: "error_jobs",
				label: "Failed Jobs",
				icon: "exclamation-triangle",
				description: "Jobs that failed to be scraped or rated",
				premiumOnly: true,
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
			},
			{
				key: "upcoming_interviews",
				label: "Upcoming Interviews",
				icon: "calendar-event",
				description: "Scheduled interviews coming up",
				premiumOnly: false,
			},
			{
				key: "past_interviews",
				label: "Past Interviews",
				icon: "calendar-check",
				description: "Interviews you have already attended",
				premiumOnly: false,
			},
			{
				key: "status_updates",
				label: "Status Updates",
				icon: "envelope-open",
				description: "Replies and notes on your applications",
				premiumOnly: false,
			},
			{
				key: "upcoming_deadlines_timeline",
				label: "Upcoming Deadlines",
				icon: "alarm",
				description: "Approaching application deadlines",
				premiumOnly: false,
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
				featured: true,
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
			},
			{
				key: "interview_attendance",
				label: "Interview Attendance",
				icon: "building",
				description: "Remote vs on-site for interviews",
				premiumOnly: false,
				group: "Interviews",
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
			},
			{
				key: "update_type",
				label: "Update Types",
				icon: "arrow-left-right",
				description: "Received vs sent updates",
				premiumOnly: false,
				group: "Updates",
			},
			{
				key: "scraped_count",
				label: "Jobs Scraped",
				icon: "inbox",
				description: "Total scraped jobs by platform or alert",
				premiumOnly: true,
				group: "Scraped Jobs",
				featured: true,
			},
			{
				key: "imported_count",
				label: "Jobs Imported",
				icon: "box-arrow-in-down",
				description: "Scraped jobs imported as job entries",
				premiumOnly: true,
				group: "Scraped Jobs",
			},
			{
				key: "applied_count",
				label: "Jobs Applied",
				icon: "send-check",
				description: "Imported jobs that were applied to",
				premiumOnly: true,
				group: "Scraped Jobs",
			},
			{
				key: "import_rate",
				label: "Import Rate",
				icon: "percent",
				description: "% of scraped jobs imported",
				premiumOnly: true,
				group: "Scraped Jobs",
			},
			{
				key: "applied_rate",
				label: "Application Rate",
				icon: "percent",
				description: "% of scraped jobs applied to",
				premiumOnly: true,
				group: "Scraped Jobs",
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

export function isWidgetPremium(config: WidgetConfig): boolean {
	const typeDef = WIDGET_TYPE_DEFS.find((t) => t.type === config.type);
	if (!typeDef) return false;
	const variant = typeDef.variants.find((v) => v.key === configToVariantKey(config));
	return variant?.premiumOnly ?? false;
}

function filterPremium(data: DashboardLayoutDataV3, isPremium: boolean): DashboardLayoutDataV3 {
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

export function getDefaultLayout(isPremium: boolean): DashboardLayoutDataV3 {
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

	return { version: 3, widgets, layout };
}

// --- Parse layout data ---

export function parseLayoutData(data: string | null, isPremium: boolean): DashboardLayoutDataV3 {
	if (!data) return getDefaultLayout(isPremium);
	try {
		const parsed = JSON.parse(data) as Record<string, unknown>;
		if (parsed.version === 3 && parsed.widgets && parsed.layout) {
			return filterPremium(parsed as unknown as DashboardLayoutDataV3, isPremium);
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
