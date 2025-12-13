import React, { JSX } from "react";
import { Table } from "react-bootstrap";
import { PlatformStat, JobScraperServiceLog } from "../../../services/Schemas";

import { capitalise } from "../../../utils/StringUtils";

interface PlatformStatsTableProps {
	platformStats: PlatformStat[];
	latestLog: JobScraperServiceLog;
}

const getPlatformStat = (log: JobScraperServiceLog, platform: string, key: string): number => {
	const stat: PlatformStat | undefined = log.platform_stats.find((p: PlatformStat): boolean => p.name === platform);
	if (!stat) return 0;

	const value = (stat as any)[key];

	if (Array.isArray(value)) {
		return value.length;
	}

	if (typeof value === "string") {
		const parsed: number = Number(value);
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
				{platformStats.map(
					(platformStat: PlatformStat): JSX.Element => (
						<tr key={platformStat.name}>
							<td>{capitalise(platformStat.name)}</td>
							<td>{getPlatformStat(latestLog, platformStat.name, "job_found_ids")}</td>
							<td>{getPlatformStat(latestLog, platformStat.name, "job_scrape_succeeded_ids")}</td>
							<td>{getPlatformStat(latestLog, platformStat.name, "job_scrape_failed_ids")}</td>
							<td>{getPlatformStat(latestLog, platformStat.name, "job_scrape_skipped_ids")}</td>
						</tr>
					),
				)}
			</tbody>
		</Table>
	);
};
