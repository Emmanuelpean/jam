import React, { JSX, useState } from "react";
import { ErrorGroup } from "../../hooks/useServiceErrors";
import { ServiceError } from "../../services/schemas/Services";
import { toDdMmYyyyHhMm } from "../../utils/TimeUtils";

interface GroupedErrorListProps {
	title: string;
	groups: ErrorGroup[];
	variant: "info" | "warning" | "danger";
	emptyText: string;
	showJobs?: boolean;
	onSetAcknowledged: (ids: number[], isAcknowledged: boolean) => Promise<void>;
}

const formatContextValue = (value: unknown): string =>
	value === null || typeof value !== "object" ? String(value) : JSON.stringify(value);

export const GroupedErrorList = ({
	title,
	groups,
	variant,
	emptyText,
	showJobs = false,
	onSetAcknowledged,
}: GroupedErrorListProps): JSX.Element => {
	const [busyIndex, setBusyIndex] = useState<number | null>(null);
	const [busyErrorId, setBusyErrorId] = useState<number | null>(null);
	const [expanded, setExpanded] = useState<Set<string>>(new Set());

	const groupKey = (group: ErrorGroup): string => `${group.errorType}:${group.message}`;

	const handleToggleAcknowledged = async (group: ErrorGroup, index: number): Promise<void> => {
		setBusyIndex(index);
		try {
			await onSetAcknowledged(group.ids, !group.isAcknowledged);
		} finally {
			setBusyIndex(null);
		}
	};

	const handleToggleErrorAcknowledged = async (error: ServiceError): Promise<void> => {
		setBusyErrorId(error.id);
		try {
			await onSetAcknowledged([error.id], !error.is_acknowledged);
		} finally {
			setBusyErrorId(null);
		}
	};

	const toggleExpanded = (key: string): void => {
		setExpanded((prev: Set<string>): Set<string> => {
			const next = new Set(prev);
			if (next.has(key)) {
				next.delete(key);
			} else {
				next.add(key);
			}
			return next;
		});
	};

	return (
		<div style={{ flex: 1 }}>
			<h5 className="mb-3">
				{title} ({groups.length} unique)
			</h5>
			{groups.length === 0 ? (
				<div className="text-muted">{emptyText}</div>
			) : (
				<div className="error-list d-flex flex-column" style={{ gap: "10.8px" }}>
					{groups.map((group: ErrorGroup, idx: number) => {
						const key: string = groupKey(group);
						const isExpanded: boolean = expanded.has(key);
						return (
							<div key={idx} className={`alert alert-${variant}`}>
								<div className="d-flex justify-content-between align-items-start mb-2 gap-2">
									<span className={`badge bg-${variant}`}>
										{group.count} {group.count > 1 ? "occurrences" : "occurrence"}
									</span>
									<button
										type="button"
										className="btn btn-sm btn-outline-secondary py-0"
										disabled={busyIndex === idx}
										title={group.isAcknowledged ? "De-acknowledge" : "Acknowledge"}
										aria-label={group.isAcknowledged ? "De-acknowledge" : "Acknowledge"}
										onClick={() => handleToggleAcknowledged(group, idx)}
									>
										<i
											className={`bi ${
												busyIndex === idx
													? "bi-arrow-repeat spin"
													: group.isAcknowledged
														? "bi-arrow-counterclockwise"
														: "bi-check-lg"
											}`}
										></i>
									</button>
								</div>
								<div
									className="grouped-error-message"
									role="button"
									tabIndex={0}
									aria-expanded={isExpanded}
									title={isExpanded ? "Hide individual errors" : "Show individual errors"}
									onClick={() => toggleExpanded(key)}
									onKeyDown={(e: React.KeyboardEvent): void => {
										if (e.key === "Enter" || e.key === " ") {
											e.preventDefault();
											toggleExpanded(key);
										}
									}}
									style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", cursor: "pointer" }}
								>
									<i className={`bi ${isExpanded ? "bi-chevron-down" : "bi-chevron-right"} me-1`}></i>
									<span className="grouped-error-type">{group.errorType}</span> {group.message}
								</div>
								{showJobs && group.jobs.length > 0 && (
									<div className="mt-2" style={{ fontSize: "0.85rem" }}>
										{group.jobs.map((job, jobIdx: number) => (
											<div key={jobIdx}>
												{job.platform ?? "unknown"}: {job.jobId}
											</div>
										))}
									</div>
								)}
								{isExpanded && (
									<div className="grouped-error-occurrences mt-2">
										{group.errors.map(
											(error: ServiceError): JSX.Element => (
												<div key={error.id} className="grouped-error-occurrence">
													<div className="grouped-error-occurrence-meta">
														<span className="fw-semibold">#{error.id}</span>
														<span>{toDdMmYyyyHhMm(new Date(error.created_at))}</span>
														{error.level && (
															<span className="text-uppercase">{error.level}</span>
														)}
														<button
															type="button"
															className="btn btn-sm btn-outline-secondary py-0 ms-auto"
															disabled={busyErrorId === error.id}
															title={
																error.is_acknowledged ? "De-acknowledge" : "Acknowledge"
															}
															aria-label={
																error.is_acknowledged ? "De-acknowledge" : "Acknowledge"
															}
															onClick={() => handleToggleErrorAcknowledged(error)}
														>
															<i
																className={`bi ${
																	busyErrorId === error.id
																		? "bi-arrow-repeat spin"
																		: error.is_acknowledged
																			? "bi-arrow-counterclockwise"
																			: "bi-check-lg"
																}`}
															></i>
														</button>
													</div>
													{error.context && Object.keys(error.context).length > 0 && (
														<div className="grouped-error-context">
															{Object.entries(error.context).map(
																([contextKey, value]): JSX.Element => (
																	<div key={contextKey}>
																		<span className="grouped-error-context-key">
																			{contextKey}:
																		</span>{" "}
																		{formatContextValue(value)}
																	</div>
																)
															)}
														</div>
													)}
													{error.traceback && (
														<details className="mt-1">
															<summary style={{ cursor: "pointer" }}>Traceback</summary>
															<pre className="grouped-error-traceback">
																{error.traceback}
															</pre>
														</details>
													)}
												</div>
											)
										)}
									</div>
								)}
							</div>
						);
					})}
				</div>
			)}
		</div>
	);
};
