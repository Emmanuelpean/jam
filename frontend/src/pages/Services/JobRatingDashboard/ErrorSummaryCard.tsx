import React, { JSX, useState } from "react";
import { ServiceLog } from "../../../services/schemas/Services";

interface ErrorSummaryCardProps {
	latestServiceLogs: ServiceLog[] | null;
	lastRatingErrors: Record<string, number>;
	latestRatingErrors: Record<string, number>;
	isRunning: boolean;
}

type ErrorView = "current" | "last";

export const ErrorSummaryCard = ({
	latestServiceLogs,
	lastRatingErrors,
	latestRatingErrors,
	isRunning,
}: ErrorSummaryCardProps): JSX.Element => {
	const [errorView, setErrorView] = useState<ErrorView>("current");

	// Select data based on view
	const criticalErrorLogs: ServiceLog[] = latestServiceLogs || [];
	const scrapeErrors = errorView === "current" ? latestRatingErrors : lastRatingErrors;

	const criticalErrorCount = criticalErrorLogs.filter(
		(l: ServiceLog): boolean => !!(l.error_message && l.error_message.trim())
	).length;

	const handleViewToggle = (e: React.ChangeEvent<HTMLInputElement>): void => {
		setErrorView(e.target.checked ? "last" : "current");
	};

	return (
		<div className="status-card mt-4">
			<h2 className="card-title">
				<i className="bi bi-exclamation-triangle me-2"></i>
				Error Summary
				{isRunning && <span className="live-indicator ms-2"></span>}
			</h2>

			<div className="form-check mb-3">
				<input
					type="checkbox"
					className="form-check-input"
					id="errorViewToggle"
					checked={errorView === "last"}
					onChange={handleViewToggle}
				/>
				<label className="form-check-label" htmlFor="errorViewToggle">
					Show previous run errors
				</label>
			</div>

			<div style={{ display: "flex", gap: "20px", height: "600px", overflow: "auto" }}>
				{/* Critical Errors Column */}
				<div style={{ flex: 1 }}>
					<h5 className="mb-3">Critical Errors ({criticalErrorCount})</h5>
					{criticalErrorCount === 0 ? (
						<div className="text-muted">No critical errors</div>
					) : (
						<div className="error-list d-flex flex-column" style={{ gap: "12px" }}>
							{criticalErrorLogs
								.slice()
								.sort(
									(a: ServiceLog, b: ServiceLog): number =>
										new Date(b.run_datetime).getTime() - new Date(a.run_datetime).getTime()
								)
								.filter((log: ServiceLog): boolean => !!(log.error_message && log.error_message.trim()))
								.map(
									(log: ServiceLog, idx: number): JSX.Element => (
										<div key={idx} className="alert alert-danger">
											<div className="small mb-1">
												{new Date(log.run_datetime).toLocaleString()}
											</div>
											<div
												style={{
													whiteSpace: "pre-wrap",
													wordBreak: "break-word",
												}}
											>
												{log.error_message}
											</div>
										</div>
									)
								)}
						</div>
					)}
				</div>

				{/* Rating Errors Column */}
				<div style={{ flex: 1 }}>
					<h5 className="mb-3">Job Rating Errors ({Object.keys(scrapeErrors).length} unique)</h5>
					{Object.keys(scrapeErrors).length === 0 ? (
						<div className="text-muted">No scrape errors</div>
					) : (
						<div className="error-list d-flex flex-column" style={{ gap: "12px" }}>
							{Object.entries(scrapeErrors)
								.sort((a, b) => b[1] - a[1])
								.map(([errorMsg, count], idx) => (
									<div key={idx} className="alert alert-warning">
										<div className="d-flex justify-content-between align-items-start mb-1">
											<span className="badge bg-warning">
												{count} {count > 1 ? "occurrences" : "occurrence"}
											</span>
										</div>
										<div
											style={{
												whiteSpace: "pre-wrap",
												wordBreak: "break-word",
											}}
										>
											{errorMsg}
										</div>
									</div>
								))}
						</div>
					)}
				</div>
			</div>
		</div>
	);
};
