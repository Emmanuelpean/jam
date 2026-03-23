import { LayoutItem } from "react-grid-layout";
import { CARD_REGISTRY, DashboardLayoutData } from "./cardRegistry";

export type MetricVariant =
	| "total_jobs"
	| "applications"
	| "pending"
	| "follow_up"
	| "active_applications"
	| "interview_rate"
	| "avg_response_time";
export type TableVariant = "follow_up" | "upcoming_deadlines" | "job_alerts" | "favourites";
export type TimelineVariant =
	| "recent_activity"
	| "upcoming_interviews"
	| "status_updates"
	| "upcoming_deadlines_timeline"
	| "past_interviews";
export type GraphSource = "jobs" | "interviews" | "updates";
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
	| "update_type";

export type WidgetType = "metric" | "table" | "timeline" | "graph";

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
export interface GraphConfig {
	type: "graph";
	source: GraphSource;
	field: GraphField;
	chartType?: "line" | "bar" | "pie";
	granularity?: "week" | "month";
}
export type WidgetConfig = MetricConfig | TableConfig | TimelineConfig | GraphConfig;

export interface WidgetInstance {
	id: string;
	config: WidgetConfig;
}

export interface DashboardLayoutDataV2 {
	version: 2;
	widgets: WidgetInstance[];
	layouts: {
		lg: LayoutItem[];
		md: LayoutItem[];
		sm: LayoutItem[];
	};
}

// --- Widget type definitions ---

export interface VariantDef {
	key: string;
	label: string;
	icon: string;
	description?: string;
	premiumOnly: boolean;
	group?: string;
}

export interface WidgetTypeDef {
	type: WidgetType;
	label: string;
	icon: string;
	description: string;
	variants: VariantDef[];
	defaultLayouts: {
		lg: Omit<LayoutItem, "i">;
		md: Omit<LayoutItem, "i">;
		sm: Omit<LayoutItem, "i">;
	};
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
		defaultLayouts: {
			lg: { x: 0, y: 0, w: 2, h: 4, minW: 1, minH: 4 },
			md: { x: 0, y: 0, w: 2, h: 4, minW: 1, minH: 4 },
			sm: { x: 0, y: 0, w: 2, h: 4, minW: 1, minH: 4 },
		},
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
		],
		defaultLayouts: {
			lg: { x: 0, y: 0, w: 8, h: 12, minW: 4, minH: 8 },
			md: { x: 0, y: 0, w: 8, h: 12, minW: 4, minH: 8 },
			sm: { x: 0, y: 0, w: 12, h: 12, minW: 6, minH: 8 },
		},
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
		defaultLayouts: {
			lg: { x: 0, y: 0, w: 4, h: 12, minW: 3, minH: 8 },
			md: { x: 0, y: 0, w: 4, h: 12, minW: 3, minH: 8 },
			sm: { x: 0, y: 0, w: 12, h: 12, minW: 6, minH: 8 },
		},
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
			},
			{
				key: "application_status",
				label: "Status Breakdown",
				icon: "pie-chart",
				description: "Applications split by status",
				premiumOnly: false,
				group: "Jobs",
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
		],
		defaultLayouts: {
			lg: { x: 0, y: 0, w: 6, h: 12, minW: 3, minH: 8 },
			md: { x: 0, y: 0, w: 6, h: 12, minW: 3, minH: 8 },
			sm: { x: 0, y: 0, w: 12, h: 12, minW: 3, minH: 8 },
		},
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
	}
}

export function isWidgetPremium(config: WidgetConfig): boolean {
	const typeDef = WIDGET_TYPE_DEFS.find((t) => t.type === config.type);
	if (!typeDef) return false;
	const variant = typeDef.variants.find((v) => v.key === configToVariantKey(config));
	return variant?.premiumOnly ?? false;
}

function filterPremium(data: DashboardLayoutDataV2, isPremium: boolean): DashboardLayoutDataV2 {
	if (isPremium) return data;
	const filteredWidgets = data.widgets.filter((w) => !isWidgetPremium(w.config));
	const widgetIds = new Set(filteredWidgets.map((w) => w.id));
	return {
		...data,
		widgets: filteredWidgets,
		layouts: {
			lg: data.layouts.lg.filter((l) => widgetIds.has(l.i)),
			md: data.layouts.md.filter((l) => widgetIds.has(l.i)),
			sm: data.layouts.sm.filter((l) => widgetIds.has(l.i)),
		},
	};
}

// --- V1 → V2 migration ---

const OLD_ID_TO_CONFIG: Record<string, WidgetConfig> = {
	"stat-total-jobs": { type: "metric", metric: "total_jobs" },
	"stat-applications": { type: "metric", metric: "applications" },
	"stat-pending": { type: "metric", metric: "pending" },
	"stat-follow-up": { type: "metric", metric: "follow_up" },
	"follow-up-table": { type: "table", source: "follow_up" },
	"upcoming-deadlines": { type: "table", source: "upcoming_deadlines" },
	"job-alerts": { type: "table", source: "job_alerts" },
	"recent-activity": { type: "timeline", feed: "recent_activity" },
	"upcoming-interviews": { type: "timeline", feed: "upcoming_interviews" },
};

function migrateV1toV2(v1: DashboardLayoutData): DashboardLayoutDataV2 {
	const widgets: WidgetInstance[] = [];
	const oldToNewId: Record<string, string> = {};

	for (const oldId of v1.visibleCards) {
		const config = OLD_ID_TO_CONFIG[oldId];
		if (!config) continue;
		const newId = `w-migrated-${oldId}`;
		oldToNewId[oldId] = newId;
		widgets.push({ id: newId, config });
	}

	const remapLayout = (items: LayoutItem[]): LayoutItem[] =>
		items.filter((l) => l.i in oldToNewId).map((l) => ({ ...l, i: oldToNewId[l.i]! }));

	return {
		version: 2,
		widgets,
		layouts: {
			lg: remapLayout(v1.layouts.lg),
			md: remapLayout(v1.layouts.md),
			sm: remapLayout(v1.layouts.sm),
		},
	};
}

// --- Default layout ---

export function getDefaultLayout(isPremium: boolean): DashboardLayoutDataV2 {
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
	const layouts: DashboardLayoutDataV2["layouts"] = { lg: [], md: [], sm: [] };

	for (const { config, oldId } of defaultWidgets) {
		if (isWidgetPremium(config) && !isPremium) continue;
		const id = `w-default-${oldId}`;
		widgets.push({ id, config });
		const cardDef = CARD_REGISTRY.find((c) => c.id === oldId);
		if (cardDef) {
			for (const bp of ["lg", "md", "sm"] as const) {
				layouts[bp].push({ ...cardDef.layouts[bp], i: id });
			}
		}
	}

	return { version: 2, widgets, layouts };
}

// --- Parse layout data ---

export function parseLayoutData(data: string | null, isPremium: boolean): DashboardLayoutDataV2 {
	console.log(getDefaultLayout(isPremium));
	if (!data) return getDefaultLayout(isPremium);
	try {
		const parsed = JSON.parse(data) as Record<string, unknown>;
		if (parsed.version === 1 && parsed.visibleCards && parsed.layouts) {
			return filterPremium(migrateV1toV2(parsed as unknown as DashboardLayoutData), isPremium);
		}
		if (parsed.version === 2 && parsed.widgets && parsed.layouts) {
			return filterPremium(parsed as unknown as DashboardLayoutDataV2, isPremium);
		}
		return getDefaultLayout(isPremium);
	} catch {
		return getDefaultLayout(isPremium);
	}
}

export function getDefaultLayoutsForConfig(config: WidgetConfig): WidgetTypeDef["defaultLayouts"] {
	const typeDef = WIDGET_TYPE_DEFS.find((t) => t.type === config.type)!;
	return typeDef.defaultLayouts;
}
