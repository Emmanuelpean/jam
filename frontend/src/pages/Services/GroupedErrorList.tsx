import React, { JSX, useState } from "react";
import { ErrorGroup } from "../../hooks/useServiceErrors";

interface GroupedErrorListProps {
	title: string;
	groups: ErrorGroup[];
	variant: "info" | "warning" | "danger";
	emptyText: string;
	/** Whether to list the affected jobs (platform: id) under each error. */
	showJobs?: boolean;
	onAcknowledge: (ids: number[]) => Promise<void>;
}

/** A single column of grouped errors, each with an acknowledge button. */
export const GroupedErrorList = ({
	title,
	groups,
	variant,
	emptyText,
	showJobs = false,
	onAcknowledge,
}: GroupedErrorListProps): JSX.Element => {
	const [acknowledging, setAcknowledging] = useState<number | null>(null);

	const handleAcknowledge = async (group: ErrorGroup, index: number): Promise<void> => {
		setAcknowledging(index);
		try {
			await onAcknowledge(group.ids);
		} finally {
			setAcknowledging(null);
		}
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
					{groups.map((group: ErrorGroup, idx: number) => (
						<div key={idx} className={`alert alert-${variant}`}>
							<div className="d-flex justify-content-between align-items-start mb-2 gap-2">
								<span className={`badge bg-${variant}`}>
									{group.count} {group.count > 1 ? "occurrences" : "occurrence"}
								</span>
								<button
									type="button"
									className="btn btn-sm btn-outline-secondary py-0"
									disabled={acknowledging === idx}
									onClick={() => handleAcknowledge(group, idx)}
								>
									{acknowledging === idx ? "Acknowledging…" : "Acknowledge"}
								</button>
							</div>
							<div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{group.message}</div>
							{showJobs && group.jobs.length > 0 && (
								<div className="mt-2" style={{ fontSize: "0.85rem" }}>
									{group.jobs.map((job, jobIdx: number) => (
										<div key={jobIdx}>
											{job.platform ?? "unknown"}: {job.jobId}
										</div>
									))}
								</div>
							)}
						</div>
					))}
				</div>
			)}
		</div>
	);
};
