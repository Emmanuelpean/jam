import React, { JSX, useEffect, useState } from "react";
import { JobScrapingServiceLogData, PlatformStat } from "../../../services/schemas/Services";
import { SelectOption } from "../../../components/rendering/form/FormOptions";
import { LineChart, SeriesData } from "../../../components/Chart/LineChart";
import { createSeries } from "../ServiceUtils";
import { ModalFormField } from "../../../components/rendering/form/FormRenders";
import { SelectInput } from "../../../components/rendering/widgets/SelectWidget";
import { useDelayedLoading } from "../../../hooks/useDelayedLoading";

interface RunHistoryChartProps {
	serviceLogData: JobScrapingServiceLogData[] | null;
	selectedPlatform: string;
	platformOptions: SelectOption[];
	onPlatformChange: (value: string) => void;
	isRunning: boolean;
	loading?: boolean;
}

const successColor = "#22c55e";
const failureColor = "#ef4444";
const infoColor = "#0d38e3";

const getPlatformStat = (log: JobScrapingServiceLogData, platform: string, key: string): number => {
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
	isRunning,
	loading = false,
}: RunHistoryChartProps): JSX.Element => {
	const visibleLoading = useDelayedLoading(loading);
	const [logData, setLogData] = useState<SeriesData[][] | null>(null);

	useEffect(() => {
		if (!serviceLogData) return;

		const durationSeries: SeriesData[] = [
			createSeries(serviceLogData, "Run Duration (h)", infoColor, (log: JobScrapingServiceLogData): number =>
				log.run_duration ? log.run_duration / 3600 : 0
			),
		];

		if (selectedPlatform === "all") {
			const jobSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					"Successful Jobs",
					successColor,
					(log: JobScrapingServiceLogData): number => log.job_scrape_succeeded_n
				),
				createSeries(
					serviceLogData,
					"Failed Jobs",
					failureColor,
					(log: JobScrapingServiceLogData): number => log.job_scrape_failed_n
				),
				createSeries(
					serviceLogData,
					"Copied Jobs",
					infoColor,
					(log: JobScrapingServiceLogData): number => log.job_scrape_copied_n
				),
				createSeries(
					serviceLogData,
					"Skipped Jobs",
					"#fbbf24",
					(log: JobScrapingServiceLogData): number => log.job_scrape_skipped_n
				),
			];
			setLogData([jobSeries, durationSeries]);
		} else {
			const platformSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Found`,
					successColor,
					(log: JobScrapingServiceLogData): number => getPlatformStat(log, selectedPlatform, "job_found_ids")
				),
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Scraped`,
					failureColor,
					(log: JobScrapingServiceLogData): number => getPlatformStat(log, selectedPlatform, "job_scraped_n")
				),
				createSeries(
					serviceLogData,
					`${selectedPlatform} Failed`,
					infoColor,
					(log: JobScrapingServiceLogData): number => getPlatformStat(log, selectedPlatform, "job_failed_n")
				),
			];
			setLogData([platformSeries, durationSeries]);
		}
	}, [serviceLogData, selectedPlatform]);

	const platformField: ModalFormField = {
		name: "platform",
		type: "select",
		label: "Platform",
		options: platformOptions,
		isClearable: false,
	};

	return (
		<div className="status-card mt-4">
			<div className="d-flex justify-content-between align-items-center mb-3">
				<h2 className="card-title mb-0">
					<i className="bi bi-clock-history me-2"></i>
					Run History
					{isRunning && <span className="live-indicator ms-2"></span>}
				</h2>
				<div style={{ minWidth: "225px" }}>
					<SelectInput
						field={platformField}
						value={selectedPlatform}
						error={null}
						handleChange={(event: any) => {
							onPlatformChange(event.target.value);
						}}
					/>
				</div>
			</div>
			{visibleLoading ? (
				<div className="d-flex justify-content-center align-items-center" style={{ minHeight: "270px" }}>
					<div className="spinner-border text-primary" role="status">
						<span className="visually-hidden">Loading...</span>
					</div>
				</div>
			) : (
				<div style={{ display: "flex" }}>
					{logData && logData[0] && (
						<LineChart data={logData[0]} xAxisLabel="Run date" yAxisLabel="Number of scraped jobs" />
					)}
					{logData && logData[1] && (
						<LineChart data={logData[1]} xAxisLabel="Run date" yAxisLabel="Run duration [h]" />
					)}
				</div>
			)}
		</div>
	);
};
