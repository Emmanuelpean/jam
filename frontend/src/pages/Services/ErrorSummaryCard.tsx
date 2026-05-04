import React, { JSX, useState } from "react";
import { ServiceLog } from "../../services/schemas/Services";
import { useDelayedLoading } from "../../hooks/useDelayedLoading";

export type ErrorView = "current" | "last";

interface SharedErrorSummaryCardProps {
	latestServiceLogs: ServiceLog[] | null;
	isRunning: boolean;
	loading?: boolean;
	children: (errorView: ErrorView) => React.ReactNode;
}

export const ErrorSummaryCard = ({
	latestServiceLogs,
	isRunning,
	loading = false,
	children,
}: SharedErrorSummaryCardProps): JSX.Element => {
	const visibleLoading = useDelayedLoading(loading);
	const [errorView, setErrorView] = useState<ErrorView>("current");

	const criticalErrorLogs: ServiceLog[] = latestServiceLogs || [];
	const criticalErrorCount: number = criticalErrorLogs.filter(
		(l: ServiceLog): boolean => !!(l.error_message && l.error_message.trim())
	).length;

	return (
		<div id="error-summary-card" className="status-card mt-4">
			<h2 className="card-title">
				<i className="bi bi-exclamation-triangle me-2"></i>
				Error Summary
				{isRunning && <span className="live-indicator ms-2"></span>}
			</h2>

			<div className="form-check form-switch mb-3">
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

			{visibleLoading ? (
				<div className="d-flex justify-content-center align-items-center" style={{ minHeight: "270px" }}>
					<div className="spinner-border text-primary" role="status">
						<span className="visually-hidden">Loading...</span>
					</div>
				</div>
			) : (
				<div style={{ display: "flex", gap: "18px", height: "540px", overflow: "auto" }}>
					<div style={{ flex: 1 }}>
						<h5 className="mb-3">Critical Errors ({criticalErrorCount})</h5>
						{criticalErrorCount === 0 ? (
							<div className="text-muted">No critical errors</div>
						) : (
							<div className="error-list d-flex flex-column" style={{ gap: "10.8px" }}>
								{criticalErrorLogs
									.slice()
									.sort(
										(a: ServiceLog, b: ServiceLog): number =>
											new Date(b.run_datetime).getTime() - new Date(a.run_datetime).getTime()
									)
									.filter(
										(log: ServiceLog): boolean => !!(log.error_message && log.error_message.trim())
									)
									.map(
										(log: ServiceLog, idx: number): JSX.Element => (
											<div key={idx} className="alert alert-danger">
												<div className="small mb-1">
													{new Date(log.run_datetime).toLocaleString()}
												</div>
												<div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
													{log.error_message}
												</div>
											</div>
										)
									)}
							</div>
						)}
					</div>

					{children(errorView)}
				</div>
			)}
		</div>
	);
};
