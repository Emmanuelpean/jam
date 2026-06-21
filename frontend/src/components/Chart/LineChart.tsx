import { JSX, useState } from "react";

import {
	CartesianGrid,
	Label,
	Legend,
	Line,
	LineChart as RechartsLineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
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

export interface LineChartProps {
	data: SeriesData[] | null;
	xAxisLabel?: string;
	yAxisLabel?: string;
	fontsize?: number;
	yAxisFormatter?: (value: number | null) => number | null;
	xAxisFormatter?: (value: Date) => string;
	isLoading?: boolean;
	height?: number;
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

	if (!data || data.length === 0 || data[0]?.data.length === 0) {
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

	const transformedData =
		data[0]?.data.map((_, index) => {
			const point: Record<string, any> = {
				x: toMs(data[0]!.data[index]!.x),
			};
			data.forEach((series) => {
				point[series.id] = series.data[index]?.y;
			});
			return point;
		}) || [];

	const handleLegendClick = (e: any): void => {
		const seriesId = e.dataKey;
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

	const formatTick = (value: any): string => xAxisFormatter(new Date(value));

	const CustomTooltip = ({ active, payload, label }: any) => {
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
					{xAxisLabel}: {formatTick(label)}
				</p>
				{payload.map((entry: any) => (
					<p key={entry.dataKey} style={{ margin: 0, color: entry.color }}>
						{entry.dataKey}: {Number(entry.value ?? 0).toFixed(2)}
					</p>
				))}
			</div>
		);
	};

	return (
		<ResponsiveContainer width={"100%"} height={height}>
			<RechartsLineChart data={transformedData} margin={{ top: 5, right: 30, left: 8, bottom: 12 }}>
				<CartesianGrid strokeDasharray="3 3" stroke="var(--bs-border-color)" />
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
					tickFormatter={(value) => String(yAxisFormatter(value) ?? "")}
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
					formatter={(value) => (
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
							isAnimationActive={false}
						/>
					)
				)}
			</RechartsLineChart>
		</ResponsiveContainer>
	);
};
