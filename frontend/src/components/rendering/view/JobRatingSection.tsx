import React, { JSX } from "react";
import { JobRatingData, ProcessingStatus, ScrapedJobData, ServiceError } from "../../../services/schemas/Services";
import { useConfig } from "../../../contexts/ConfigContext";
import JobRatingCard from "./JobRatingCard";

interface JobRatingSectionProps {
	scrapedJob: ScrapedJobData;
}

const JobRatingSection = ({ scrapedJob }: JobRatingSectionProps): JSX.Element | null => {
	const { config } = useConfig();
	const rating: JobRatingData | null = scrapedJob?.job_rating;
	const supportEmail: string | undefined = config?.support_email;

	const createReportLink = (rating: JobRatingData): JSX.Element => {
		const errorIds: number[] = rating.rating_errors?.map((e: ServiceError): number => e.id) || [];
		const title: string = "Job Rating Error Report";
		const message: string = ["", `Job ID: ${scrapedJob.id}`, `Service Error IDs: ${errorIds.join(", ")}`].join(
			"\n"
		);
		const body: string = encodeURIComponent(message);
		const mailtoLink = `mailto:${supportEmail}?subject=${encodeURIComponent(title)}&body=${body}`;

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
							{rating.notes.map(
								(note: string, idx: number): JSX.Element => (
									<li key={idx}>{note}</li>
								)
							)}
						</ul>
					</div>
				)}
			</>
		);
	}

	// Rating failed
	if (rating?.status === ProcessingStatus.FAILED) {
		const reportLink: JSX.Element = createReportLink(rating);
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

	// Scraping pending
	if (scrapedJob?.status === ProcessingStatus.PENDING) {
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
