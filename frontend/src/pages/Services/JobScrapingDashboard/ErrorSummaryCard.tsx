import React, { JSX, useState } from "react";
import { JobScrapingServiceLogData } from "../../../services/schemas/Services";
import { ErrorCount } from "../../../hooks/useJobScraperErrors";

interface ErrorSummaryCardProps {
	latestServiceLogs: JobScrapingServiceLogData[] | null;
	lastScraperErrors: Record<string, ErrorCount>;
	latestScraperErrors: Record<string, ErrorCount>;
	lastServiceErrors: Record<string, number>;
	latestServiceErrors: Record<string, number>;
	isRunning: boolean;
	loading?: boolean;
}

type ErrorView = "current" | "last";

export const ErrorSummaryCard = ({
	latestServiceLogs,
	lastScraperErrors,
	latestScraperErrors,
	lastServiceErrors,
	latestServiceErrors,
	isRunning,
	loading = false,
}: ErrorSummaryCardProps): JSX.Element => {
	const [errorView, setErrorView] = useState<ErrorView>("current");

	// Select data based on view
	const criticalErrorLogs: JobScrapingServiceLogData[] = latestServiceLogs || [];
	const scrapeErrors = errorView === "current" ? latestScraperErrors : lastScraperErrors;
	const serviceErrors = errorView === "current" ? latestServiceErrors : lastServiceErrors;

	const criticalErrorCount: number = criticalErrorLogs.filter(
		(l: JobScrapingServiceLogData): boolean => !!(l.error_message && l.error_message.trim())
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

			{loading ? (
				<div className="d-flex justify-content-center align-items-center" style={{ minHeight: "270px" }}>
					<div className="spinner-border text-primary" role="status">
						<span className="visually-hidden">Loading...</span>
					</div>
				</div>
			) : (
				<div style={{ display: "flex", gap: "18px", height: "540px", overflow: "auto" }}>
					{/* Critical Errors Column */}
					<div style={{ flex: 1 }}>
						<h5 className="mb-3">Critical Errors ({criticalErrorCount})</h5>
						{criticalErrorCount === 0 ? (
							<div className="text-muted">No critical errors</div>
						) : (
							<div className="error-list d-flex flex-column" style={{ gap: "10.8px" }}>
								{criticalErrorLogs
									.slice()
									.sort(
										(a: JobScrapingServiceLogData, b: JobScrapingServiceLogData): number =>
											new Date(b.run_datetime).getTime() - new Date(a.run_datetime).getTime()
									)
									.filter(
										(log: JobScrapingServiceLogData): boolean =>
											!!(log.error_message && log.error_message.trim())
									)
									.map(
										(log: JobScrapingServiceLogData, idx: number): JSX.Element => (
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

					{/* Service Errors Column */}
					<div style={{ flex: 1 }}>
						<h5 className="mb-3">Service Errors ({Object.keys(serviceErrors).length} unique)</h5>
						{Object.keys(serviceErrors).length === 0 ? (
							<div className="text-muted">No service errors</div>
						) : (
							<div className="error-list d-flex flex-column" style={{ gap: "10.8px" }}>
								{Object.entries(serviceErrors)
									.sort((a, b) => b[1] - a[1])
									.map(([errorMsg, count], idx) => (
										<div key={idx} className="alert alert-info">
											<div className="d-flex justify-content-between align-items-start mb-1">
												<span className="badge bg-info">
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

					{/* Scraping Errors Column */}
					<div style={{ flex: 1 }}>
						<h5 className="mb-3">Scraping Errors ({Object.keys(scrapeErrors).length} unique)</h5>
						{Object.keys(scrapeErrors).length === 0 ? (
							<div className="text-muted">No scrape errors</div>
						) : (
							<div className="error-list d-flex flex-column" style={{ gap: "10.8px" }}>
								{Object.entries(scrapeErrors)
									.sort((a, b) => b[1].count - a[1].count)
									.map(([errorMsg, error], idx) => (
										<div key={idx} className="alert alert-warning">
											<div className="d-flex justify-content-between align-items-start mb-2">
												<span className="badge bg-warning">
													{error.count} {error.count > 1 ? "occurrences" : "occurrence"}
												</span>
											</div>
											<div
												style={{
													whiteSpace: "pre-wrap",
													wordBreak: "break-word",
												}}
												className="mb-2"
											>
												{errorMsg}
											</div>
											<div className="mt-2" style={{ fontSize: "0.85rem" }}>
												{error.jobs.map((job, jobIdx) => (
													<div key={jobIdx}>
														{job.platform}: {job.jobId}
													</div>
												))}
											</div>
										</div>
									))}
							</div>
						)}
					</div>
				</div>
			)}
		</div>
	);
};
