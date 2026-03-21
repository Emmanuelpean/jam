import React, { useEffect, useMemo, useState } from "react";
import { CustomSelect } from "../../components/rendering/widgets/CustomSelect";
import { Button } from "react-bootstrap";
import {
	ResponsiveContainer,
	LineChart,
	Line,
	BarChart,
	Bar,
	Cell,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
} from "recharts";
import { useDataContext } from "../../contexts/DataContext";
import { GraphConfig, GraphSource } from "./widgetRegistry";
import { aggregateGraphData, ChartDataPoint, getFieldMeta, GRAPH_SOURCES } from "./graphAggregations";
import { SelectOption } from "../../components/rendering/form/FormOptions";
import { PieChart } from "../../components/Chart/PieChart";
import { DashboardCard } from "./DashboardCard";
import "./GraphWidget.scss";

const CHART_COLORS = [
	"#6366f1",
	"#8b5cf6",
	"#a855f7",
	"#ec4899",
	"#f43f5e",
	"#f97316",
	"#eab308",
	"#22c55e",
	"#14b8a6",
	"#06b6d4",
	"#3b82f6",
	"#6d28d9",
	"#059669",
	"#dc2626",
	"#0891b2",
];

interface GraphWidgetProps {
	config: GraphConfig;
	onConfigChange: (updated: GraphConfig) => void;
	isEditMode?: boolean;
}

const CustomTooltip = ({ active, payload, label }: any) => {
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
			<p style={{ margin: 0, color: entry.color ?? "var(--bs-body-color)" }}>Count: {entry.value}</p>
		</div>
	);
};

const renderLineChart = (data: ChartDataPoint[]) => (
	<ResponsiveContainer width="100%" height="100%">
		<LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
			<CartesianGrid strokeDasharray="3 3" stroke="var(--bs-border-color)" />
			<XAxis
				dataKey="name"
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				interval="preserveStartEnd"
			/>
			<YAxis
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				allowDecimals={false}
			/>
			<Tooltip content={<CustomTooltip />} />
			<Line type="monotone" dataKey="value" stroke={CHART_COLORS[0]} strokeWidth={2} dot={{ r: 3 }} />
		</LineChart>
	</ResponsiveContainer>
);

const renderBarChart = (data: ChartDataPoint[]) => (
	<ResponsiveContainer width="100%" height="100%">
		<BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
			<CartesianGrid strokeDasharray="3 3" stroke="var(--bs-border-color)" />
			<XAxis
				dataKey="name"
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				interval={0}
				angle={data.length > 8 ? -45 : 0}
				textAnchor={data.length > 8 ? "end" : "middle"}
				height={data.length > 8 ? 60 : 30}
			/>
			<YAxis
				tick={{ fontSize: 13, fill: "var(--bs-body-color)" }}
				stroke="var(--bs-border-color)"
				allowDecimals={false}
			/>
			<Tooltip content={<CustomTooltip />} />
			<Bar dataKey="value" radius={[4, 4, 0, 0]}>
				{data.map((_, index) => (
					<Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
				))}
			</Bar>
		</BarChart>
	</ResponsiveContainer>
);

const GraphWidget: React.FC<GraphWidgetProps> = ({ config, onConfigChange, isEditMode }) => {
	const dataContext = useDataContext();
	const [sidebarOpen, setSidebarOpen] = useState(false);

	useEffect(() => {
		if (!isEditMode) setSidebarOpen(false);
	}, [isEditMode]);

	const sourceMeta = GRAPH_SOURCES[config.source];
	const fieldMeta = getFieldMeta(config.source, config.field);
	const effectiveChartType = config.chartType ?? fieldMeta?.defaultChartType ?? "bar";
	const effectiveGranularity = config.granularity ?? "month";

	const data = useMemo(
		() => aggregateGraphData(config.field, dataContext, effectiveGranularity),
		[config.field, dataContext, effectiveGranularity]
	);

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

	const granularityOptions: SelectOption[] = [
		{ value: "week", label: "Week" },
		{ value: "month", label: "Month" },
	];

	const renderChart = () => {
		switch (effectiveChartType) {
			case "line":
				return renderLineChart(data);
			case "bar":
				return renderBarChart(data);
			case "pie":
				return <PieChart data={data} colors={CHART_COLORS} />;
		}
	};

	return (
		<DashboardCard
			icon={fieldMeta?.icon ?? "bar-chart-line"}
			title={fieldMeta?.label ?? "Graph"}
			isEmpty={data.length === 0}
			emptyState={{
				icon: "bar-chart-line",
				title: "No data available",
				description: "Add some data to see this chart",
			}}
			bodyPadding={false}
			headerAction={
				isEditMode ? (
					<Button
						className="graph-sidebar-toggle"
						variant={`${sidebarOpen ? "primary" : "outline-primary"}`}
						onClick={(): void => setSidebarOpen((prev: boolean): boolean => !prev)}
						title="Configure"
					>
						<i className={`bi bi-gear`}></i>
					</Button>
				) : undefined
			}
		>
			<div className="graph-body">
				<div className="graph-chart-container">{renderChart()}</div>
				<div className={`graph-sidebar ${sidebarOpen ? "open" : ""}`}>
					<div className="graph-sidebar-content">
						<label className="graph-sidebar-label">Source</label>
						<CustomSelect
							id="graph-source"
							value={sourceOptions.find((o) => o.value === config.source) ?? null}
							onChange={(opt) => opt && !Array.isArray(opt) && handleSourceChange(opt.value as GraphSource)}
							options={sourceOptions}
							isSearchable={false}
							isClearable={false}
							size="sm"
						/>

						<label className="graph-sidebar-label">Display</label>
						<CustomSelect
							id="graph-field"
							value={fieldOptions.find((o) => o.value === config.field) ?? null}
							onChange={(opt) =>
								opt && !Array.isArray(opt) &&
								onConfigChange({ type: "graph", source: config.source, field: opt.value as GraphConfig["field"] })
							}
							options={fieldOptions}
							isSearchable={false}
							isClearable={false}
							size="sm"
						/>

						{fieldMeta && fieldMeta.supportedChartTypes.length > 1 && (
							<>
								<label className="graph-sidebar-label">Chart</label>
								<CustomSelect
									id="graph-chart-type"
									value={chartTypeOptions.find((o) => o.value === effectiveChartType) ?? null}
									onChange={(opt) =>
										opt && !Array.isArray(opt) &&
										onConfigChange({ ...config, chartType: opt.value as GraphConfig["chartType"] })
									}
									options={chartTypeOptions}
									isSearchable={false}
									isClearable={false}
									size="sm"
								/>
							</>
						)}

						{fieldMeta?.supportsGranularity && (
							<>
								<label className="graph-sidebar-label">Period</label>
								<CustomSelect
									id="graph-granularity"
									value={granularityOptions.find((o) => o.value === effectiveGranularity) ?? null}
									onChange={(opt) =>
										opt && !Array.isArray(opt) &&
										onConfigChange({ ...config, granularity: opt.value as GraphConfig["granularity"] })
									}
									options={granularityOptions}
									isSearchable={false}
									isClearable={false}
									size="sm"
								/>
							</>
						)}
					</div>
				</div>
			</div>
		</DashboardCard>
	);
};

export default GraphWidget;
