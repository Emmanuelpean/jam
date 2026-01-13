import React, { JSX, useEffect, useState } from "react";
import { JobRatingServiceLogData } from "../../../services/schemas/Services";
import { LineChart, SeriesData } from "../../../components/charts/LineChart";
import TimeSelection from "../../../components/TimeSelection/TimeSelection";
import { DateRange } from "../../../utils/TimeUtils";
import { createSeries, failureColor, infoColor, successColor } from "../ServiceUtils";

interface RunHistoryChartProps {
	serviceLogData: JobRatingServiceLogData[] | null;
	onDateRangeChange: (dateRange: DateRange) => void;
	isRunning: boolean;
}

export const RunHistoryChart = ({
	serviceLogData,
	onDateRangeChange,
	isRunning,
}: RunHistoryChartProps): JSX.Element => {
	const [logData, setLogData] = useState<SeriesData[][] | null>(null);

	useEffect(() => {
		if (!serviceLogData) return;

		const durationSeries: SeriesData[] = [
			createSeries(serviceLogData, "Run Duration (h)", infoColor, (log: JobRatingServiceLogData): number =>
				log.run_duration ? log.run_duration / 3600 : 0,
			),
		];

		const jobSeries: SeriesData[] = [
			createSeries(
				serviceLogData,
				"Successful Jobs",
				successColor,
				(log: JobRatingServiceLogData): number => log.rated_job_succeeded_ids.length,
			),
			createSeries(
				serviceLogData,
				"Failed Jobs",
				failureColor,
				(log: JobRatingServiceLogData): number => log.rated_job_failed_ids.length,
			),
		];
		setLogData([jobSeries, durationSeries]);
	}, [serviceLogData]);

	return (
		<div className="status-card mt-4">
			<h2 className="card-title">
				<i className="bi bi-clock-history me-2"></i>
				Run History
				{isRunning && <span className="live-indicator ms-2"></span>}
			</h2>
			<div style={{ display: "flex", justifyContent: "space-between" }}>
				<TimeSelection onDateRangeChange={onDateRangeChange} defaultMode="period" />
			</div>
			<div style={{ display: "flex" }}>
				{logData && logData[0] && (
					<LineChart data={logData[0]} xAxisLabel="Run date" yAxisLabel="Number of jobs rated" />
				)}
				{logData && logData[1] && (
					<LineChart data={logData[1]} xAxisLabel="Run date" yAxisLabel="Run duration [h]" />
				)}
			</div>
		</div>
	);
};
