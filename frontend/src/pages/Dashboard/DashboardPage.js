import React, { useState, useEffect } from "react";
import { Container, Row, Col, Card, Alert, Button } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { useLoading } from "../../contexts/LoadingContext";
import { api } from "../../services/Api";
import JobsToChase from "../../components/tables/JobsToChase";
import { JobViewModal } from "../../components/modals/JobModal";
import "./DashboardPage.css";

const JobSearchDashboard = () => {
	const { token } = useAuth();
	const { showLoading, hideLoading } = useLoading();
	const [dashboardStats, setDashboardStats] = useState({
		totalJobs: 0,
		totalApplications: 0,
		pendingApplications: 0,
		interviewsScheduled: 0,
		jobsNeedingChase: 0,
		recentActivity: [],
		applicationsByStatus: {},
	});
	const [chaseJobsData, setChaseJobsData] = useState([]);
	const [error, setError] = useState(null);
	const [selectedJob, setSelectedJob] = useState(null);
	const [showJobModal, setShowJobModal] = useState(false);

	useEffect(() => {
		const fetchDashboardData = async () => {
			try {
				showLoading("Loading dashboard data...");

				// Fetch various statistics using the new dedicated routes
				const [
					jobsResponse,
					applicationsResponse,
					interviewsResponse,
					chaseApplicationsResponse,
					recentUpdatesResponse,
				] = await Promise.all([
					api.get("jobs/", token),
					api.get("jobapplications/", token),
					api.get("interviews/", token),
					api.get("jobapplications/needs_chase", token),
					api.get("latest_updates", token),
				]);

				// Store the chase applications data for passing to the table
				setChaseJobsData(chaseApplicationsResponse || []);

				// Calculate statistics
				const applications = applicationsResponse || [];
				const statusCounts = applications.reduce((acc, app) => {
					acc[app.status] = (acc[app.status] || 0) + 1;
					return acc;
				}, {});

				const pendingStatuses = ["Applied", "Under Review", "Interview Scheduled"];
				const pendingCount = applications.filter((app) => pendingStatuses.includes(app.status)).length;

				// Get upcoming interviews (next 7 days)
				const nextWeek = new Date();
				nextWeek.setDate(nextWeek.getDate() + 7);
				const upcomingInterviews = (interviewsResponse || []).filter((interview) => {
					const interviewDate = new Date(interview.date);
					return interviewDate >= new Date() && interviewDate <= nextWeek;
				});

				setDashboardStats({
					totalJobs: jobsResponse?.length || 0,
					totalApplications: applications.length,
					pendingApplications: pendingCount,
					interviewsScheduled: upcomingInterviews.length,
					jobsNeedingChase: chaseApplicationsResponse?.length || 0,
					recentActivity: recentUpdatesResponse || [],
					applicationsByStatus: statusCounts,
				});
			} catch (err) {
				console.error("Error fetching dashboard data:", err);
				setError("Failed to load dashboard data. Please try again later.");
			} finally {
				hideLoading();
			}
		};

		fetchDashboardData();
	}, [token]); // Remove showLoading and hideLoading from dependencies
	// Function to handle job button click
	const handleJobClick = async (jobTitle) => {
		try {
			showLoading("Loading job details...");
			// Find the job by title from the jobs data we already have
			const jobsResponse = await api.get("jobs/", token);
			const job = jobsResponse.find((j) => j.itemName === jobTitle);

			if (job) {
				setSelectedJob(job);
				setShowJobModal(true);
			}
		} catch (err) {
			console.error("Error fetching job details:", err);
		} finally {
			hideLoading();
		}
	};

	// Callback to handle updates from the JobsToChase table
	const handleChaseJobsUpdate = (updatedApplications) => {
		setChaseJobsData(updatedApplications);
		setDashboardStats((prev) => ({
			...prev,
			jobsNeedingChase: updatedApplications.length,
		}));
	};

	// Rest of your component remains the same...
	const StatCard = ({ itemName, value, icon, variant, description }) => (
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

	const RecentActivityCard = () => (
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
						{dashboardStats.recentActivity.map((activity, index) => {
							const isLast = index === dashboardStats.recentActivity.length - 1;

							// Activity type icon mapping - updated for new types
							const getActivityIcon = (type) => {
								const iconMap = {
									Application: "bi-send-fill",
									Interview: "bi-people-fill",
									"Job Application Update": "bi-pencil-fill",
									"Follow-up": "bi-telephone-fill",
								};
								return iconMap[type] || "bi-plus-circle-fill";
							};

							// Activity type color mapping - updated for new types
							const getActivityColor = (type) => {
								const colorMap = {
									Application: "#3b82f6",
									Interview: "#8b5cf6",
									"Job Application Update": "#6b7280",
								};
								return colorMap[type] || "#3b82f6";
							};

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

											{/* Job title as clickable button */}
											{activity.job_title && (
												<div className="mt-1 mb-2">
													<Button
														variant="link"
														size="sm"
														className="p-0 text-primary fw-medium text-decoration-none"
														style={{ fontSize: "0.85rem" }}
														onClick={() => handleJobClick(activity.job_title)}
													>
														<i className="bi bi-briefcase me-1"></i>
														{activity.job_title}
													</Button>
												</div>
											)}

											{/* Note/description if available */}
											{activity.note && (
												<div className="text-muted small lh-sm" style={{ fontSize: "0.85rem" }}>
													{activity.note.length > 120
														? `${activity.note.substring(0, 120)}...`
														: activity.note}
												</div>
											)}
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
						title="Total Jobs"
						value={dashboardStats.totalJobs}
						icon="briefcase"
						variant="primary"
						description="Jobs in your database"
					/>
				</Col>
				<Col md={6} lg={3}>
					<StatCard
						title="Applications"
						value={dashboardStats.totalApplications}
						icon="send"
						variant="success"
						description="Total applications sent"
					/>
				</Col>
				<Col md={6} lg={3}>
					<StatCard
						title="Pending"
						value={dashboardStats.pendingApplications}
						icon="clock"
						variant="warning"
						description="Awaiting response"
					/>
				</Col>
				<Col md={6} lg={3}>
					<StatCard
						title="Need Follow-up"
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
							<JobsToChase initialData={chaseJobsData} onDataChange={handleChaseJobsUpdate} />
						</Card.Body>
					</Card>
				</Col>
			</Row>

			{/* Job Modal */}
			{selectedJob && (
				<JobViewModal
					show={showJobModal}
					onHide={() => {
						setShowJobModal(false);
						setSelectedJob(null);
					}}
					data={selectedJob}
					jobData={selectedJob}
					jobSubmode="view"
					onJobSuccess={(updatedJob) => {
						// Handle job update if needed
						console.log("Job updated:", updatedJob);
					}}
				/>
			)}
		</Container>
	);
};

export default JobSearchDashboard;
