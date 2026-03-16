import React, { JSX } from "react";
import { ServiceLog } from "../../../services/schemas/Services";
import { ErrorSummaryCard as SharedErrorSummaryCard, ErrorView } from "../ErrorSummaryCard";

interface ErrorSummaryCardProps {
	latestServiceLogs: ServiceLog[] | null;
	lastRatingErrors: Record<string, number>;
	latestRatingErrors: Record<string, number>;
	isRunning: boolean;
	loading?: boolean;
}

export const ErrorSummaryCard = ({
	latestServiceLogs,
	lastRatingErrors,
	latestRatingErrors,
	isRunning,
	loading = false,
}: ErrorSummaryCardProps): JSX.Element => {
	return (
		<SharedErrorSummaryCard latestServiceLogs={latestServiceLogs} isRunning={isRunning} loading={loading}>
			{(errorView: ErrorView) => {
				const ratingErrors = errorView === "current" ? latestRatingErrors : lastRatingErrors;
				return (
					<div style={{ flex: 1 }}>
						<h5 className="mb-3">Job Rating Errors ({Object.keys(ratingErrors).length} unique)</h5>
						{Object.keys(ratingErrors).length === 0 ? (
							<div className="text-muted">No scrape errors</div>
						) : (
							<div className="error-list d-flex flex-column" style={{ gap: "10.8px" }}>
								{Object.entries(ratingErrors)
									.sort((a, b) => b[1] - a[1])
									.map(([errorMsg, count], idx) => (
										<div key={idx} className="alert alert-warning">
											<div className="d-flex justify-content-between align-items-start mb-1">
												<span className="badge bg-warning">
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
				);
			}}
		</SharedErrorSummaryCard>
	);
};
