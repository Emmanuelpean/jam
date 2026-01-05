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
import LoadingSpinner from "../spinner/Spinner";

interface DataPoint {
	x: number | string | Date;
	y: number | null;
}

export interface SeriesData {
	id: string;
	color?: string;
	data: DataPoint[];
}

export interface LineChartProps {
	data: SeriesData[] | null;
	xAxisLabel?: string;
	yAxisLabel?: string;
	fontsize?: number;
	yAxisFormatter?: (value: number | null) => number | null;
	xAxisFormatter?: (value: string | Date) => string;
	isLoading?: boolean;
	height?: number;
}

export const LineChart = ({
	data,
	yAxisLabel = "Y-axis",
	xAxisLabel = "X-Axis",
	fontsize = 14,
	xAxisFormatter = (value: string | Date): string => toDdMmYyyyHhMm(value),
	yAxisFormatter = (value: number | null): number | null => value,
	isLoading = false,
	height = 400,
}: LineChartProps): JSX.Element => {
	const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set());

	if (isLoading) {
		return (
			<div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: height + "px" }}>
				<LoadingSpinner text="Loading chart data..." size="lg" />
			</div>
		);
	}

	if (!data || data.length === 0 || data[0]?.data.length === 0) {
		return (
			<div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: height + "px" }}>
				<p>No data available.</p>
			</div>
		);
	}

	const transformedData =
		data[0]?.data.map((_, index) => {
			const point: Record<string, any> = {
				x: data[0]!.data[index]!.x,
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

	const CustomTooltip = ({ active, payload, label }: any) => {
		if (!active || !payload || !payload.length) return null;
		return (
			<div style={{ backgroundColor: "white", padding: "10px", border: "1px solid #ccc" }}>
				<p style={{ margin: 0, fontWeight: "bold" }}>
					{xAxisLabel}: {xAxisFormatter(label)}
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
		<ResponsiveContainer width="100%" height={height}>
			<RechartsLineChart data={transformedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis dataKey="x" tickFormatter={(value) => xAxisFormatter(value)} tick={{ fontSize: fontsize }}>
					<Label value={xAxisLabel} offset={-5} position="insideBottom" />
				</XAxis>
				<YAxis
					tickFormatter={(value) => String(yAxisFormatter(value) ?? "")}
					tick={{ fontSize: fontsize }}
					domain={[0, "auto"]}
				>
					<Label value={yAxisLabel} angle={-90} position="insideLeft" style={{ textAnchor: "middle" }} />
				</YAxis>
				<Tooltip content={<CustomTooltip />} />
				<Legend
					onClick={handleLegendClick}
					wrapperStyle={{ cursor: "pointer" }}
					formatter={(value) => (
						<span style={{ color: hiddenSeries.has(value) ? "#ccc" : "inherit" }}>{value}</span>
					)}
				/>
				{data.map((series) => (
					<Line
						key={series.id}
						type="monotone"
						dataKey={series.id}
						stroke={series.color}
						hide={hiddenSeries.has(series.id)}
						strokeWidth={2}
					/>
				))}
			</RechartsLineChart>
		</ResponsiveContainer>
	);
};
