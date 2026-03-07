import { LayoutItem } from "react-grid-layout";
import { CARD_REGISTRY, DashboardLayoutData } from "./cardRegistry";

// --- Widget types ---

export type MetricVariant = "total_jobs" | "applications" | "pending" | "follow_up";
export type TableVariant = "follow_up" | "upcoming_deadlines" | "job_alerts";
export type TimelineVariant = "recent_activity" | "upcoming_interviews";
export type GraphSource = "jobs" | "interviews";
export type GraphField =
	| "application_date"
	| "application_status"
	| "source_aggregator"
	| "salary"
	| "attendance_type"
	| "personal_rating"
	| "city"
	| "country"
	| "interview_date";

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
			{ key: "total_jobs", label: "Total Jobs", icon: "briefcase", premiumOnly: false },
			{ key: "applications", label: "Applications", icon: "send", premiumOnly: false },
			{ key: "pending", label: "Pending", icon: "clock", premiumOnly: false },
			{ key: "follow_up", label: "Need Follow-up", icon: "telephone", premiumOnly: false },
		],
		defaultLayouts: {
			lg: { x: 0, y: 0, w: 3, h: 8, minW: 2, minH: 4 },
			md: { x: 0, y: 0, w: 3, h: 8, minW: 2, minH: 4 },
			sm: { x: 0, y: 0, w: 6, h: 8, minW: 3, minH: 4 },
		},
	},
	{
		type: "table",
		label: "Table",
		icon: "table",
		description: "Data tables and lists",
		variants: [
			{ key: "follow_up", label: "Follow-up Required", icon: "telephone", premiumOnly: false },
			{ key: "upcoming_deadlines", label: "Upcoming Deadlines", icon: "clock", premiumOnly: false },
			{ key: "job_alerts", label: "Job Alerts", icon: "bell", premiumOnly: true },
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
			{ key: "recent_activity", label: "Recent Activity", icon: "clock-history", premiumOnly: false },
			{ key: "upcoming_interviews", label: "Upcoming Interviews", icon: "calendar-event", premiumOnly: false },
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
			{ key: "application_date", label: "Applications Over Time", icon: "graph-up", premiumOnly: false, group: "Jobs" },
			{ key: "application_status", label: "Status Breakdown", icon: "pie-chart", premiumOnly: false, group: "Jobs" },
			{ key: "source_aggregator", label: "By Source", icon: "signpost-split", premiumOnly: false, group: "Jobs" },
			{ key: "salary", label: "Salary Distribution", icon: "cash-stack", premiumOnly: false, group: "Jobs" },
			{ key: "attendance_type", label: "By Attendance", icon: "building", premiumOnly: false, group: "Jobs" },
			{ key: "personal_rating", label: "By Rating", icon: "star", premiumOnly: false, group: "Jobs" },
			{ key: "city", label: "By City", icon: "geo-alt", premiumOnly: false, group: "Jobs" },
			{ key: "country", label: "By Country", icon: "globe2", premiumOnly: false, group: "Jobs" },
			{ key: "interview_date", label: "Interviews Over Time", icon: "graph-up-arrow", premiumOnly: false, group: "Interviews" },
		],
		defaultLayouts: {
			lg: { x: 0, y: 0, w: 6, h: 12, minW: 4, minH: 8 },
			md: { x: 0, y: 0, w: 6, h: 12, minW: 4, minH: 8 },
			sm: { x: 0, y: 0, w: 12, h: 12, minW: 6, minH: 8 },
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
		items
			.filter((l) => l.i in oldToNewId)
			.map((l) => ({ ...l, i: oldToNewId[l.i]! }));

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

export function parseLayoutData(json: string | null, isPremium: boolean): DashboardLayoutDataV2 {
	if (!json) return getDefaultLayout(isPremium);
	try {
		const parsed = JSON.parse(json);
		if (parsed.version === 1 && parsed.visibleCards && parsed.layouts) {
			return filterPremium(migrateV1toV2(parsed as DashboardLayoutData), isPremium);
		}
		if (parsed.version === 2 && parsed.widgets && parsed.layouts) {
			return filterPremium(parsed as DashboardLayoutDataV2, isPremium);
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
