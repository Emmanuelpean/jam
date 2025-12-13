import React, { JSX, useEffect, useState } from "react";
import { PlatformStat, JobScraperServiceLog } from "../../../services/Schemas";
import { SelectOption } from "../../../components/rendering/form/FormOptions";
import { LineChart, SeriesData } from "../../../components/charts/LineChart";
import TimeSelection from "../../../components/TimeSelection/TimeSelection";
import { DateRange } from "../../../utils/TimeUtils";
import Select from "react-select";
import { createSeries } from "../ServiceUtils";

interface RunHistoryChartProps {
	serviceLogData: JobScraperServiceLog[] | null;
	selectedPlatform: string;
	platformOptions: SelectOption[];
	onPlatformChange: (value: string) => void;
	onDateRangeChange: (dateRange: DateRange) => void;
	isRunning: boolean;
}

const successColor = "#22c55e";
const failureColor = "#ef4444";
const infoColor = "#0d38e3";

const getPlatformStat = (log: JobScraperServiceLog, platform: string, key: string): number => {
	const stat: PlatformStat | undefined = log.platform_stats.find((p: PlatformStat): boolean => p.name === platform);
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
	onDateRangeChange,
	isRunning,
}: RunHistoryChartProps): JSX.Element => {
	const [logData, setLogData] = useState<SeriesData[][] | null>(null);

	const handlePlatformChange = (option: SelectOption | null): void => {
		if (option) {
			onPlatformChange(option.value);
		}
	};

	useEffect(() => {
		if (!serviceLogData) return;

		const durationSeries: SeriesData[] = [
			createSeries(serviceLogData, "Run Duration (h)", infoColor, (log: JobScraperServiceLog): number =>
				log.run_duration ? log.run_duration / 3600 : 0,
			),
		];

		if (selectedPlatform === "all") {
			const jobSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					"Successful Jobs",
					successColor,
					(log: JobScraperServiceLog): number => log.job_scrape_succeeded_n,
				),
				createSeries(
					serviceLogData,
					"Failed Jobs",
					failureColor,
					(log: JobScraperServiceLog): number => log.job_scrape_failed_n,
				),
				createSeries(
					serviceLogData,
					"Copied Jobs",
					infoColor,
					(log: JobScraperServiceLog): number => log.job_scrape_copied_n,
				),
				createSeries(
					serviceLogData,
					"Skipped Jobs",
					"#fbbf24",
					(log: JobScraperServiceLog): number => log.job_scrape_skipped_n,
				),
			];
			setLogData([jobSeries, durationSeries]);
		} else {
			const platformSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Found`,
					successColor,
					(log: JobScraperServiceLog): number => getPlatformStat(log, selectedPlatform, "job_found_ids"),
				),
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Scraped`,
					failureColor,
					(log: JobScraperServiceLog): number => getPlatformStat(log, selectedPlatform, "job_scraped_n"),
				),
				createSeries(
					serviceLogData,
					`${selectedPlatform} Failed`,
					infoColor,
					(log: JobScraperServiceLog): number => getPlatformStat(log, selectedPlatform, "job_failed_n"),
				),
			];
			setLogData([platformSeries, durationSeries]);
		}
	}, [serviceLogData, selectedPlatform]);

	const selectedOption: SelectOption | undefined = platformOptions.find(
		(opt: SelectOption): boolean => opt.value === selectedPlatform,
	);

	return (
		<div className="status-card mt-4">
			<h2 className="card-title">
				<i className="bi bi-clock-history me-2"></i>
				Run History
				{isRunning && <span className="live-indicator ms-2"></span>}
			</h2>
			<div style={{ display: "flex", justifyContent: "space-between" }}>
				<TimeSelection onDateRangeChange={onDateRangeChange} defaultMode="period" />
				<div className="mb-4">
					<div style={{ minWidth: "250px" }}>
						<Select
							classNamePrefix="react-select"
							value={selectedOption}
							onChange={handlePlatformChange}
							options={platformOptions}
							isSearchable={false}
						/>
					</div>
				</div>
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
