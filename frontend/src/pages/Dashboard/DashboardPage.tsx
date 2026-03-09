import React, { useState } from "react";
import { Col, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import "./DashboardPage.scss";
import {
	EnrichedInterviewData,
	EnrichedJobApplicationUpdateData,
	EnrichedJobData,
} from "../../services/schemas/DataTables";
import JobsToChase from "../../components/DataTable/JobsToChase";
import UpcomingDeadlinesTable from "../../components/DataTable/UpcomingDeadlines";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { StatCard } from "./StatCard";
import { DashboardCard } from "./DashboardCard";
import {
	ActivityFeedCard,
	RecentActivity,
	renderRecentActivityItem,
	renderUpcomingInterviewItem,
} from "./ActivityFeed";
import ScrapedJobsTable from "../../components/DataTable/ScrapedJobTable";
import { scrapedJobApi } from "../../services/api/Services";
import { sortByKey } from "../../utils/Utils";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import ExtensionBanner from "./ExtensionBanner";

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
		(job: EnrichedJobData): Date | string | null | undefined => job.application_date || job.application_status
	);

	const jobApplicationPending: EnrichedJobData[] = jobApplications.filter(
		(job: EnrichedJobData): boolean | string | null | undefined =>
			job.application_status && !["rejected", "withdrawn"].includes(job.application_status)
	);

	const needsChase: EnrichedJobData[] = jobApplicationPending.filter(
		(job: EnrichedJobData) =>
			job.days_since_last_update &&
			job.days_since_last_update > currentUser.preferences.chase_threshold &&
			(!job.followup_snooze_datetime || job.followup_snooze_datetime <= now) &&
			job.application_status &&
			!["rejected", "offer", "withdrawn"].includes(job.application_status)
	);

	const thresholdDate = new Date(now.getTime() + currentUser.preferences.deadline_threshold * 24 * 60 * 60 * 1000);

	const upcomingDeadlines: EnrichedJobData[] = dataContext.jobs.filter(
		(job: EnrichedJobData) =>
			!job.application_date &&
			!job.application_status &&
			job.deadline &&
			new Date(job.deadline) > now &&
			new Date(job.deadline) <= thresholdDate
	);

	const upcomingInterviews: EnrichedInterviewData[] = sortByKey(
		dataContext.interviews.filter(
			(interview: EnrichedInterviewData): boolean | null | undefined => new Date(interview.date!) >= now
		),
		"date"
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
	const recentActivity = allUpdates.slice(0, currentUser.preferences.update_limit);

	scrapedJobApi.getCount(token || "").then((count) => {
		setScrapedJobCount(count.data.count);
	});

	return (
		<>
			<ExtensionBanner />
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
						badgeValue={recentActivity.length}
						emptyIcon="inbox"
						emptyTitle="No recent activity"
						emptyDescription="Your recent activity will appear here"
						items={recentActivity}
						renderItem={renderRecentActivityItem}
					/>
				</Col>
				<Col xs={12} lg={8} className="table-column order-lg-2">
					<DashboardCard
						icon="telephone"
						title="Applications Requiring Follow-up"
						badgeValue={needsChase.length}
						isEmpty={needsChase.length === 0}
						emptyState={{
							icon: "telephone-x",
							title: "No follow-ups needed",
							description: "All your applications are up to date",
						}}
					>
						<JobsToChase data={needsChase} />
					</DashboardCard>
				</Col>
			</Row>

			{/* Second section: Upcoming Deadlines (left on desktop) and Upcoming Interviews */}
			<Row className="g-4 mb-4">
				<Col xs={12} lg={8} className="table-column order-lg-1">
					<DashboardCard
						icon="clock"
						title="Upcoming Deadlines"
						badgeValue={upcomingDeadlines.length}
						isEmpty={upcomingDeadlines.length === 0}
						emptyState={{
							icon: "calendar-check",
							title: "No upcoming deadlines",
							description: "You have no application deadlines approaching",
						}}
					>
						<UpcomingDeadlinesTable data={upcomingDeadlines} />
					</DashboardCard>
				</Col>
				<Col xs={12} lg={4} className="activity-column order-lg-2">
					<ActivityFeedCard
						icon="calendar-event"
						title="Upcoming Interviews"
						badgeValue={upcomingInterviews.length}
						emptyIcon="calendar-x"
						emptyTitle="No upcoming interviews"
						emptyDescription="Your scheduled interviews will appear here"
						items={upcomingInterviews}
						renderItem={renderUpcomingInterviewItem}
					/>
				</Col>
			</Row>
			{currentUser?.premium.is_active && (
				<Row className="g-4 mb-4">
					<Col lg={12} className="toast-table order-lg-1">
						<DashboardCard
							icon={getEntityIcon("scrapedJob")}
							title="Job Alerts"
							subtitle="Jobs that you received from job boards"
							badgeValue={scrapedJobCount}
							path="/scraped-jobs"
							isEmpty={scrapedJobCount === 0}
							emptyState={{
								icon: "bell-slash",
								title: "No job alerts",
								description: "Job alerts from your scrapers will appear here",
							}}
						>
							<div style={{ paddingTop: "9px", paddingBottom: "18px", display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
								<ScrapedJobsTable />
							</div>
						</DashboardCard>
					</Col>
				</Row>
			)}
		</>
	);
};

export default Dashboard;
