import React, { JSX } from "react";
import { Table } from "react-bootstrap";
import { PlatformStat, ServiceLog } from "../../services/Schemas";
import { capitalise } from "../../utils/Utils";

interface PlatformStatsTableProps {
	platformStats: PlatformStat[];
	latestLog: ServiceLog;
}

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

export const PlatformStatsTable = ({ platformStats, latestLog }: PlatformStatsTableProps): JSX.Element => {
	return (
		<Table striped bordered hover size="sm">
			<thead>
				<tr>
					<th>Platform</th>
					<th>Found</th>
					<th>Succeeded</th>
					<th>Failed</th>
					<th>Skipped</th>
				</tr>
			</thead>
			<tbody>
				{platformStats.map((platformStat: PlatformStat) => (
					<tr key={platformStat.name}>
						<td>{capitalise(platformStat.name)}</td>
						<td>{getPlatformStat(latestLog, platformStat.name, "job_found_ids")}</td>
						<td>{getPlatformStat(latestLog, platformStat.name, "job_scrape_succeeded_ids")}</td>
						<td>{getPlatformStat(latestLog, platformStat.name, "job_scrape_failed_ids")}</td>
						<td>{getPlatformStat(latestLog, platformStat.name, "job_scrape_skipped_ids")}</td>
					</tr>
				))}
			</tbody>
		</Table>
	);
};
