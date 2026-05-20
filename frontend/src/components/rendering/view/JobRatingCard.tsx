import React, { JSX, useState } from "react";
import { Button } from "react-bootstrap";
import { JobRatingData } from "../../../services/schemas/Services";

interface JobRatingCardProps {
	jobRating: JobRatingData;
}

const JobRatingCard = ({ jobRating }: JobRatingCardProps): JSX.Element => {
	const [showPrompt, setShowPrompt] = useState<boolean>(false);

	const handleTogglePrompt = (e: React.MouseEvent): void => {
		e.preventDefault();
		e.stopPropagation();
		setShowPrompt(!showPrompt);
	};

	return (
		<div className="card shadow-sm position-relative">
			{jobRating.job_prompt && (
				<Button
					variant="outline-secondary"
					size="sm"
					className="p-1 lh-1 position-absolute top-0 end-0 m-2"
					onClick={handleTogglePrompt}
					title={showPrompt ? "Hide AI Prompt" : "Show AI Prompt"}
				>
					<i className="bi bi-robot me-1" />
					<i
						className="bi bi-chevron-down"
						style={{
							display: "inline-block",
							transition: "transform 0.3s ease-in-out",
							transform: showPrompt ? "rotate(0deg)" : "rotate(-90deg)",
						}}
					/>
				</Button>
			)}
			<div className="card-body p-3">
				<table className="table table-sm table-striped table-hover mb-2">
					<thead>
						<tr>
							<th className="text-center">Overall</th>
							<th className="text-center">Educational</th>
							<th className="text-center">Experience</th>
							<th className="text-center">Interest</th>
							<th className="text-center">Technical</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td className="text-center fw-semibold">{jobRating.overall_score || "/"}</td>
							<td className="text-center">{jobRating.educational_score || "/"}</td>
							<td className="text-center">{jobRating.experience_score || "/"}</td>
							<td className="text-center">{jobRating.interest_score || "/"}</td>
							<td className="text-center">{jobRating.technical_score || "/"}</td>
						</tr>
					</tbody>
				</table>

				{jobRating.feedback && <div className="small mb-2">{jobRating.feedback}</div>}

				{jobRating.job_prompt && (
					<div
						style={{
							display: "grid",
							gridTemplateRows: showPrompt ? "1fr" : "0fr",
							transition: "grid-template-rows 0.3s ease-in-out",
						}}
					>
						<div style={{ overflow: "hidden" }}>
							<div
								className="mt-2 p-2 rounded small"
								style={{ whiteSpace: "pre-wrap", backgroundColor: "var(--bs-tertiary-bg)" }}
							>
								{jobRating.job_prompt}
							</div>
						</div>
					</div>
				)}
			</div>
		</div>
	);
};

export default JobRatingCard;
