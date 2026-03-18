import React, { useState } from "react";
import { Button, Collapse } from "react-bootstrap";
import { JobRatingData } from "../../../services/schemas/Services";
import { useConfig } from "../../../contexts/ConfigContext";
import { DataContextValue, useDataContext } from "../../../contexts/DataContext";

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
		<div className="card shadow-sm">
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
					<>
						<Button
							variant="link"
							size="sm"
							className="p-0 text-muted text-decoration-none"
							onClick={handleTogglePrompt}
						>
							<i className={`bi ${showPrompt ? "bi-chevron-up" : "bi-chevron-down"} me-1`} />
							{showPrompt ? "Hide" : "Show"} AI Prompt
						</Button>
						<Collapse in={showPrompt}>
							<div>
								<div
									className="mt-2 p-2 rounded small"
									style={{ whiteSpace: "pre-wrap", backgroundColor: "var(--bs-tertiary-bg)" }}
								>
									{jobRating.job_prompt}
								</div>
							</div>
						</Collapse>
					</>
				)}
			</div>
		</div>
	);
};

export default JobRatingCard;
