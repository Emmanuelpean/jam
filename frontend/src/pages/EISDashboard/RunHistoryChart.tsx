import React, { JSX, useEffect, useState } from "react";
import { ServiceLog } from "../../services/Schemas";
import { SelectOption } from "../../components/rendering/form/FormOptions";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { LineChart, SeriesData } from "../../components/charts/LineChart";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { RenderSelect } from "../../components/rendering/widgets/SelectWidget";

interface RunHistoryChartProps {
	serviceLogData: ServiceLog[] | null;
	selectedPlatform: string;
	platformOptions: SelectOption[];
	onPlatformChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void;
	isRunning: boolean;
}

const successColor = "#22c55e";
const failureColor = "#ef4444";
const infoColor = "#0d38e3";

const createSeries = (
	logs: ServiceLog[],
	id: string,
	color: string,
	getValue: (log: ServiceLog) => number,
): SeriesData => ({
	id,
	color,
	data: logs
		.slice()
		.reverse()
		.map((log) => ({
			x: new Date(log.run_datetime),
			y: getValue(log),
		})),
});

const getPlatformStat = (log: ServiceLog, platform: string, key: string): number => {
	const stat = log.platform_stats.find((p) => p.name === platform);
	if (!stat) return 0;

	const value = (stat as any)[key];

	if (Array.isArray(value)) {
		return value.length;
	}

	if (typeof value === "string") {
		const parsed = Number(value);
		return isNaN(parsed) ? 0 : parsed;
	}

	return typeof value === "number" ? value : 0;
};

export const RunHistoryChart = ({
	serviceLogData,
	selectedPlatform,
	platformOptions,
	onPlatformChange,
	isRunning,
}: RunHistoryChartProps): JSX.Element => {
	const [logData, setLogData] = useState<SeriesData[][] | null>(null);

	useEffect(() => {
		if (!serviceLogData) return;
		// Prepare data for charts
		const durationSeries: SeriesData[] = [
			createSeries(serviceLogData, "Run Duration (h)", infoColor, (log: ServiceLog): number =>
				log.run_duration ? log.run_duration / 3600 : 0,
			),
		];
		if (selectedPlatform === "all") {
			// Show service-level data
			const jobSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					"Successful Jobs",
					successColor,
					(log: ServiceLog): number => log.job_scrape_succeeded_n,
				),
				createSeries(
					serviceLogData,
					"Failed Jobs",
					failureColor,
					(log: ServiceLog): number => log.job_scrape_failed_n,
				),
				createSeries(
					serviceLogData,
					"Copied Jobs",
					infoColor,
					(log: ServiceLog): number => log.job_scrape_copied_n,
				),
			];
			setLogData([jobSeries, durationSeries]);
		} else {
			// Show platform-specific data
			const platformSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Found`,
					successColor,
					(log: ServiceLog): number => getPlatformStat(log, selectedPlatform, "job_found_ids"),
				),
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Scraped`,
					failureColor,
					(log: ServiceLog): number => getPlatformStat(log, selectedPlatform, "job_scraped_n"),
				),
				createSeries(serviceLogData, `${selectedPlatform} Failed`, infoColor, (log: ServiceLog): number =>
					getPlatformStat(log, selectedPlatform, "job_failed_n"),
				),
			];
			setLogData([platformSeries, durationSeries]);
		}
	}, [serviceLogData, selectedPlatform]);

	const platformField: ModalFormField = {
		name: "platform-select",
		type: "select",
		label: "Select Platform",
		options: platformOptions,
	};

	return (
		<div className="status-card mt-4">
			<h2 className="card-title">
				<i className="bi bi-clock-history me-2"></i>
				Run History
				{isRunning && <span className="live-indicator ms-2"></span>}
			</h2>
			<div className="mb-4">
				<RenderSelect field={platformField} value={selectedPlatform} handleChange={onPlatformChange} />
			</div>
			<div style={{ display: "flex" }}>
				{logData && logData[0] && (
					<LineChart data={logData[0]} xAxisLabel="Run date" yAxisLabel="Number of scraped jobs" />
				)}
				{logData && logData[1] && (
					<LineChart data={logData[1]} xAxisLabel="Run date" yAxisLabel="Run duration [h]" />
				)}
			</div>
		</div>
	);
};
