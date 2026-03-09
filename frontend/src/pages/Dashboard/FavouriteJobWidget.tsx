import React, { useRef } from "react";
import { Badge } from "react-bootstrap";
import { useDataContext } from "../../contexts/DataContext";
import { EnrichedJobData } from "../../services/schemas/DataTables";
import DashboardCard from "./DashboardCard";
import { DataModalHandle } from "../../components/DataModal/DataModal";
import { JobModal } from "../../components/DataModal/JobModal";
import { getApplicationStatusBadgeClass } from "../../components/rendering/view/Icons";

const FavouriteJobWidget: React.FC = () => {
	const { jobs } = useDataContext();
	const jobModalRef = useRef<DataModalHandle>(null);

	const favouriteJob: EnrichedJobData | undefined = jobs.find((j) => j.is_favourite);

	const handleOpenJob = () => {
		if (favouriteJob) {
			jobModalRef.current?.showView(favouriteJob);
		}
	};

	return (
		<>
			<DashboardCard
				icon="star-fill"
				title="Favourite Job"
				isEmpty={!favouriteJob}
				emptyState={{
					icon: "star",
					title: "No favourite job set",
					description: "Mark a job as favourite in the job details to pin it here",
				}}
				onHeaderClick={favouriteJob ? handleOpenJob : undefined}
			>
				{favouriteJob && (
					<div className="p-3 d-flex flex-column gap-3">
						<div>
							<div className="d-flex align-items-start justify-content-between gap-2 mb-1">
								<h6 className="fw-bold mb-0" style={{ lineHeight: 1.3 }}>
									{favouriteJob.title}
								</h6>
								{favouriteJob.application_status && (
									<Badge
										className={getApplicationStatusBadgeClass(favouriteJob.application_status)}
										style={{ flexShrink: 0, fontSize: "0.7rem" }}
									>
										{favouriteJob.application_status}
									</Badge>
								)}
							</div>
							{favouriteJob.name && (
								<small className="text-muted d-flex align-items-center gap-1">
									<i className="bi bi-building"></i>
									{favouriteJob.name}
								</small>
							)}
						</div>

						{(favouriteJob.salary_min || favouriteJob.salary_max) && (
							<div className="d-flex align-items-center gap-1 text-muted small">
								<i className="bi bi-cash-stack"></i>
								<span>
									{favouriteJob.salary_min && favouriteJob.salary_max
										? `${favouriteJob.salary_min.toLocaleString()} – ${favouriteJob.salary_max.toLocaleString()}`
										: favouriteJob.salary_min
											? `From ${favouriteJob.salary_min.toLocaleString()}`
											: `Up to ${favouriteJob.salary_max!.toLocaleString()}`}
									{favouriteJob.salary_currency ? ` ${favouriteJob.salary_currency}` : ""}
								</span>
							</div>
						)}

						{favouriteJob.attendance_type && (
							<div className="d-flex align-items-center gap-1 text-muted small">
								<i className="bi bi-building"></i>
								<span style={{ textTransform: "capitalize" }}>{favouriteJob.attendance_type.replace(/_/g, " ")}</span>
							</div>
						)}

						{favouriteJob.deadline && (
							<div className="d-flex align-items-center gap-1 text-muted small">
								<i className="bi bi-calendar-event"></i>
								<span>Deadline: {new Date(favouriteJob.deadline).toLocaleDateString()}</span>
							</div>
						)}

						{favouriteJob.personal_rating != null && (
							<div className="d-flex align-items-center gap-1 small">
								{Array.from({ length: 5 }).map((_, i) => (
									<i
										key={i}
										className={`bi bi-star${i < favouriteJob.personal_rating! ? "-fill" : ""}`}
										style={{ color: i < favouriteJob.personal_rating! ? "var(--primary-mid)" : "var(--bs-secondary-color)", fontSize: "0.9rem" }}
									></i>
								))}
							</div>
						)}

						<button
							className="btn btn-sm w-100"
							style={{
								background: "var(--primary-gradient)",
								color: "white",
								border: "none",
								borderRadius: "0.375rem",
								marginTop: "auto",
							}}
							onClick={handleOpenJob}
						>
							<i className="bi bi-box-arrow-up-right me-1"></i>
							View Job
						</button>
					</div>
				)}
			</DashboardCard>
			<JobModal ref={jobModalRef} />
		</>
	);
};

export default FavouriteJobWidget;
