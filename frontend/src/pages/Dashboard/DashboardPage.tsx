import React, { useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import "./DashboardPage.css";
import { EnrichedInterviewData, EnrichedJobApplicationUpdateData, EnrichedJobData } from "../../services/Schemas";
import JobsToChase from "../../components/tables/JobsToChase";
import UpcomingDeadlinesTable from "../../components/tables/UpcomingDeadlines";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { StatCard } from "./StatCard";
import { CardHeader } from "./CardHeader";
import {
	ActivityFeedCard,
	RecentActivity,
	renderRecentActivityItem,
	renderUpcomingInterviewItem,
} from "./ActivityFeed";
import ScrapedJobsTable from "../../components/tables/ScrapedJobTable";
import { scrapedJobApi } from "../../services/Api";

const Dashboard: React.FC = () => {
	const dataContext: DataContextValue = useDataContext();
	const { token } = useAuth();
	const { currentUser } = useAuth();
	const [scrapedJobCount, setScrapedJobCount] = useState<number>(0);
	if (!currentUser) {
		return null;
	}
	const now = new Date();

	const jobApplications: EnrichedJobData[] = dataContext.jobs.filter(
		(job: EnrichedJobData): Date | string | null | undefined => job.application_date || job.application_status,
	);

	const jobApplicationPending: EnrichedJobData[] = jobApplications.filter(
		(job: EnrichedJobData): boolean | string | null | undefined =>
			job.application_status && !["rejected", "withdrawn"].includes(job.application_status),
	);

	const needsChase: EnrichedJobData[] = jobApplicationPending.filter(
		(job: EnrichedJobData): boolean | 0 | null | undefined =>
			job.days_since_last_update &&
			job.days_since_last_update > currentUser.chase_threshold &&
			(!job.followup_snooze_datetime || job.followup_snooze_datetime <= now),
	);

	const thresholdDate = new Date(now.getTime() + currentUser.deadline_threshold * 24 * 60 * 60 * 1000);

	const upcomingDeadlines: EnrichedJobData[] = dataContext.jobs.filter(
		(job: EnrichedJobData): boolean | null | undefined =>
			!job.application_date &&
			!job.application_status &&
			job.deadline &&
			new Date(job.deadline) > now &&
			new Date(job.deadline) <= thresholdDate,
	);

	const upcomingInterviews: EnrichedInterviewData[] = dataContext.interviews.filter(
		(interview: EnrichedInterviewData): boolean | null | undefined => new Date(interview.date!) >= now,
	);

	const allUpdates: RecentActivity[] = [];

	// Add job applications as "Application" updates
	jobApplications.forEach((job: EnrichedJobData): void => {
		if (job.application_date) {
			allUpdates.push({
				data: job,
				date: job.application_date,
				type: "Application",
				job_id: job.id,
			});
		}
	});

	// Add interviews as "Interview" updates
	dataContext.interviews.forEach((interview: EnrichedInterviewData): void => {
		if (new Date(interview.date) < now) {
			allUpdates.push({
				data: interview,
				date: interview.date,
				type: "Interview",
				job_id: interview.job_id,
			});
		}
	});

	// Add job application updates
	dataContext.jobApplicationUpdates.forEach((update: EnrichedJobApplicationUpdateData): void => {
		if (new Date(update.date) < now) {
			allUpdates.push({
				data: update,
				date: update.date,
				type: "Job Application Update",
				job_id: update.job_id,
			});
		}
	});

	allUpdates.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
	const recentActivity = allUpdates.slice(0, currentUser.update_limit);

	scrapedJobApi.getCount(token || "").then((count) => {
		console.log(count);
		setScrapedJobCount(count.count);
	});

	return (
		<>
			<Row className="g-4 mb-4">
				<Col xs={6} md={6} lg={3}>
					<StatCard
						name="Total Jobs"
						value={dataContext.jobs.length}
						icon="briefcase"
						variant="primary"
						description="Jobs in your database"
					/>
				</Col>
				<Col xs={6} md={6} lg={3}>
					<StatCard
						name="Applications"
						value={jobApplications.length}
						icon="send"
						variant="success"
						description="Total applications sent"
					/>
				</Col>
				<Col xs={6} md={6} lg={3}>
					<StatCard
						name="Pending"
						value={jobApplicationPending.length}
						icon="clock"
						variant="warning"
						description="Applications awaiting response"
					/>
				</Col>
				<Col xs={6} md={6} lg={3}>
					<StatCard
						name="Need Follow-up"
						value={needsChase.length}
						icon="telephone"
						variant="danger"
						description="Applications requiring action"
					/>
				</Col>
			</Row>

			{/* First section: Recent Activity (left on desktop, top on mobile) and Follow-up Table */}
			<Row className="g-4 mb-4">
				<Col xs={12} lg={4} className="activity-column order-lg-1">
					<ActivityFeedCard
						icon="clock-history"
						title="Recent Activity"
						subtitle="Latest job applications, interviews and updates"
						badgeValue={recentActivity.length}
						emptyIcon="inbox"
						emptyTitle="No recent activity"
						emptyDescription="Your recent activity will appear here"
						items={recentActivity}
						renderItem={renderRecentActivityItem}
					/>
				</Col>
				<Col xs={12} lg={8} className="table-column order-lg-2">
					<Card className="shadow-sm border-0 h-100 d-flex flex-column">
						<CardHeader
							icon="telephone"
							title="Applications Requiring Follow-up"
							subtitle="Jobs that need your attention"
							badgeValue={needsChase.length}
						/>
						<Card.Body className="p-0 flex-grow-1 overflow-auto">
							<div className="px-3">
								<JobsToChase data={needsChase} menuItems={["view", "edit", "snooze", "delete"]} />
							</div>
						</Card.Body>
					</Card>
				</Col>
			</Row>

			{/* Second section: Upcoming Deadlines (left on desktop) and Upcoming Interviews */}
			<Row className="g-4 mb-4">
				<Col xs={12} lg={8} className="table-column order-lg-1">
					<Card className="shadow-sm border-0 h-100 d-flex flex-column">
						<CardHeader
							icon="clock"
							title="Upcoming Deadlines"
							subtitle="Jobs that need your attention"
							badgeValue={upcomingDeadlines.length}
						/>
						<Card.Body className="p-0 flex-grow-1 overflow-auto">
							<div className="px-3">
								<UpcomingDeadlinesTable data={upcomingDeadlines} />
							</div>
						</Card.Body>
					</Card>
				</Col>
				<Col xs={12} lg={4} className="activity-column order-lg-2">
					<ActivityFeedCard
						icon="calendar-event"
						title="Upcoming Interviews"
						subtitle="Scheduled interviews"
						badgeValue={upcomingInterviews.length}
						emptyIcon="calendar-x"
						emptyTitle="No upcoming interviews"
						emptyDescription="Your scheduled interviews will appear here"
						items={upcomingInterviews}
						renderItem={renderUpcomingInterviewItem}
					/>
				</Col>
			</Row>
			{currentUser?.toast_active && (
				<Row className="g-4 mb-4">
					<Col lg={12} className="table-column order-lg-1">
						<Card
							className="shadow-sm border-0 flex-grow-1 d-flex flex-column"
							style={{ height: "100%", minHeight: 0 }}
						>
							<CardHeader
								icon="inbox"
								title="Job Alerts"
								subtitle="Jobs that you received from job boards"
								badgeValue={scrapedJobCount}
							/>
							<Card.Body
								className="p-0 flex-grow-1 d-flex flex-column"
								style={{ height: "100%", minHeight: 0 }}
							>
								<div
									style={{
										flexGrow: 1,
										overflowY: "auto",
										minHeight: 0,
										paddingTop: "10px",
										paddingBottom: "20px",
									}}
								>
									<div style={{ marginLeft: "1rem", marginRight: "1rem" }}>
										<ScrapedJobsTable />
									</div>
								</div>
							</Card.Body>
						</Card>
					</Col>
				</Row>
			)}
		</>
	);
};

export default Dashboard;
