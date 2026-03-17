import React, { JSX } from "react";
import { JobScrapingServiceLogData } from "../../../services/schemas/Services";
import { ErrorCount } from "../../../hooks/useJobScraperErrors";
import { ErrorSummaryCard as SharedErrorSummaryCard, ErrorView } from "../ErrorSummaryCard";

interface ErrorSummaryCardProps {
	latestServiceLogs: JobScrapingServiceLogData[] | null;
	lastScraperErrors: Record<string, ErrorCount>;
	latestScraperErrors: Record<string, ErrorCount>;
	lastServiceErrors: Record<string, number>;
	latestServiceErrors: Record<string, number>;
	isRunning: boolean;
	loading?: boolean;
}

export const ErrorSummaryCard = ({
	latestServiceLogs,
	lastScraperErrors,
	latestScraperErrors,
	lastServiceErrors,
	latestServiceErrors,
	isRunning,
	loading = false,
}: ErrorSummaryCardProps): JSX.Element => {
	return (
		<SharedErrorSummaryCard
			latestServiceLogs={latestServiceLogs as any}
			isRunning={isRunning}
			loading={loading}
		>
			{(errorView: ErrorView) => {
				const scrapeErrors = errorView === "current" ? latestScraperErrors : lastScraperErrors;
				const serviceErrors = errorView === "current" ? latestServiceErrors : lastServiceErrors;
				return (
					<>
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
												<div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
													{errorMsg}
												</div>
											</div>
										))}
								</div>
							)}
						</div>

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
													style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}
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
					</>
				);
			}}
		</SharedErrorSummaryCard>
	);
};
