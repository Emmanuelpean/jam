import React, { JSX } from "react";
import { ServiceError } from "../../services/schemas/Services";
import { ErrorGroup, groupErrorsByMessage } from "../../hooks/useServiceErrors";
import { useDelayedLoading } from "../../hooks/useDelayedLoading";
import { GroupedErrorList } from "./GroupedErrorList";

export interface ErrorGroupData {
	errors: ServiceError[];
	setAcknowledged: (ids: number[], isAcknowledged: boolean) => Promise<void>;
	platformByJobId?: Record<number, string | null>;
}

export interface PerJobErrorConfig {
	title: string;
	discriminatorKey: "scraped_job_id" | "job_rating_id";
	emptyText: string;
}

interface ErrorSummaryCardProps {
	current: ErrorGroupData;
	showAcknowledged: boolean;
	onToggleAcknowledged: (value: boolean) => void;
	isRunning: boolean;
	loading?: boolean;
	perJob?: PerJobErrorConfig;
	selectedRunLabel?: string | null;
	onClearSelectedRun?: () => void;
}

export const ErrorSummaryCard = ({
	current: data,
	showAcknowledged,
	onToggleAcknowledged,
	isRunning,
	loading = false,
	perJob,
	selectedRunLabel = null,
	onClearSelectedRun,
}: ErrorSummaryCardProps): JSX.Element => {
	const visibleLoading = useDelayedLoading(loading);

	const jobKey = perJob?.discriminatorKey;
	const runLevel: ServiceError[] = jobKey
		? data.errors.filter((e: ServiceError): boolean => e[jobKey] == null)
		: data.errors;
	const criticalGroups: ErrorGroup[] = groupErrorsByMessage(
		runLevel.filter((e: ServiceError): boolean => e.level === "critical")
	);
	const serviceGroups: ErrorGroup[] = groupErrorsByMessage(
		runLevel.filter((e: ServiceError): boolean => e.level !== "critical")
	);
	const perJobGroups: ErrorGroup[] = jobKey
		? groupErrorsByMessage(data.errors.filter((e: ServiceError): boolean => e[jobKey] != null))
		: [];
	return (
		<div id="error-summary-card" className="status-card mt-4">
			<h2 className="card-title">
				<i className="bi bi-exclamation-triangle me-2"></i>
				Error Summary
				{isRunning && <span className="live-indicator ms-2"></span>}
				{selectedRunLabel && (
					<button
						id="selected-run-filter"
						type="button"
						className="btn btn-sm btn-outline-primary ms-3 py-0"
						onClick={onClearSelectedRun}
						title="Show errors for all runs"
					>
						<i className="bi bi-funnel-fill me-1"></i>
						Run: {selectedRunLabel}
						<i className="bi bi-x-lg ms-2"></i>
					</button>
				)}
			</h2>

			<div className="d-flex flex-wrap gap-4 mb-3">
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
						onSetAcknowledged={data.setAcknowledged}
					/>
					<GroupedErrorList
						title="Service Errors"
						groups={serviceGroups}
						variant="info"
						emptyText="No service errors"
						onSetAcknowledged={data.setAcknowledged}
					/>
					{perJob && (
						<GroupedErrorList
							title={perJob.title}
							groups={perJobGroups}
							variant="warning"
							emptyText={perJob.emptyText}
							platformByJobId={data.platformByJobId}
							onSetAcknowledged={data.setAcknowledged}
						/>
					)}
				</div>
			)}
		</div>
	);
};
