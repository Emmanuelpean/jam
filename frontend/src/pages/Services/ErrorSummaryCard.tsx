import React, { JSX, useState } from "react";
import { ServiceError } from "../../services/schemas/Services";
import { groupErrorsByMessage } from "../../hooks/useServiceErrors";
import { useDelayedLoading } from "../../hooks/useDelayedLoading";
import { GroupedErrorList } from "./GroupedErrorList";

type ErrorView = "current" | "last";

export interface ErrorGroupData {
	errors: ServiceError[];
	acknowledge: (ids: number[]) => Promise<void>;
	platformByJobId?: Record<number, string | null>;
}

export interface PerJobErrorConfig {
	title: string;
	discriminatorKey: "scraped_job_id" | "job_rating_id";
	emptyText: string;
	showJobs?: boolean;
}

interface ErrorSummaryCardProps {
	current: ErrorGroupData;
	previous: ErrorGroupData;
	showAcknowledged: boolean;
	onToggleAcknowledged: (value: boolean) => void;
	isRunning: boolean;
	loading?: boolean;
	perJob?: PerJobErrorConfig;
}

export const ErrorSummaryCard = ({
	current,
	previous,
	showAcknowledged,
	onToggleAcknowledged,
	isRunning,
	loading = false,
	perJob,
}: ErrorSummaryCardProps): JSX.Element => {
	const visibleLoading = useDelayedLoading(loading);
	const [errorView, setErrorView] = useState<ErrorView>("current");
	const data: ErrorGroupData = errorView === "current" ? current : previous;

	const jobKey = perJob?.discriminatorKey;
	const runLevel: ServiceError[] = jobKey
		? data.errors.filter((e: ServiceError): boolean => e[jobKey] == null)
		: data.errors;
	const criticalGroups = groupErrorsByMessage(runLevel.filter((e: ServiceError): boolean => e.level === "critical"));
	const serviceGroups = groupErrorsByMessage(runLevel.filter((e: ServiceError): boolean => e.level !== "critical"));
	const perJobGroups = jobKey
		? groupErrorsByMessage(
				data.errors.filter((e: ServiceError): boolean => e[jobKey] != null),
				data.platformByJobId
			)
		: [];

	return (
		<div id="error-summary-card" className="status-card mt-4">
			<h2 className="card-title">
				<i className="bi bi-exclamation-triangle me-2"></i>
				Error Summary
				{isRunning && <span className="live-indicator ms-2"></span>}
			</h2>

			<div className="d-flex flex-wrap gap-4 mb-3">
				<div className="form-check form-switch">
					<input
						type="checkbox"
						className="form-check-input"
						id="errorViewToggle"
						checked={errorView === "last"}
						onChange={(e) => setErrorView(e.target.checked ? "last" : "current")}
					/>
					<label className="form-check-label" htmlFor="errorViewToggle">
						Show previous run errors
					</label>
				</div>
				<div className="form-check form-switch">
					<input
						type="checkbox"
						className="form-check-input"
						id="showAcknowledgedToggle"
						checked={showAcknowledged}
						onChange={(e) => onToggleAcknowledged(e.target.checked)}
					/>
					<label className="form-check-label" htmlFor="showAcknowledgedToggle">
						Show acknowledged errors
					</label>
				</div>
			</div>

			{visibleLoading ? (
				<div className="d-flex justify-content-center align-items-center" style={{ minHeight: "270px" }}>
					<div className="spinner-border text-primary" role="status">
						<span className="visually-hidden">Loading...</span>
					</div>
				</div>
			) : (
				<div style={{ display: "flex", gap: "18px", height: "540px", overflow: "auto" }}>
					<GroupedErrorList
						title="Critical Service Errors"
						groups={criticalGroups}
						variant="danger"
						emptyText="No critical errors"
						onAcknowledge={data.acknowledge}
					/>
					<GroupedErrorList
						title="Service Errors"
						groups={serviceGroups}
						variant="info"
						emptyText="No service errors"
						onAcknowledge={data.acknowledge}
					/>
					{perJob && (
						<GroupedErrorList
							title={perJob.title}
							groups={perJobGroups}
							variant="warning"
							emptyText={perJob.emptyText}
							showJobs={perJob.showJobs}
							onAcknowledge={data.acknowledge}
						/>
					)}
				</div>
			)}
		</div>
	);
};
