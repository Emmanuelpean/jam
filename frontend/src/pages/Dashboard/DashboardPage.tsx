import React, { JSX, useEffect, useState } from "react";
import { Alert, Card, Col, Container, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { useLoading } from "../../contexts/LoadingContext";
import { dashboardApi } from "../../services/Api";
import "./DashboardPage.css";
import { getTableIcon, renderFunctions } from "../../components/rendering/view/ViewRenders";
import { ApplicationData, InterviewData, JobApplicationUpdateData, JobData } from "../../services/Schemas";
import JobsToChase from "../../components/tables/JobsToChase";
import UpcomingDeadlinesTable from "../../components/tables/UpcomingDeadlines";
import { formatActivityDate } from "../../utils/TimeUtils";

interface StatCardProps {
	itemName: string;
	value: number;
	icon: string;
	variant: string;
	description?: string;
}

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

interface TableCardHeaderProps {
	icon: string;
	title: string;
	subtitle: string;
	badgeValue?: number;
}

const TableCardHeader: React.FC<TableCardHeaderProps> = ({ icon, title, subtitle, badgeValue }) => (
	<Card.Header className="table-card-header border-0 p-0">
		<div className="d-flex align-items-center justify-content-between p-4">
			<div className="d-flex align-items-center">
				<div className="header-icon-wrapper me-3">
					<i className={`bi bi-${icon}`}></i>
				</div>
				<div>
					<h5 className="mb-0 fw-bold text-dark">{title}</h5>
					<small className="text-muted">{subtitle}</small>
				</div>
			</div>
			{badgeValue && badgeValue > 0 && <div className={"table-count-badge"}>{badgeValue}</div>}
		</div>
	</Card.Header>
);

interface ActivityFeedCardProps<T> {
	icon: string;
	title: string;
	subtitle: string;
	badgeValue: number;
	emptyIcon: string;
	emptyTitle: string;
	emptyDescription: string;
	items: T[];
	renderItem: (item: T, index: number, isLast: boolean) => JSX.Element;
}

const ActivityFeedCard = <T,>({
	icon,
	title,
	subtitle,
	badgeValue,
	emptyIcon,
	emptyTitle,
	emptyDescription,
	items,
	renderItem,
}: ActivityFeedCardProps<T>) => (
	<Card className="h-100 shadow-sm border-0 d-flex flex-column">
		<TableCardHeader icon={icon} title={title} subtitle={subtitle} badgeValue={badgeValue} />
		<Card.Body className="p-0 flex-grow-1 d-flex flex-column" style={{ minHeight: 0 }}>
			{items.length === 0 ? (
				<div className="text-center py-5 px-4 flex-grow-1 d-flex flex-column justify-content-center">
					<div className="mb-3">
						<i className={`bi bi-${emptyIcon} text-muted`} style={{ fontSize: "3.5rem" }}></i>
					</div>
					<h6 className="text-muted fw-semibold">{emptyTitle}</h6>
					<p className="text-muted small mb-0">{emptyDescription}</p>
				</div>
			) : (
				<div
					className="activity-timeline px-4 flex-grow-1"
					style={{ overflowY: "auto", height: "100%", minHeight: 0 }}
				>
					{items.map((item, index) => renderItem(item, index, index === items.length - 1))}
				</div>
			)}
		</Card.Body>
	</Card>
);

interface RecentActivity {
	data: JobApplicationUpdateData | InterviewData | ApplicationData;
	type: string;
	date: string;
	job: JobData;
}

const renderRecentActivityItem = (activity: RecentActivity, index: number, isLast: boolean): JSX.Element => {
	const getActivityIcon = (type: string): string => {
		const iconMap: { [key: string]: string } = {
			Application: getTableIcon("Job Applications"),
			Interview: getTableIcon("Interviews"),
			"Job Application Update": getTableIcon("Job Application Updates"),
		};
		return iconMap[type] || "bi-plus-circle-fill";
	};

	const getActivityColor = (type: string): string => {
		const colorMap: { [key: string]: string } = {
			Application: "#2563eb",
			Interview: "#10b981",
			"Job Application Update": "#f59e42",
		};
		return colorMap[type] || "#2563eb";
	};

	const activityColor = getActivityColor(activity.type);
	const activityIcon = getActivityIcon(activity.type);

	return (
		<div key={`activity-${index}`} className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
			<div className="d-flex position-relative">
				{/* Timeline line */}
				{!isLast && <div className="position-absolute activity-line"></div>}

				{/* Activity icon */}
				<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
					<div
						className="rounded-circle d-flex align-items-center justify-content-center"
						style={{
							width: "35px",
							height: "35px",
							backgroundColor: activityColor,
						}}
					>
						<i className={`bi ${activityIcon} text-white`} style={{ fontSize: "1rem" }}></i>
					</div>
				</div>

				{/* Activity content */}
				<div className="flex-grow-1 min-width-0">
					<div className="d-flex align-items-start justify-content-between mb-1">
						<div className="fw-semibold text-dark" style={{ fontSize: "1rem" }}>
							{activity.type}
						</div>
						<small className="text-muted flex-shrink-0 ms-2">{formatActivityDate(activity.date)}</small>
					</div>
					{renderFunctions.jobBadge({ item: activity })}
				</div>
			</div>
		</div>
	);
};

const renderUpcomingInterviewItem = (interview: InterviewData, index: number, isLast: boolean): JSX.Element => {
	return (
		<div key={`interview-${index}`} className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
			<div className="d-flex position-relative">
				{/* Timeline line */}
				{!isLast && <div className="position-absolute activity-line"></div>}
				{/* Interview icon */}
				<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
					<div
						className="rounded-circle d-flex align-items-center justify-content-center"
						style={{
							width: "35px",
							height: "35px",
							backgroundColor: "#8b5cf6",
						}}
					>
						<i className="bi bi-people-fill text-white" style={{ fontSize: "1rem" }}></i>
					</div>
				</div>
				{/* Interview content */}
				<div className="flex-grow-1 min-width-0">
					<div className="d-flex align-items-start justify-content-between mb-1">
						<div className="fw-semibold text-dark" style={{ fontSize: "0.95rem" }}>
							{interview.type}
						</div>
						<small className="text-muted flex-shrink-0 ms-2">{formatActivityDate(interview.date!)}</small>
					</div>
					{renderFunctions.jobBadge({ item: { job: interview.job } })}
				</div>
			</div>
		</div>
	);
};

interface DashboardStats {
	totalJobs: number;
	totalApplications: number;
	pendingApplications: number;
	interviewsScheduled: number;
	jobsNeedingChase: number;
	recentActivity: RecentActivity[];
	upcomingInterviews: InterviewData[];
	jobsToChase: JobData[];
	upcomingDeadlines: JobData[];
}

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
		upcomingInterviews: [],
		jobsToChase: [],
		upcomingDeadlines: [],
	});
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
				const upcomingInterviews = dashboardResponse?.upcoming_interviews || [];
				const upcomingDeadlines = dashboardResponse?.upcoming_deadlines || [];

				setDashboardStats({
					totalJobs: statistics.jobs,
					totalApplications: statistics.job_applications,
					pendingApplications: statistics.job_application_pending,
					interviewsScheduled: statistics.interviews,
					jobsNeedingChase: needsChase.length,
					recentActivity: allUpdates,
					upcomingInterviews: upcomingInterviews,
					jobsToChase: needsChase,
					upcomingDeadlines: upcomingDeadlines,
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

	if (error) {
		return (
			<Container fluid className="py-4">
				<Alert variant="danger">{error}</Alert>
			</Container>
		);
	}

	return (
		<>
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
						description="Applications awaiting response"
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
			<Row className="g-4" style={{ height: "500px", minHeight: 0 }}>
				<Col lg={4} style={{ height: "100%", minHeight: 0 }}>
					<ActivityFeedCard
						icon="clock-history"
						title="Recent Activity"
						subtitle="Latest job applications, interviews and updates"
						badgeValue={dashboardStats.recentActivity.length}
						emptyIcon="inbox"
						emptyTitle="No recent activity"
						emptyDescription="Your recent activity will appear here"
						items={dashboardStats.recentActivity}
						renderItem={renderRecentActivityItem}
					/>
				</Col>
				<Col lg={8} style={{ height: "100%", minHeight: 0, display: "flex", flexDirection: "column" }}>
					<Card
						className="shadow-sm border-0 flex-grow-1 d-flex flex-column"
						style={{ height: "100%", minHeight: 0 }}
					>
						<TableCardHeader
							icon="telephone"
							title="Applications Requiring Follow-up"
							subtitle="Jobs that need your attention"
							badgeValue={dashboardStats.jobsNeedingChase}
						/>
						<Card.Body
							className="p-0 flex-grow-1"
							style={{ marginLeft: "1rem", marginRight: "1rem", overflowY: "auto", minHeight: 0 }}
						>
							<JobsToChase data={dashboardStats.jobsToChase} />
						</Card.Body>
					</Card>
				</Col>
			</Row>
			<Row className="g-4" style={{ height: "500px", minHeight: 0, paddingTop: "3rem" }}>
				<Col lg={8} style={{ height: "100%", minHeight: 0, display: "flex", flexDirection: "column" }}>
					<Card
						className="shadow-sm border-0 flex-grow-1 d-flex flex-column"
						style={{ height: "100%", minHeight: 0 }}
					>
						<TableCardHeader
							icon="clock"
							title="Upcoming Deadlines"
							subtitle="Jobs that need your attention"
							badgeValue={dashboardStats.upcomingDeadlines.length}
						/>
						<Card.Body className="p-0" style={{ marginLeft: "1rem", marginRight: "1rem" }}>
							<UpcomingDeadlinesTable data={dashboardStats.upcomingDeadlines} />
						</Card.Body>
					</Card>
				</Col>
				<Col lg={4} style={{ height: "100%", minHeight: 0, display: "flex", flexDirection: "column" }}>
					<ActivityFeedCard
						icon="calendar-event"
						title="Upcoming Interviews"
						subtitle="Scheduled interviews"
						badgeValue={dashboardStats.upcomingInterviews.length}
						emptyIcon="calendar-x"
						emptyTitle="No upcoming interviews"
						emptyDescription="Your scheduled interviews will appear here"
						items={dashboardStats.upcomingInterviews}
						renderItem={renderUpcomingInterviewItem}
					/>
				</Col>
			</Row>
		</>
	);
};

export default JobSearchDashboard;
