import { DataContextValue } from "../../contexts/DataContext";
import { GraphField, GraphSource } from "./widgetRegistry";

export interface ChartDataPoint {
	name: string;
	value: number;
	[key: string]: string | number;
}

type ChartType = "line" | "bar" | "pie";

export interface GraphFieldMeta {
	key: GraphField;
	label: string;
	icon: string;
	supportedChartTypes: ChartType[];
	defaultChartType: ChartType;
	supportsGranularity: boolean;
}

export interface GraphSourceMeta {
	label: string;
	icon: string;
	fields: GraphFieldMeta[];
}

export const GRAPH_SOURCES: Record<GraphSource, GraphSourceMeta> = {
	jobs: {
		label: "Jobs",
		icon: "briefcase",
		fields: [
			{ key: "application_date", label: "Applications Over Time", icon: "graph-up", supportedChartTypes: ["line", "bar"], defaultChartType: "line", supportsGranularity: true },
			{ key: "application_status", label: "Status Breakdown", icon: "pie-chart", supportedChartTypes: ["pie", "bar"], defaultChartType: "pie", supportsGranularity: false },
			{ key: "source_aggregator", label: "By Source", icon: "signpost-split", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "salary", label: "Salary Distribution", icon: "cash-stack", supportedChartTypes: ["bar"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "attendance_type", label: "By Attendance", icon: "building", supportedChartTypes: ["pie", "bar"], defaultChartType: "pie", supportsGranularity: false },
			{ key: "personal_rating", label: "By Rating", icon: "star", supportedChartTypes: ["bar"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "city", label: "By City", icon: "geo-alt", supportedChartTypes: ["bar"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "country", label: "By Country", icon: "globe2", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "applied_via", label: "Applied Via", icon: "cursor-fill", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "application_funnel", label: "Application Funnel", icon: "funnel", supportedChartTypes: ["bar"], defaultChartType: "bar", supportsGranularity: false },
		],
	},
	interviews: {
		label: "Interviews",
		icon: "calendar-event",
		fields: [
			{ key: "interview_date", label: "Interviews Over Time", icon: "graph-up-arrow", supportedChartTypes: ["line", "bar"], defaultChartType: "line", supportsGranularity: true },
			{ key: "interview_type", label: "Interview Types", icon: "person-badge", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "interview_attendance", label: "Interview Attendance", icon: "building", supportedChartTypes: ["pie", "bar"], defaultChartType: "pie", supportsGranularity: false },
		],
	},
	updates: {
		label: "Updates",
		icon: "chat-left-text",
		fields: [
			{ key: "update_date", label: "Updates Over Time", icon: "chat-left-text", supportedChartTypes: ["line", "bar"], defaultChartType: "line", supportsGranularity: true },
			{ key: "update_type", label: "Update Types", icon: "arrow-left-right", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
		],
	},
	scraped_jobs: {
		label: "Scraped Jobs",
		icon: "inbox",
		fields: [
			{ key: "scraped_count", label: "Jobs Scraped", icon: "inbox", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "imported_count", label: "Jobs Imported", icon: "box-arrow-in-down", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "applied_count", label: "Jobs Applied", icon: "send-check", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "import_rate", label: "Import Rate", icon: "percent", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
			{ key: "applied_rate", label: "Application Rate", icon: "percent", supportedChartTypes: ["bar", "pie"], defaultChartType: "bar", supportsGranularity: false },
		],
	},
};

export function getFieldMeta(source: GraphSource, field: GraphField): GraphFieldMeta | undefined {
	return GRAPH_SOURCES[source].fields.find((f) => f.key === field);
}

export function getSourceForField(field: GraphField): GraphSource {
	for (const [source, meta] of Object.entries(GRAPH_SOURCES)) {
		if (meta.fields.some((f) => f.key === field)) return source as GraphSource;
	}
	return "jobs";
}

// --- Aggregation helpers ---

function bucketByTime(dates: (Date | string | null | undefined)[], granularity: "week" | "month"): ChartDataPoint[] {
	const counts = new Map<string, number>();

	for (const raw of dates) {
		if (!raw) continue;
		const d = new Date(raw);
		if (isNaN(d.getTime())) continue;

		let key: string;
		if (granularity === "month") {
			key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
		} else {
			const day = d.getDay();
			const monday = new Date(d);
			monday.setDate(d.getDate() - ((day + 6) % 7));
			key = `${monday.getFullYear()}-${String(monday.getMonth() + 1).padStart(2, "0")}-${String(monday.getDate()).padStart(2, "0")}`;
		}
		counts.set(key, (counts.get(key) ?? 0) + 1);
	}

	return Array.from(counts.entries())
		.sort(([a], [b]) => a.localeCompare(b))
		.map(([name, value]) => ({ name, value }));
}

function groupAndCount(values: (string | null | undefined)[], labelFallback = "Unknown"): ChartDataPoint[] {
	const counts = new Map<string, number>();
	for (const v of values) {
		const label = v || labelFallback;
		counts.set(label, (counts.get(label) ?? 0) + 1);
	}
	return Array.from(counts.entries())
		.sort((a, b) => b[1] - a[1])
		.map(([name, value]) => ({ name, value }));
}

const SALARY_BUCKETS: [string, number, number][] = [
	["< 20k", 0, 20000],
	["20-40k", 20000, 40000],
	["40-60k", 40000, 60000],
	["60-80k", 60000, 80000],
	["80-100k", 80000, 100000],
	["100k+", 100000, Infinity],
];

function aggregateSalaryDistribution(ctx: DataContextValue): ChartDataPoint[] {
	const buckets = new Map<string, number>(SALARY_BUCKETS.map(([label]) => [label, 0]));

	for (const job of ctx.jobs) {
		if (job.salary_min == null) continue;
		for (const [label, min, max] of SALARY_BUCKETS) {
			if (job.salary_min >= min && job.salary_min < max) {
				buckets.set(label, (buckets.get(label) ?? 0) + 1);
				break;
			}
		}
	}

	return SALARY_BUCKETS.map(([label]) => ({ name: label, value: buckets.get(label) ?? 0 }));
}

function aggregateJobsByLocationField(ctx: DataContextValue, field: "city" | "country"): ChartDataPoint[] {
	const locationMap = new Map<number, string>();
	for (const loc of ctx.locations) {
		const value = loc[field];
		if (value) locationMap.set(loc.id, value);
	}

	const counts = new Map<string, number>();
	for (const job of ctx.jobs) {
		if (job.location_id == null) continue;
		const name = locationMap.get(job.location_id);
		if (!name) continue;
		counts.set(name, (counts.get(name) ?? 0) + 1);
	}

	return Array.from(counts.entries())
		.sort((a, b) => b[1] - a[1])
		.slice(0, 15)
		.map(([name, value]) => ({ name, value }));
}

function aggregateJobsBySource(ctx: DataContextValue): ChartDataPoint[] {
	const aggMap = new Map<number, string>();
	for (const agg of ctx.aggregators) {
		aggMap.set(agg.id, agg.name);
	}

	const values = ctx.jobs.map((job) =>
		job.source_aggregator_id != null ? (aggMap.get(job.source_aggregator_id) ?? "Unknown") : null
	);
	return groupAndCount(values, "No Source");
}

function aggregateJobsByRating(ctx: DataContextValue): ChartDataPoint[] {
	const counts = new Map<string, number>();
	for (const job of ctx.jobs) {
		if (job.personal_rating == null) continue;
		const label = String(job.personal_rating);
		counts.set(label, (counts.get(label) ?? 0) + 1);
	}

	return Array.from(counts.entries())
		.sort(([a], [b]) => Number(a) - Number(b))
		.map(([name, value]) => ({ name: `${name} star${name === "1" ? "" : "s"}`, value }));
}

function aggregateApplicationFunnel(ctx: DataContextValue): ChartDataPoint[] {
	const jobsWithInterviews = new Set(ctx.interviews.map((i) => i.job_id));
	const apps = ctx.jobs.filter((j) => j.application_date || j.application_status);
	return [
		{ name: "Applied", value: apps.length },
		{ name: "Interviewed", value: apps.filter((j) => jobsWithInterviews.has(j.id)).length },
		{ name: "Offered", value: apps.filter((j) => j.application_status === "offer").length },
		{ name: "Rejected", value: apps.filter((j) => j.application_status === "rejected").length },
		{ name: "Withdrawn", value: apps.filter((j) => j.application_status === "withdrawn").length },
	];
}

// --- Main dispatcher ---

export function aggregateGraphData(
	field: GraphField,
	ctx: DataContextValue,
	granularity: "week" | "month"
): ChartDataPoint[] {
	switch (field) {
		case "application_date":
			return bucketByTime(
				ctx.jobs.filter((j) => j.application_date).map((j) => j.application_date),
				granularity
			);
		case "application_status":
			return groupAndCount(
				ctx.jobs.filter((j) => j.application_status).map((j) => j.application_status),
				"No Status"
			);
		case "source_aggregator":
			return aggregateJobsBySource(ctx);
		case "salary":
			return aggregateSalaryDistribution(ctx);
		case "interview_date":
			return bucketByTime(
				ctx.interviews.map((i) => i.date),
				granularity
			);
		case "attendance_type":
			return groupAndCount(
				ctx.jobs.filter((j) => j.attendance_type).map((j) => j.attendance_type),
				"Not Specified"
			);
		case "personal_rating":
			return aggregateJobsByRating(ctx);
		case "city":
			return aggregateJobsByLocationField(ctx, "city");
		case "country":
			return aggregateJobsByLocationField(ctx, "country");
		case "applied_via":
			return groupAndCount(
				ctx.jobs.filter((j) => j.applied_via).map((j) => j.applied_via),
				"Not Specified"
			);
		case "application_funnel":
			return aggregateApplicationFunnel(ctx);
		case "interview_type":
			return groupAndCount(ctx.interviews.map((i) => i.type), "Unknown");
		case "interview_attendance":
			return groupAndCount(
				ctx.interviews.filter((i) => i.attendance_type).map((i) => i.attendance_type),
				"Not Specified"
			);
		case "update_date":
			return bucketByTime(ctx.jobApplicationUpdates.map((u) => u.date), granularity);
		case "update_type":
			return groupAndCount(ctx.jobApplicationUpdates.map((u) => u.type), "Unknown");
		default:
			return [];
	}
}
