export const chartTheme = {
	fontSize: 14,
	fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
	textColor: "#2d3748",
	background: "transparent",
	grid: {
		line: {
			stroke: "#e2e8f0",
			strokeWidth: 1,
		},
	},
	axis: {
		domain: {
			line: {
				stroke: "#cbd5e0",
				strokeWidth: 2,
			},
		},
		ticks: {
			line: {
				stroke: "#cbd5e0",
				strokeWidth: 1,
			},
			text: {
				fontSize: 13,
				fontWeight: 500,
				fill: "#4a5568",
			},
		},
		legend: {
			text: {
				fontSize: 15,
				fontWeight: 600,
				fill: "#2d3748",
			},
		},
	},
	tooltip: {
		container: {
			background: "#ffffff",
			color: "#2d3748",
			fontSize: 13,
			borderRadius: 8,
			boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
			border: "1px solid #e2e8f0",
		},
	},
};

// Chart configurations
export const lineChartProps = {
	theme: chartTheme,
	margin: { top: 30, right: 30, bottom: 70, left: 80 },
	xScale: { type: "point" },
	yScale: { type: "linear", min: 0, max: "auto" },
	curve: "monotoneX",
	axisBottom: {
		tickSize: 8,
		tickPadding: 8,
		tickRotation: -45,
		legend: "Time Period",
		legendPosition: "middle",
		legendOffset: 55,
	},
	axisLeft: {
		tickSize: 8,
		tickPadding: 8,
		tickRotation: 0,
		legend: "Average Duration (seconds)",
		legendPosition: "middle",
		legendOffset: -60,
	},
	pointSize: 8,
	pointColor: "#ffffff",
	pointBorderWidth: 2,
	pointBorderColor: { from: "serieColor" },
	useMesh: true,
	animate: true,
	motionConfig: { mass: 1, tension: 120, friction: 14 },
	lineWidth: 3,
	enableGridY: true,
};

export const barChartProps = {
	keys: ["successful", "failed"],
	indexBy: "period",
	theme: chartTheme,
	margin: { top: 30, right: 110, bottom: 70, left: 80 },
	padding: 0.3,
	colors: ["#27ae60", "#e74c3c"],
	borderRadius: 4,
	axisBottom: {
		tickSize: 8,
		tickPadding: 8,
		tickRotation: -45,
		legend: "Time Period",
		legendPosition: "middle",
		legendOffset: 55,
	},
	axisLeft: {
		tickSize: 8,
		tickPadding: 8,
		tickRotation: 0,
		legend: "Number of Runs",
		legendPosition: "middle",
		legendOffset: -60,
	},
	enableLabel: true,
	labelSkipWidth: 12,
	labelSkipHeight: 12,
	labelTextColor: "#ffffff",
	animate: true,
	motionConfig: { mass: 1, tension: 120, friction: 14 },
	enableGridY: true,
	legends: [
		{
			dataFrom: "keys",
			anchor: "bottom-right",
			direction: "column",
			justify: false,
			translateX: 100,
			translateY: 0,
			itemsSpacing: 2,
			itemWidth: 80,
			itemHeight: 20,
			itemTextColor: "#2d3748",
			symbolSize: 12,
		},
	],
};
