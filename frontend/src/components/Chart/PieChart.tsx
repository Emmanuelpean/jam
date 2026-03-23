import { JSX, useState } from "react";
import {
	PieChart as RechartsPieChart,
	Pie,
	Cell,
	Legend,
	ResponsiveContainer,
	Tooltip,
} from "recharts";

export interface PieDataPoint {
	name: string;
	value: number;
	[key: string]: string | number;
}

export interface PieChartProps {
	data: PieDataPoint[];
	colors: string[];
	fontSize?: number;
	suffix?: string;
}

const PieTooltip = ({ active, payload, suffix = "" }: any) => {
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
			<p style={{ margin: 0, fontWeight: 600, color: "var(--bs-body-color)" }}>{entry.name}</p>
			<p style={{ margin: 0, color: entry.payload?.fill ?? "var(--bs-body-color)" }}>{entry.value}{suffix}</p>
		</div>
	);
};

export const PieChart = ({ data, colors, fontSize = 13, suffix = "" }: PieChartProps): JSX.Element => {
	const [hiddenSlices, setHiddenSlices] = useState<Set<string>>(new Set());

	const handleLegendClick = (e: any): void => {
		const name = e.value;
		setHiddenSlices((prev) => {
			const next = new Set(prev);
			if (next.has(name)) next.delete(name);
			else next.add(name);
			return next;
		});
	};

	// Keep all data but zero out hidden slices so legend entries persist
	const chartData = data.map((d) => (hiddenSlices.has(d.name) ? { ...d, value: 0 } : d));

	return (
		<ResponsiveContainer width="100%" height="100%">
			<RechartsPieChart>
				<Pie
					data={chartData}
					dataKey="value"
					nameKey="name"
					cx="50%"
					cy="45%"
					outerRadius="70%"
					label={({ name, percent, value }) => {
						if (!name || hiddenSlices.has(name) || value === 0) return "";
						return `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`;
					}}
					labelLine={({ payload }) => {
						if (!payload?.name || hiddenSlices.has(payload.name)) return <line stroke="none" />;
						return <line stroke="var(--bs-body-color)" />;
					}}
					fontSize={fontSize}
				>
					{chartData.map((d, i) => (
						<Cell
							key={d.name}
							fill={colors[i % colors.length]}
							fillOpacity={hiddenSlices.has(d.name) ? 0 : 1}
							stroke={hiddenSlices.has(d.name) ? "none" : undefined}
						/>
					))}
				</Pie>
				<Tooltip content={<PieTooltip suffix={suffix} />} />
				<Legend
					onClick={handleLegendClick}
					wrapperStyle={{
						cursor: "pointer",
						color: "var(--bs-body-color)",
						fontSize,
					}}
					formatter={(value) => (
						<span
							style={{
								color: hiddenSlices.has(value as string) ? "var(--bs-muted-color)" : "var(--bs-body-color)",
							}}
						>
							{value}
						</span>
					)}
				/>
			</RechartsPieChart>
		</ResponsiveContainer>
	);
};
