import React, { JSX } from "react";
import { ProcessingStatus, ScrapedJobData } from "../../../services/schemas/Services";
import { useConfig } from "../../../contexts/ConfigContext";
import JobRatingCard from "./JobRatingCard";

interface JobRatingSectionProps {
	scrapedJob: ScrapedJobData;
}

const JobRatingSection = ({ scrapedJob }: JobRatingSectionProps): JSX.Element | null => {
	const { config } = useConfig();
	const rating = scrapedJob?.job_rating;

	const createReportLink = (subject: string, errorMessage: string | null): JSX.Element | null => {
		const supportEmail: string = config?.support_email;
		if (!supportEmail) return null;

		const body: string = encodeURIComponent(
			`Error Details:\n${errorMessage || "Unknown error"}\n\nJob ID: ${scrapedJob?.id || "N/A"}\nJob Title: ${scrapedJob?.title || "N/A"}\nJob URL: ${scrapedJob?.url || "N/A"}`
		);
		const mailtoLink = `mailto:${supportEmail}?subject=${encodeURIComponent(subject)}&body=${body}`;

		return (
			<a href={mailtoLink} style={{ color: "inherit", textDecoration: "underline" }}>
				report it here
			</a>
		);
	};

	// Successful rating
	if (rating?.status === ProcessingStatus.COMPLETED) {
		return (
			<>
				<JobRatingCard jobRating={rating} />
				{rating.notes.length > 0 && (
					<div className="text-muted small mt-2">
						<i className="bi bi-info-circle me-1" />
						<span>Notes:</span>
						<ul className="mb-0 mt-1">
							{rating.notes.map((note: string, idx: number) => (
								<li key={idx}>{note}</li>
							))}
						</ul>
					</div>
				)}
			</>
		);
	}

	// Rating failed with error
	if (rating?.status === ProcessingStatus.FAILED) {
		const ratingErrorText: string | null =
			rating.rating_errors
				?.map((e) => e.message)
				.join("\n\n---\n\n") || null;
		const reportLink = createReportLink("Job Rating Error Report", ratingErrorText);
		return (
			<div className="text-muted small">
				<i className="bi bi-exclamation-triangle me-1" />
				This job could not be rated due to an unexpected error.
				{reportLink && <> You can {reportLink}.</>}
			</div>
		);
	}

	// Rating skipped
	if (rating?.status === ProcessingStatus.SKIPPED) {
		return (
			<div className="text-muted small">
				<i className="bi bi-skip-forward me-1" />
				This job was not rated due to the following reason: {rating.skip_reason}
			</div>
		);
	}

	// Scraping not successfully completed — rating not applicable
	if (scrapedJob?.status !== ProcessingStatus.COMPLETED) {
		return (
			<div className="text-muted small">
				<i className="bi bi-dash-circle me-1" />
				Rating not available — job has not been successfully scraped yet.
			</div>
		);
	}

	// Pending rating (scraped successfully but no rating yet)
	return (
		<div className="text-muted small">
			<i className="bi bi-hourglass-split me-1" />
			This job has yet to be rated. Please come back later.
		</div>
	);
};

export default JobRatingSection;
