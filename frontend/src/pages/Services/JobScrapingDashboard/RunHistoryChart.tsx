import React, { JSX, useEffect, useState } from "react";
import { JobScrapingServiceLogData, PlatformStat } from "../../../services/schemas/Services";
import { SelectOption } from "../../../components/rendering/form/FormOptions";
import { LineChart, SeriesData } from "../../../components/Chart/LineChart";
import { createSeries, failureColor, successColor } from "../ServiceUtils";
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
			createSeries(serviceLogData, "Run Duration (h)", (log: JobScrapingServiceLogData): number =>
				log.run_duration ? log.run_duration / 3600 : 0
			),
		];

		if (selectedPlatform === "all") {
			const jobSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					"Successful Jobs",
					(log: JobScrapingServiceLogData): number => log.job_scrape_succeeded_n,
					successColor
				),
				createSeries(
					serviceLogData,
					"Failed Jobs",
					(log: JobScrapingServiceLogData): number => log.job_scrape_failed_n,
					failureColor
				),
				createSeries(
					serviceLogData,
					"Copied Jobs",
					(log: JobScrapingServiceLogData): number => log.job_scrape_copied_n
				),
				createSeries(
					serviceLogData,
					"Skipped Jobs",
					(log: JobScrapingServiceLogData): number => log.job_scrape_skipped_n
				),
			];
			setLogData([jobSeries, durationSeries]);
		} else {
			const platformSeries: SeriesData[] = [
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Found`,
					(log: JobScrapingServiceLogData): number => getPlatformStat(log, selectedPlatform, "job_found_ids")
				),
				createSeries(
					serviceLogData,
					`${selectedPlatform} Jobs Scraped`,
					(log: JobScrapingServiceLogData): number => getPlatformStat(log, selectedPlatform, "job_scraped_n")
				),
				createSeries(
					serviceLogData,
					`${selectedPlatform} Failed`,
					(log: JobScrapingServiceLogData): number => getPlatformStat(log, selectedPlatform, "job_failed_n"),
					failureColor
				),
			];
			setLogData([platformSeries, durationSeries]);
		}
	}, [serviceLogData, selectedPlatform]);

	const platformField: ModalFormField = {
		key: "platform",
		type: "select",
		label: "Platform",
		options: platformOptions,
		isClearable: false,
		size: "sm",
		fitContentWidth: true,
	};

	return (
		<div className="status-card mt-4">
			<div className="history-chart-header d-flex justify-content-between align-items-center">
				<h2 className="card-title mb-0">
					<i className="bi bi-clock-history me-2"></i>
					Run History
					{isRunning && <span className="live-indicator ms-2"></span>}
				</h2>
				<div className="history-chart-controls">
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
						<LineChart data={logData[0]} xAxisLabel="Run date" yAxisLabel="Number of job alerts" />
					)}
					{logData && logData[1] && (
						<LineChart data={logData[1]} xAxisLabel="Run date" yAxisLabel="Run duration [h]" />
					)}
				</div>
			)}
		</div>
	);
};
