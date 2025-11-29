import { JSX, useState } from "react";
import {
	LineChart as RechartsLineChart,
	Line,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	Legend,
	ResponsiveContainer,
	Label,
} from "recharts";
import { toDdMmYyyyHhMm } from "../../utils/TimeUtils";

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
}

export const LineChart = ({
	data,
	yAxisLabel = "Y-axis",
	xAxisLabel = "X-Axis",
	fontsize = 14,
	xAxisFormatter = (value) => toDdMmYyyyHhMm(value),
	yAxisFormatter = (value) => value,
}: LineChartProps): JSX.Element => {
	const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set());

	if (!data) return <div>No data available</div>;

	// Transform data from Nivo format to Recharts format
	const transformedData =
		data[0]?.data.map((_, index) => {
			const point: Record<string, any> = {
				// @ts-ignore
				x: data[0].data[index].x,
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
			<div
				style={{
					background: "white",
					padding: "9px 12px",
					border: "1px solid #ccc",
					borderRadius: "4px",
					fontSize: `${fontsize}px`,
				}}
			>
				<div>
					<strong>{xAxisLabel}:</strong> {xAxisFormatter(label)}
				</div>
				{payload.map((entry: any) => (
					<div key={entry.dataKey} style={{ color: entry.color }}>
						<strong>{entry.dataKey}:</strong> {Number(entry.value ?? 0).toFixed(2)}
					</div>
				))}
			</div>
		);
	};

	return (
		<div style={{ height: "400px", width: "100%" }}>
			<ResponsiveContainer width="100%" height="100%">
				<RechartsLineChart data={transformedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
					<CartesianGrid strokeDasharray="3 3" />
					<XAxis dataKey="x" tickFormatter={(value) => xAxisFormatter(value)} tick={{ fontSize: fontsize }}>
						<Label
							value={xAxisLabel}
							position="insideBottom"
							offset={-10}
							style={{ fontSize: fontsize + 2 }}
						/>
					</XAxis>
					<YAxis
						tickFormatter={(value) => String(yAxisFormatter(value) ?? "")}
						tick={{ fontSize: fontsize }}
						domain={[0, "auto"]}
					>
						<Label
							value={yAxisLabel}
							angle={-90}
							position="insideLeft"
							style={{ textAnchor: "middle", fontSize: fontsize + 2 }}
						/>
					</YAxis>
					<Tooltip content={<CustomTooltip />} />
					<Legend
						onClick={handleLegendClick}
						wrapperStyle={{ fontSize: `${fontsize}px`, cursor: "pointer", paddingTop: "20px" }}
						formatter={(value: string) => (
							<span style={{ opacity: hiddenSeries.has(value) ? 0.5 : 1 }}>{value}</span>
						)}
					/>
					{data.map((series) => (
						<Line
							key={series.id}
							type="monotone"
							dataKey={series.id}
							stroke={series.color || "#8884d8"}
							strokeWidth={3}
							dot={{ r: 5 }}
							activeDot={{ r: 7 }}
							hide={hiddenSeries.has(series.id)}
						/>
					))}
				</RechartsLineChart>
			</ResponsiveContainer>
		</div>
	);
};
