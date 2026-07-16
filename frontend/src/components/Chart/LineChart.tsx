import { JSX, useState } from "react";

import {
	CartesianGrid,
	Label,
	Legend,
	Line,
	LineChart as RechartsLineChart,
	ReferenceLine,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
import type { LegendPayload } from "recharts/types/component/DefaultLegendContent";
import { toDdMmYyyyHhMm } from "../../utils/TimeUtils";
import LoadingSpinner from "../Spinner/Spinner";

interface DataPoint {
	x: number | string | Date;
	y: number | null;
}

export interface SeriesData {
	id: string;
	color?: string;
	data: DataPoint[];
}

const CHART_PALETTE: string[] = ["var(--bs-primary)", "#f59e0b", "#22c55e", "#ef4444", "#8b5cf6", "#06b6d4"];

type ChartRow = { x: number } & Record<string, number | null | undefined>;

interface TooltipEntry {
	dataKey: string | number;
	value: number | null;
	color?: string;
}

interface CustomTooltipProps {
	active?: boolean;
	payload?: TooltipEntry[];
	label?: number | string;
}

interface ChartClickState {
	activeLabel?: number | string;
}

export interface LineChartProps {
	data: SeriesData[] | null;
	xAxisLabel?: string;
	yAxisLabel?: string;
	fontsize?: number;
	yAxisFormatter?: (value: number | null) => number | null;
	xAxisFormatter?: (value: Date) => string;
	isLoading?: boolean;
	height?: number;
	onPointClick?: (xMs: number) => void;
	selectedX?: number | null;
}

export const LineChart = ({
	data,
	yAxisLabel,
	xAxisLabel,
	fontsize = 14,
	xAxisFormatter = (value: Date): string => toDdMmYyyyHhMm(value),
	yAxisFormatter = (value: number | null): number | null => value,
	isLoading = false,
	height = 400,
	onPointClick,
	selectedX = null,
}: LineChartProps): JSX.Element => {
	const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set());

	if (isLoading) {
		return (
			<div
				style={{
					display: "flex",
					justifyContent: "center",
					alignItems: "center",
					height: height + "px",
				}}
			>
				<LoadingSpinner text="Loading chart data..." size="lg" />
			</div>
		);
	}

	if (!data || data.length === 0 || data.every((series: SeriesData): boolean => series.data.length === 0)) {
		return (
			<div
				className="d-flex flex-column justify-content-center align-items-center text-muted"
				style={{ height: height + "px", width: "100%" }}
			>
				<i className="bi bi-bar-chart-line fs-1 mb-2 opacity-50"></i>
				<p className="mb-1">No data available</p>
				<small>Try adjusting the date range or filters</small>
			</div>
		);
	}

	const toMs = (value: number | string | Date): number => {
		if (value instanceof Date) return value.getTime();
		if (typeof value === "number") return value;
		const parsed: Date = new Date(value);
		return Number.isNaN(parsed.getTime()) ? 0 : parsed.getTime();
	};

	const rowsByX = new Map<number, ChartRow>();
	data.forEach((series: SeriesData): void => {
		series.data.forEach((pt: DataPoint): void => {
			const xMs: number = toMs(pt.x);
			const row: ChartRow = rowsByX.get(xMs) ?? { x: xMs };
			row[series.id] = pt.y;
			rowsByX.set(xMs, row);
		});
	});
	const transformedData: ChartRow[] = Array.from(rowsByX.values()).sort(
		(a: ChartRow, b: ChartRow): number => a.x - b.x
	);

	const handleLegendClick = (e: LegendPayload): void => {
		const seriesId: string = String(e.dataKey);
		setHiddenSeries((prev: Set<string>): Set<string> => {
			const newSet = new Set(prev);
			if (newSet.has(seriesId)) {
				newSet.delete(seriesId);
			} else {
				newSet.add(seriesId);
			}
			return newSet;
		});
	};

	const formatTick = (value: number | string | undefined): string => xAxisFormatter(new Date(value ?? 0));

	const CustomTooltip = ({ active, payload, label }: CustomTooltipProps): JSX.Element | null => {
		if (!active || !payload || !payload.length) return null;
		return (
			<div
				style={{
					backgroundColor: "var(--bs-card-bg)",
					padding: "9px",
					border: "1px solid var(--bs-border-color)",
					borderRadius: "4px",
					boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
				}}
			>
				<p style={{ margin: 0, fontWeight: "bold", color: "var(--bs-body-color)" }}>
					{xAxisLabel ? `${xAxisLabel}: ${formatTick(label)}` : formatTick(label)}
				</p>
				{payload.map((entry: TooltipEntry) => (
					<p key={entry.dataKey} style={{ margin: 0, color: entry.color }}>
						{entry.dataKey}: {Number(entry.value ?? 0).toFixed(2)}
					</p>
				))}
			</div>
		);
	};

	const handleChartClick = (state: ChartClickState): void => {
		if (onPointClick && state && state.activeLabel != null) {
			onPointClick(Number(state.activeLabel));
		}
	};

	return (
		<ResponsiveContainer width={"100%"} height={height}>
			<RechartsLineChart
				data={transformedData}
				margin={{ top: 5, right: 30, left: 8, bottom: 12 }}
				onClick={onPointClick ? handleChartClick : undefined}
				style={onPointClick ? { cursor: "pointer" } : undefined}
			>
				<CartesianGrid strokeDasharray="3 3" stroke="var(--bs-border-color)" />
				{selectedX != null && (
					<ReferenceLine x={selectedX} stroke="var(--bs-primary)" strokeWidth={2} strokeDasharray="4 3" />
				)}
				<XAxis
					dataKey="x"
					type="number"
					scale="time"
					domain={["dataMin", "dataMax"]}
					tickFormatter={formatTick}
					tick={{ fontSize: fontsize, fill: "var(--bs-body-color)" }}
					stroke="var(--bs-border-color)"
				>
					{xAxisLabel && (
						<Label value={xAxisLabel} offset={0} position="insideBottom" fill="var(--bs-body-color)" />
					)}
				</XAxis>
				<YAxis
					tickFormatter={(value: number): string => String(yAxisFormatter(value) ?? "")}
					tick={{ fontSize: fontsize, fill: "var(--bs-body-color)" }}
					stroke="var(--bs-border-color)"
					domain={[0, "auto"]}
				>
					<Label
						value={yAxisLabel}
						angle={-90}
						position="insideLeft"
						style={{ textAnchor: "middle", fill: "var(--bs-body-color)" }}
					/>
				</YAxis>
				<Tooltip content={<CustomTooltip />} />
				<Legend
					onClick={handleLegendClick}
					wrapperStyle={{
						cursor: "pointer",
						color: "var(--bs-body-color)",
					}}
					formatter={(value: string): JSX.Element => (
						<span
							style={{
								color: hiddenSeries.has(value) ? "var(--bs-muted-color)" : "var(--bs-body-color)",
							}}
						>
							{value}
						</span>
					)}
				/>
				{data.map(
					(series: SeriesData, index: number): JSX.Element => (
						<Line
							key={series.id}
							type="monotone"
							dataKey={series.id}
							stroke={series.color ?? CHART_PALETTE[index % CHART_PALETTE.length]}
							hide={hiddenSeries.has(series.id)}
							strokeWidth={2}
							connectNulls
							isAnimationActive={false}
						/>
					)
				)}
			</RechartsLineChart>
		</ResponsiveContainer>
	);
};
