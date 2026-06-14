import React, { useEffect, useMemo, useState } from "react";
import { CustomSelect } from "../../components/rendering/widgets/CustomSelect";
import {
	ResponsiveContainer,
	LineChart,
	Line,
	BarChart,
	Bar,
	Rectangle,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
} from "recharts";
import { useDataContext } from "../../contexts/DataContext";
import { useAuth } from "../../contexts/AuthContext";
import { scrapedJobApi, ScrapedJobPlatformStat } from "../../services/api/Services";
import { GraphConfig, GraphSource } from "./widgetRegistry";
import { aggregateGraphData, ChartDataPoint, getFieldMeta, GRAPH_SOURCES } from "./graphAggregations";
import { SelectOption } from "../../components/rendering/form/FormOptions";
import { PieChart } from "../../components/Chart/PieChart";
import { ConfigurableDashboardCard } from "./WidgetConfig";
import "./GraphWidget.scss";

const CHART_COLORS: string[] = [
	"#6366f1", // indigo
	"#f97316", // orange
	"#22c55e", // green
	"#ec4899", // pink
	"#06b6d4", // cyan
	"#dc2626", // red
	"#14b8a6", // teal
	"#eab308", // yellow
	"#3b82f6", // blue
	"#a855f7", // purple
	"#059669", // emerald
	"#f43f5e", // rose
	"#0891b2", // sky
	"#8b5cf6", // violet
	"#6d28d9", // dark purple
];

interface GraphWidgetProps {
	config: GraphConfig;
	onConfigChange: (updated: GraphConfig) => void;
	isEditMode?: boolean;
	open?: boolean;
}

const CustomTooltip = ({ active, payload, label, suffix = "" }: any) => {
	if (!active || !payload?.length) return null;
	const entry = payload[0];
	return (
		<div
			style={{
				backgroundColor: "var(--bs-card-bg)",
				padding: "8px 12px",
				border: "1px solid var(--bs-border-color)",
				borderRadius: "4px",
				boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
			}}
		>
			<p style={{ margin: 0, fontWeight: 600, color: "var(--bs-body-color)" }}>{entry.name ?? label}</p>
			<p style={{ margin: 0, color: entry.color ?? "var(--bs-body-color)" }}>
				{entry.value}
				{suffix}
			</p>
		</div>
	);
};

const AXIS_LABEL_STYLE = { fill: "var(--bs-secondary-color)", fontSize: 11 };

const renderLineChart = (data: ChartDataPoint[], suffix = "", xLabel?: string, yLabel?: string) => (
	<ResponsiveContainer width="100%" height="100%">
		<LineChart data={data} margin={{ top: 5, right: 20, left: yLabel ? 10 : 0, bottom: xLabel ? 20 : 5 }}>
			<CartesianGrid strokeDasharray="3 3" stroke="var(--bs-border-color)" />
			<XAxis
				dataKey="name"
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				interval="preserveStartEnd"
				label={
					xLabel
						? { value: xLabel, position: "insideBottom", offset: -10, style: AXIS_LABEL_STYLE }
						: undefined
				}
			/>
			<YAxis
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				allowDecimals={false}
				tickFormatter={(v) => `${v}${suffix}`}
				label={
					yLabel
						? {
								value: yLabel,
								angle: -90,
								position: "insideLeft",
								offset: 15,
								style: { ...AXIS_LABEL_STYLE, textAnchor: "middle" },
							}
						: undefined
				}
			/>
			<Tooltip content={<CustomTooltip suffix={suffix} />} />
			<Line
				type="monotone"
				dataKey="value"
				stroke={CHART_COLORS[0]}
				strokeWidth={2}
				dot={{ r: 3 }}
				isAnimationActive={false}
			/>
		</LineChart>
	</ResponsiveContainer>
);

const renderBarChart = (data: ChartDataPoint[], suffix = "", xLabel?: string, yLabel?: string) => (
	<ResponsiveContainer width="100%" height="100%">
		<BarChart
			data={data}
			margin={{ top: 5, right: 20, left: yLabel ? 10 : 0, bottom: data.length > 8 ? 60 : xLabel ? 20 : 5 }}
		>
			<CartesianGrid strokeDasharray="3 3" stroke="var(--bs-border-color)" />
			<XAxis
				dataKey="name"
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				interval={0}
				angle={data.length > 8 ? -45 : 0}
				textAnchor={data.length > 8 ? "end" : "middle"}
				height={data.length > 8 ? 60 : xLabel ? 40 : 30}
				label={
					xLabel && data.length <= 8
						? { value: xLabel, position: "insideBottom", offset: -10, style: AXIS_LABEL_STYLE }
						: undefined
				}
			/>
			<YAxis
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				allowDecimals={false}
				tickFormatter={(v) => `${v}${suffix}`}
				label={
					yLabel
						? {
								value: yLabel,
								angle: -90,
								position: "insideLeft",
								offset: 15,
								style: { ...AXIS_LABEL_STYLE, textAnchor: "middle" },
							}
						: undefined
				}
			/>
			<Tooltip content={<CustomTooltip suffix={suffix} />} />
			<Bar
				dataKey="value"
				isAnimationActive={false}
				shape={(props: any) => (
					<Rectangle
						{...props}
						fill={CHART_COLORS[props.index % CHART_COLORS.length]}
						radius={[4, 4, 0, 0]}
					/>
				)}
			/>
		</BarChart>
	</ResponsiveContainer>
);

const GraphWidget: React.FC<GraphWidgetProps> = ({ config, onConfigChange, isEditMode, open }) => {
	const dataContext = useDataContext();
	const { token } = useAuth();
	const [rawPlatformStats, setRawPlatformStats] = useState<ScrapedJobPlatformStat[]>([]);

	useEffect(() => {
		if (config.source !== "scraped_jobs" || !token) return;
		scrapedJobApi.platformStats(token).then((res) => {
			if (res.data) setRawPlatformStats(res.data);
		});
	}, [config.source, token]);

	const sourceMeta = GRAPH_SOURCES[config.source];
	const fieldMeta = getFieldMeta(config.source, config.field);
	const effectiveChartType = config.chartType ?? fieldMeta?.defaultChartType ?? "bar";
	const effectiveGranularity = config.granularity ?? "month";
	const effectiveGroupBy = config.groupBy ?? "platform";

	const getGroupKey = (stat: ScrapedJobPlatformStat): string => {
		if (effectiveGroupBy === "platform") return stat.platform;
		if (effectiveGroupBy === "alert_name") return stat.alert_name ?? "Unknown";
		return `${stat.platform} — ${stat.alert_name ?? "Unknown"}`;
	};

	const data = useMemo(() => {
		if (config.source === "scraped_jobs") {
			if (config.field === "import_rate" || config.field === "applied_rate") {
				const numeratorKey = config.field === "import_rate" ? "imported_count" : "applied_count";
				const scraped = new Map<string, number>();
				const numerator = new Map<string, number>();
				for (const stat of rawPlatformStats) {
					const key = getGroupKey(stat);
					scraped.set(key, (scraped.get(key) ?? 0) + stat.scraped_count);
					numerator.set(key, (numerator.get(key) ?? 0) + stat[numeratorKey]);
				}
				return Array.from(scraped.entries())
					.map(([name, total]) => ({
						name,
						value: total > 0 ? Math.round((numerator.get(name)! / total) * 100) : 0,
					}))
					.sort((a, b) => b.value - a.value);
			}
			const metricKey = config.field as "scraped_count" | "imported_count" | "applied_count";
			const counts = new Map<string, number>();
			for (const stat of rawPlatformStats) {
				const key = getGroupKey(stat);
				counts.set(key, (counts.get(key) ?? 0) + stat[metricKey]);
			}
			return Array.from(counts.entries())
				.sort((a, b) => b[1] - a[1])
				.map(([name, value]) => ({ name, value }));
		}
		return aggregateGraphData(config.field, dataContext, effectiveGranularity);
	}, [
		config.source,
		config.field,
		config.groupBy,
		rawPlatformStats,
		effectiveGroupBy,
		dataContext,
		effectiveGranularity,
	]);

	const handleSourceChange = (newSource: GraphSource) => {
		if (newSource === config.source) return;
		const firstField = GRAPH_SOURCES[newSource].fields[0]!;
		onConfigChange({ type: "graph", source: newSource, field: firstField.key });
	};

	const sourceOptions: SelectOption[] = (Object.keys(GRAPH_SOURCES) as GraphSource[]).map((src) => ({
		value: src,
		label: GRAPH_SOURCES[src].label,
	}));

	const fieldOptions: SelectOption[] = sourceMeta.fields.map((f) => ({
		value: f.key,
		label: f.label,
	}));

	const chartTypeOptions: SelectOption[] = (fieldMeta?.supportedChartTypes ?? []).map((ct) => ({
		value: ct,
		label: ct.charAt(0).toUpperCase() + ct.slice(1),
	}));

	const groupByOptions: SelectOption[] = [
		{ value: "platform", label: "Platform" },
		{ value: "alert_name", label: "Alert Name" },
		{ value: "platform_and_alert", label: "Platform & Alert" },
	];

	const granularityOptions: SelectOption[] = [
		{ value: "week", label: "Week" },
		{ value: "month", label: "Month" },
	];

	const suffix = config.field === "import_rate" || config.field === "applied_rate" ? "%" : "";

	const xLabel = fieldMeta?.supportsGranularity ? (effectiveGranularity === "week" ? "Week" : "Month") : undefined;
	const yLabel = fieldMeta?.yLabel;

	const renderChart = () => {
		switch (effectiveChartType) {
			case "line":
				return renderLineChart(data, suffix, xLabel, yLabel);
			case "bar":
				return renderBarChart(data, suffix, xLabel, yLabel);
			case "pie":
				return <PieChart data={data} colors={CHART_COLORS} suffix={suffix} />;
		}
	};

	const sidebarContent = (
		<>
			<div className="widget-config-field">
				<label className="widget-config-label" htmlFor="graph-source">
					Source
				</label>
				<CustomSelect
					id="graph-source"
					value={sourceOptions.find((o: SelectOption): boolean => o.value === config.source) ?? null}
					onChange={(opt) => opt && !Array.isArray(opt) && handleSourceChange(opt.value as GraphSource)}
					options={sourceOptions}
					isSearchable={false}
					isClearable={false}
					size="sm"
				/>
			</div>

			<div className="widget-config-field">
				<label className="widget-config-label" htmlFor="graph-field">
					Display
				</label>
				<CustomSelect
					id="graph-field"
					value={fieldOptions.find((o: SelectOption): boolean => o.value === config.field) ?? null}
					onChange={(opt) =>
						opt &&
						!Array.isArray(opt) &&
						onConfigChange({
							type: "graph",
							source: config.source,
							field: opt.value as GraphConfig["field"],
						})
					}
					options={fieldOptions}
					isSearchable={false}
					isClearable={false}
					size="sm"
				/>
			</div>

			{config.source === "scraped_jobs" && (
				<div className="widget-config-field">
					<label className="widget-config-label" htmlFor="graph-group-by">
						Group By
					</label>
					<CustomSelect
						id="graph-group-by"
						value={groupByOptions.find((o: SelectOption): boolean => o.value === effectiveGroupBy) ?? null}
						onChange={(opt) =>
							opt &&
							!Array.isArray(opt) &&
							onConfigChange({ ...config, groupBy: opt.value as GraphConfig["groupBy"] })
						}
						options={groupByOptions}
						isSearchable={false}
						isClearable={false}
						size="sm"
					/>
				</div>
			)}

			{fieldMeta && fieldMeta.supportedChartTypes.length > 1 && (
				<div className="widget-config-field">
					<label className="widget-config-label" htmlFor="graph-chart-type">
						Chart
					</label>
					<CustomSelect
						id="graph-chart-type"
						value={
							chartTypeOptions.find((o: SelectOption): boolean => o.value === effectiveChartType) ?? null
						}
						onChange={(opt) =>
							opt &&
							!Array.isArray(opt) &&
							onConfigChange({ ...config, chartType: opt.value as GraphConfig["chartType"] })
						}
						options={chartTypeOptions}
						isSearchable={false}
						isClearable={false}
						size="sm"
					/>
				</div>
			)}

			{fieldMeta?.supportsGranularity && (
				<div className="widget-config-field">
					<label className="widget-config-label" htmlFor="graph-granularity">
						Period
					</label>
					<CustomSelect
						id="graph-granularity"
						value={granularityOptions.find((o) => o.value === effectiveGranularity) ?? null}
						onChange={(opt) =>
							opt &&
							!Array.isArray(opt) &&
							onConfigChange({
								...config,
								granularity: opt.value as GraphConfig["granularity"],
							})
						}
						options={granularityOptions}
						isSearchable={false}
						isClearable={false}
						size="sm"
					/>
				</div>
			)}
		</>
	);

	return (
		<ConfigurableDashboardCard
			icon={fieldMeta?.icon ?? "bar-chart-line"}
			title={fieldMeta?.label ?? "Graph"}
			isEmpty={data.length === 0}
			emptyState={{
				icon: "bar-chart-line",
				title: "No data available",
				description: "Add some data to see this chart",
			}}
			settings={[]}
			isEditMode={isEditMode}
			open={open}
			sidebarContent={sidebarContent}
		>
			<div className="graph-chart-container">{renderChart()}</div>
		</ConfigurableDashboardCard>
	);
};

export default GraphWidget;
