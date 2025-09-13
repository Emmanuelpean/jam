import React, { JSX, useEffect, useState } from "react";
import { Alert, Card, Col, Container, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { useLoading } from "../../contexts/LoadingContext";
import { api, dashboardApi } from "../../services/Api";
import "./DashboardPage.css";
import { renderFunctions } from "../../components/rendering/view/ViewRenders";
import { ApplicationData, InterviewData, JobApplicationUpdateData, JobData } from "../../services/Schemas";
import JobsToChase from "../../components/tables/JobsToChase";

interface DashboardStats {
	totalJobs: number;
	totalApplications: number;
	pendingApplications: number;
	interviewsScheduled: number;
	jobsNeedingChase: number;
	recentActivity: RecentActivity[];
}

interface RecentActivity {
	data: JobApplicationUpdateData | InterviewData | ApplicationData;
	type: string;
	date: string;
	job: JobData;
}

interface ChaseJobData {
	id: number;
	status: string;

	[key: string]: any;
}

interface StatCardProps {
	itemName: string;
	value: number;
	icon: string;
	variant: string;
	description?: string;
}

const getActivityIcon = (type: string): string => {
	const iconMap: { [key: string]: string } = {
		Application: "bi-send-fill",
		Interview: "bi-people-fill",
		"Job Application Update": "bi-pencil-fill",
		"Follow-up": "bi-telephone-fill",
	};
	return iconMap[type] || "bi-plus-circle-fill";
};

const getActivityColor = (type: string): string => {
	const colorMap: { [key: string]: string } = {
		Application: "#3b82f6",
		Interview: "#8b5cf6",
		"Job Application Update": "#6b7280",
	};
	return colorMap[type] || "#3b82f6";
};

const JobSearchDashboard: React.FC = () => {
	const { token } = useAuth();
	const { showLoading, hideLoading } = useLoading();
	const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
		totalJobs: 0,
		totalApplications: 0,
		pendingApplications: 0,
		interviewsScheduled: 0,
		jobsNeedingChase: 0,
		recentActivity: [],
	});
	const [chaseJobsData, setChaseJobsData] = useState<ChaseJobData[]>([]);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const fetchDashboardData = async (): Promise<void> => {
			try {
				showLoading("Loading dashboard data...");

				if (!token) {
					throw new Error("User is not authenticated");
				}
				const dashboardResponse = await dashboardApi.getAll(token);

				const statistics = dashboardResponse?.statistics || {
					jobs: 0,
					job_applications: 0,
					job_application_pending: 0,
					interviews: 0,
				};
				const needsChase = dashboardResponse?.needs_chase || [];
				const allUpdates = dashboardResponse?.all_updates || [];

				setChaseJobsData(needsChase);

				setDashboardStats({
					totalJobs: statistics.jobs,
					totalApplications: statistics.job_applications,
					pendingApplications: statistics.job_application_pending,
					interviewsScheduled: statistics.interviews,
					jobsNeedingChase: needsChase.length,
					recentActivity: allUpdates,
				});
			} catch (err) {
				console.error("Error fetching dashboard data:", err);
				setError("Failed to load dashboard data. Please try again later.");
			} finally {
				hideLoading();
			}
		};

		fetchDashboardData().then(() => null);
	}, [token]);

	const StatCard: React.FC<StatCardProps> = ({
		itemName,
		value,
		icon,
		variant,
		description,
	}: StatCardProps): JSX.Element => (
		<Card className="h-100 shadow-sm border-0">
			<Card.Body className="d-flex align-items-center">
				<div className="flex-grow-1">
					<div className="d-flex align-items-center mb-2">
						<i className={`bi bi-${icon} text-${variant} me-2`} style={{ fontSize: "1.5rem" }}></i>
						<h5 className="card-itemName mb-0">{itemName}</h5>
					</div>
					<div className={`display-6 fw-bold text-${variant}`}>{value}</div>
					{description && <small className="text-muted">{description}</small>}
				</div>
			</Card.Body>
		</Card>
	);

	const RecentActivityCard: React.FC = (): JSX.Element => (
		<Card className="h-100 shadow-sm border-0">
			<Card.Header className="card-header border-0 p-0">
				<div className="d-flex align-items-center justify-content-between p-4">
					<div className="d-flex align-items-center">
						<div className="header-icon-wrapper me-3">
							<i className="bi bi-clock-history"></i>
						</div>
						<div>
							<h5 className="mb-0 fw-bold text-dark">Recent Activity</h5>
							<small className="text-muted">Latest updates across all activities</small>
						</div>
					</div>
					{dashboardStats.recentActivity.length > 0 && (
						<div className="activity-count-badge">{dashboardStats.recentActivity.length}</div>
					)}
				</div>
			</Card.Header>
			<Card.Body className="p-0">
				{dashboardStats.recentActivity.length === 0 ? (
					<div className="text-center py-5 px-4">
						<div className="mb-3">
							<i className="bi bi-inbox text-muted" style={{ fontSize: "3.5rem" }}></i>
						</div>
						<h6 className="text-muted fw-semibold">No recent activity</h6>
						<p className="text-muted small mb-0">Your recent activity will appear here</p>
					</div>
				) : (
					<div className="activity-timeline px-4" style={{ maxHeight: "400px", overflowY: "auto" }}>
						{dashboardStats.recentActivity.map((activity: RecentActivity, index) => {
							const isLast = index === dashboardStats.recentActivity.length - 1;

							const activityColor = getActivityColor(activity.type);
							const activityIcon = getActivityIcon(activity.type);

							return (
								<div key={`activity-${index}`} className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
									<div className="d-flex position-relative">
										{/* Timeline line */}
										{!isLast && (
											<div
												className="position-absolute"
												style={{
													left: "15px",
													top: "40px",
													width: "2px",
													height: "calc(100% + 8px)",
													backgroundColor: "#e5e7eb",
													zIndex: 0,
												}}
											></div>
										)}

										{/* Activity icon */}
										<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
											<div
												className="rounded-circle d-flex align-items-center justify-content-center"
												style={{
													width: "32px",
													height: "32px",
													backgroundColor: activityColor,
													boxShadow: `0 0 0 3px rgba(${parseInt(activityColor.slice(1, 3), 16)}, ${parseInt(activityColor.slice(3, 5), 16)}, ${parseInt(activityColor.slice(5, 7), 16)}, 0.1)`,
												}}
											>
												<i
													className={`bi ${activityIcon} text-white`}
													style={{ fontSize: "0.9rem" }}
												></i>
											</div>
										</div>

										{/* Activity content */}
										<div className="flex-grow-1 min-width-0">
											<div className="d-flex align-items-start justify-content-between mb-1">
												<div className="fw-semibold text-dark" style={{ fontSize: "0.95rem" }}>
													{activity.type}
												</div>
												<small className="text-muted flex-shrink-0 ms-2">
													{new Date(activity.date).toLocaleDateString("en-US", {
														month: "short",
														day: "numeric",
														...(new Date().getFullYear() !==
															new Date(activity.date).getFullYear() && {
															year: "numeric",
														}),
													})}
												</small>
											</div>

											{renderFunctions.jobBadge({ item: activity })}
										</div>
									</div>
								</div>
							);
						})}
					</div>
				)}
			</Card.Body>
		</Card>
	);

	if (error) {
		return (
			<Container fluid className="py-4">
				<Alert variant="danger">{error}</Alert>
			</Container>
		);
	}

	return (
		<Container fluid className="py-4">
			{/* Statistics Cards */}
			<Row className="g-4 mb-4">
				<Col md={6} lg={3}>
					<StatCard
						itemName="Total Jobs"
						value={dashboardStats.totalJobs}
						icon="briefcase"
						variant="primary"
						description="Jobs in your database"
					/>
				</Col>
				<Col md={6} lg={3}>
					<StatCard
						itemName="Applications"
						value={dashboardStats.totalApplications}
						icon="send"
						variant="success"
						description="Total applications sent"
					/>
				</Col>
				<Col md={6} lg={3}>
					<StatCard
						itemName="Pending"
						value={dashboardStats.pendingApplications}
						icon="clock"
						variant="warning"
						description="Awaiting response"
					/>
				</Col>
				<Col md={6} lg={3}>
					<StatCard
						itemName="Need Follow-up"
						value={dashboardStats.jobsNeedingChase}
						icon="telephone"
						variant="danger"
						description="Applications requiring action"
					/>
				</Col>
			</Row>

			<Row className="g-4">
				<Col lg={3}>
					<RecentActivityCard />
				</Col>
				<Col lg={9}>
					<Card className="shadow-sm border-0">
						<Card.Header className="table-card-header border-0 p-0">
							<div className="d-flex align-items-center justify-content-between p-4">
								<div className="d-flex align-items-center">
									<div className="header-icon-wrapper me-3">
										<i className="bi bi-telephone-outbound"></i>
									</div>
									<div>
										<h5 className="mb-0 fw-bold text-dark">Applications Requiring Follow-up</h5>
										<small className="text-muted">Jobs that need your attention</small>
									</div>
								</div>
								{dashboardStats.jobsNeedingChase > 0 && (
									<div className="table-count-badge">{dashboardStats.jobsNeedingChase}</div>
								)}
							</div>
						</Card.Header>
						<Card.Body className="p-0" style={{ marginLeft: "1rem", marginRight: "1rem" }}>
							<JobsToChase data={chaseJobsData} />
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
};

export default JobSearchDashboard;
