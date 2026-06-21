import { JSX } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import "./Sparkline.scss";

export interface SparklinePoint {
	x: Date | string | number;
	y: number;
}

interface SparklineProps {
	data: SparklinePoint[];
	color?: string;
	height?: number;
	loading?: boolean;
	valueFormatter?: (y: number) => string;
	/** Let the Y-axis go below zero (e.g. a balance). Otherwise it starts at 0. */
	allowNegative?: boolean;
}

const toMs = (value: Date | string | number): number => {
	if (value instanceof Date) return value.getTime();
	if (typeof value === "number") return value;
	const parsed: Date = new Date(value);
	return Number.isNaN(parsed.getTime()) ? 0 : parsed.getTime();
};

const formatDate = (value: Date): string => value.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });

export const Sparkline = ({
	data,
	color = "var(--bs-primary)",
	height = 130,
	loading = false,
	valueFormatter = (y: number): string => String(y),
	allowNegative = false,
}: SparklineProps): JSX.Element => {
	if (loading) {
		return (
			<div className="sparkline-empty" style={{ height }}>
				<span className="spinner-border spinner-border-sm text-secondary" role="status" />
			</div>
		);
	}

	if (data.length === 0) {
		return (
			<div className="sparkline-empty text-muted" style={{ height }}>
				No data
			</div>
		);
	}

	const chartData = data.map((p: SparklinePoint) => ({ x: toMs(p.x), y: p.y }));

	const SparklineTooltip = ({ active, payload, label }: any): JSX.Element | null => {
		if (!active || !payload?.length) return null;
		return (
			<div className="sparkline-tooltip">
				<span className="sparkline-tooltip-label">{formatDate(new Date(label))}</span>
				<span className="sparkline-tooltip-value">{valueFormatter(payload[0].value ?? 0)}</span>
			</div>
		);
	};

	return (
		<ResponsiveContainer width="100%" height={height}>
			<LineChart data={chartData} margin={{ top: 6, right: 10, bottom: 2, left: 0 }}>
				<CartesianGrid strokeDasharray="3 3" stroke="var(--bs-border-color)" />
				<XAxis
					dataKey="x"
					type="number"
					scale="time"
					domain={["dataMin", "dataMax"]}
					tickFormatter={(v: number): string => formatDate(new Date(v))}
					tick={{ fontSize: 10, fill: "var(--bs-body-color)" }}
					stroke="var(--bs-border-color)"
					minTickGap={24}
				/>
				<YAxis
					tickFormatter={(v: number): string => valueFormatter(v)}
					tick={{ fontSize: 10, fill: "var(--bs-body-color)" }}
					stroke="var(--bs-border-color)"
					width={48}
					domain={allowNegative ? ["auto", "auto"] : [0, "auto"]}
				/>
				<Tooltip content={<SparklineTooltip />} cursor={{ stroke: "var(--bs-border-color)", strokeWidth: 1 }} />
				<Line
					type="monotone"
					dataKey="y"
					stroke={color}
					strokeWidth={2}
					dot={false}
					isAnimationActive={false}
				/>
			</LineChart>
		</ResponsiveContainer>
	);
};
