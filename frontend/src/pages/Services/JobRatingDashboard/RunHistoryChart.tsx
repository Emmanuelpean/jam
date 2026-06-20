import React, { JSX, useEffect, useState } from "react";
import { JobRatingServiceLogData } from "../../../services/schemas/Services";
import { LineChart, SeriesData } from "../../../components/Chart/LineChart";
import { createSeries, failureColor, successColor } from "../ServiceUtils";
import { useDelayedLoading } from "../../../hooks/useDelayedLoading";

interface RunHistoryChartProps {
	serviceLogData: JobRatingServiceLogData[] | null;
	isRunning: boolean;
	loading?: boolean;
}

export const RunHistoryChart = ({ serviceLogData, isRunning, loading = false }: RunHistoryChartProps): JSX.Element => {
	const visibleLoading: boolean = useDelayedLoading(loading);
	const [logData, setLogData] = useState<SeriesData[][] | null>(null);

	useEffect(() => {
		if (!serviceLogData) return;

		const durationSeries: SeriesData[] = [
			createSeries(serviceLogData, "Run Duration (h)", (log: JobRatingServiceLogData): number =>
				log.run_duration ? log.run_duration / 3600 : 0
			),
		];

		const jobSeries: SeriesData[] = [
			createSeries(
				serviceLogData,
				"Successful Jobs",
				(log: JobRatingServiceLogData): number => log.job_succeeded_ids.length,
				successColor
			),
			createSeries(
				serviceLogData,
				"Failed Jobs",
				(log: JobRatingServiceLogData): number => log.job_failed_ids.length,
				failureColor
			),
			createSeries(
				serviceLogData,
				"Skipped Jobs",
				(log: JobRatingServiceLogData): number => log.job_skipped_ids.length
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
			{visibleLoading ? (
				<div className="d-flex justify-content-center align-items-center" style={{ minHeight: "270px" }}>
					<div className="spinner-border text-primary" role="status">
						<span className="visually-hidden">Loading...</span>
					</div>
				</div>
			) : (
				<div style={{ display: "flex" }}>
					{logData && logData[0] && (
						<LineChart data={logData[0]} xAxisLabel="Run date" yAxisLabel="Number of jobs rated" />
					)}
					{logData && logData[1] && (
						<LineChart data={logData[1]} xAxisLabel="Run date" yAxisLabel="Run duration [h]" />
					)}
				</div>
			)}
		</div>
	);
};
