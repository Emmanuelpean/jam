import React, { useState, useEffect } from "react";
import { Container, Row, Col, Card, Alert } from "react-bootstrap";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../services/api";
import JobsToChase from "../components/tables/JobsToChase";

const JobSearchDashboard = () => {
	const { token } = useAuth();
	const [dashboardStats, setDashboardStats] = useState({
		totalJobs: 0,
		totalApplications: 0,
		pendingApplications: 0,
		interviewsScheduled: 0,
		jobsNeedingChase: 0,
		recentActivity: [],
		applicationsByStatus: {},
	});
	const [chaseJobsData, setChaseJobsData] = useState([]); // Store the actual jobs needing chase
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		const fetchDashboardData = async () => {
			try {
				setLoading(true);

				// Fetch various statistics using the new dedicated route
				const [
					jobsResponse,
					applicationsResponse,
					interviewsResponse,
					chaseJobsResponse,
					recentUpdatesResponse,
				] = await Promise.all([
					api.get("jobs/", token),
					api.get("jobapplications/", token),
					api.get("interviews/", token),
					api.get("jobs/needs_chase", token), // Use the new dedicated route
					api.get("jobapplicationupdates/?limit=5", token),
				]);

				// Store the chase jobs data for passing to the table
				setChaseJobsData(chaseJobsResponse || []);

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
					jobsNeedingChase: chaseJobsResponse?.length || 0,
					recentActivity: recentUpdatesResponse || [],
					applicationsByStatus: statusCounts,
				});
			} catch (err) {
				console.error("Error fetching dashboard data:", err);
				setError("Failed to load dashboard data. Please try again later.");
			} finally {
				setLoading(false);
			}
		};

		fetchDashboardData();
	}, [token]);

	// Callback to handle updates from the JobsToChase table
	const handleChaseJobsUpdate = (updatedJobs) => {
		setChaseJobsData(updatedJobs);
		// Also update the count in dashboard stats
		setDashboardStats((prev) => ({
			...prev,
			jobsNeedingChase: updatedJobs.length,
		}));
	};

	const StatCard = ({ title, value, icon, variant, description }) => (
		<Card className="h-100 shadow-sm border-0">
			<Card.Body className="d-flex align-items-center">
				<div className="flex-grow-1">
					<div className="d-flex align-items-center mb-2">
						<i className={`bi bi-${icon} text-${variant} me-2`} style={{ fontSize: "1.5rem" }}></i>
						<h5 className="card-title mb-0">{title}</h5>
					</div>
					<div className={`display-6 fw-bold text-${variant}`}>{value}</div>
					{description && <small className="text-muted">{description}</small>}
				</div>
			</Card.Body>
		</Card>
	);

	const RecentActivityCard = () => (
		<Card className="h-100 shadow-sm border-0">
			<Card.Header className="bg-light">
				<h5 className="mb-0 d-flex align-items-center">
					<i className="bi bi-clock-history me-2"></i>
					Recent Activity
				</h5>
			</Card.Header>
			<Card.Body>
				{dashboardStats.recentActivity.length === 0 ? (
					<div className="text-center text-muted py-3">
						<i className="bi bi-inbox" style={{ fontSize: "2rem" }}></i>
						<p className="mt-2 mb-0">No recent activity</p>
					</div>
				) : (
					<div className="timeline">
						{dashboardStats.recentActivity.slice(0, 5).map((activity, index) => (
							<div key={activity.id || index} className="timeline-item mb-3">
								<div className="d-flex">
									<div className="flex-shrink-0 me-3">
										<div className="bg-primary rounded-circle p-2">
											<i className="bi bi-plus text-white"></i>
										</div>
									</div>
									<div className="flex-grow-1">
										<div className="fw-semibold">{activity.type}</div>
										<div className="text-muted small">
											{activity.note && activity.note.length > 100
												? `${activity.note.substring(0, 100)}...`
												: activity.note || "No details provided"}
										</div>
										<div className="text-muted small">
											{new Date(activity.date).toLocaleDateString()}
										</div>
									</div>
								</div>
							</div>
						))}
					</div>
				)}
			</Card.Body>
		</Card>
	);

	const ApplicationStatusCard = () => (
		<Card className="h-100 shadow-sm border-0">
			<Card.Header className="bg-light">
				<h5 className="mb-0 d-flex align-items-center">
					<i className="bi bi-pie-chart me-2"></i>
					Application Status Overview
				</h5>
			</Card.Header>
			<Card.Body>
				{Object.keys(dashboardStats.applicationsByStatus).length === 0 ? (
					<div className="text-center text-muted py-3">
						<i className="bi bi-clipboard-x" style={{ fontSize: "2rem" }}></i>
						<p className="mt-2 mb-0">No applications yet</p>
					</div>
				) : (
					<div>
						{Object.entries(dashboardStats.applicationsByStatus).map(([status, count]) => {
							const percentage = (count / dashboardStats.totalApplications) * 100;
							const statusColors = {
								Applied: "primary",
								"Under Review": "warning",
								"Interview Scheduled": "info",
								Rejected: "danger",
								Accepted: "success",
								Withdrawn: "secondary",
							};
							const color = statusColors[status] || "secondary";

							return (
								<div key={status} className="mb-3">
									<div className="d-flex justify-content-between align-items-center mb-1">
										<span className="fw-semibold">{status}</span>
										<span className="badge bg-light text-dark">{count}</span>
									</div>
									<div className="progress" style={{ height: "8px" }}>
										<div
											className={`progress-bar bg-${color}`}
											role="progressbar"
											style={{ width: `${percentage}%` }}
											aria-valuenow={percentage}
											aria-valuemin="0"
											aria-valuemax="100"
										></div>
									</div>
								</div>
							);
						})}
					</div>
				)}
			</Card.Body>
		</Card>
	);

	if (loading) {
		return (
			<Container fluid className="py-4">
				<div className="d-flex justify-content-center mt-5">
					<div className="spinner-border" role="status">
						<span className="visually-hidden">Loading...</span>
					</div>
				</div>
			</Container>
		);
	}

	if (error) {
		return (
			<Container fluid className="py-4">
				<Alert variant="danger">{error}</Alert>
			</Container>
		);
	}

	return (
		<Container fluid className="py-4">
			{/* Page Header */}
			<div className="d-flex justify-content-between align-items-center mb-4">
				<div>
					<h1 className="h3 mb-0">Job Search Dashboard</h1>
					<p className="text-muted mb-0">Track your job search progress and follow-ups</p>
				</div>
			</div>

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
						description="Jobs requiring action"
					/>
				</Col>
			</Row>

			{/* Alert for jobs needing follow-up */}
			{dashboardStats.jobsNeedingChase > 0 && (
				<Alert variant="warning" className="mb-4">
					<div className="d-flex align-items-center">
						<i className="bi bi-exclamation-triangle me-2"></i>
						<div>
							<strong>Action Required:</strong> You have {dashboardStats.jobsNeedingChase} job application
							{dashboardStats.jobsNeedingChase > 1 ? "s" : ""} that need follow-up. Check the table below
							for details.
						</div>
					</div>
				</Alert>
			)}

			{/* Secondary Statistics and Activity */}
			<Row className="g-4 mb-4">
				<Col lg={4}>
					<ApplicationStatusCard />
				</Col>
				<Col lg={8}>
					<RecentActivityCard />
				</Col>
			</Row>

			{/* Jobs to Chase Table */}
			<Row>
				<Col>
					<Card className="shadow-sm border-0">
						<Card.Body className="p-0">
							<JobsToChase
								initialData={chaseJobsData}
								onDataChange={handleChaseJobsUpdate}
								loading={loading}
							/>
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
};

export default JobSearchDashboard;
