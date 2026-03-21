import { useDataContext } from "../../contexts/DataContext";
import { useAuth } from "../../contexts/AuthContext";
import { sortByKey } from "../../utils/Utils";
import { EnrichedInterviewData, EnrichedJobData } from "../../services/schemas/DataTables";
import { RecentActivity } from "./ActivityFeed";

export interface DashboardData {
	totalJobs: number;
	jobApplications: EnrichedJobData[];
	jobApplicationPending: EnrichedJobData[];
	needsChase: EnrichedJobData[];
	upcomingDeadlines: EnrichedJobData[];
	upcomingInterviews: EnrichedInterviewData[];
	recentActivity: RecentActivity[];
}

const EMPTY_DATA: DashboardData = {
	totalJobs: 0,
	jobApplications: [],
	jobApplicationPending: [],
	needsChase: [],
	upcomingDeadlines: [],
	upcomingInterviews: [],
	recentActivity: [],
};

export function useDashboardData(): DashboardData {
	const { jobs, interviews, jobApplicationUpdates } = useDataContext();
	const { currentUser } = useAuth();

	if (!currentUser) return EMPTY_DATA;

	const now = new Date();

	const jobApplications: EnrichedJobData[] = jobs.filter(
		(job) => job.application_date || job.application_status
	);

	const jobApplicationPending: EnrichedJobData[] = jobApplications.filter(
		(job) => job.application_status && !["rejected", "withdrawn"].includes(job.application_status)
	);

	const needsChase: EnrichedJobData[] = jobApplicationPending.filter(
		(job) =>
			job.days_since_last_update &&
			job.days_since_last_update > currentUser.preferences.chase_threshold &&
			(!job.followup_snooze_datetime || job.followup_snooze_datetime <= now) &&
			job.application_status &&
			!["rejected", "offer", "withdrawn"].includes(job.application_status)
	);

	const thresholdDate = new Date(now.getTime() + currentUser.preferences.deadline_threshold * 24 * 60 * 60 * 1000);
	const upcomingDeadlines: EnrichedJobData[] = jobs.filter(
		(job) =>
			!job.application_date &&
			!job.application_status &&
			job.deadline &&
			new Date(job.deadline) > now &&
			new Date(job.deadline) <= thresholdDate
	);

	const upcomingInterviews: EnrichedInterviewData[] = sortByKey(
		interviews.filter((interview) => new Date(interview.date!) >= now),
		"date"
	);

	const allUpdates: RecentActivity[] = [];

	jobApplications.forEach((job) => {
		if (job.application_date) {
			allUpdates.push({ data: job, date: job.application_date, type: "Application", job_id: job.id });
		}
	});

	interviews.forEach((interview) => {
		if (new Date(interview.date) < now) {
			allUpdates.push({ data: interview, date: interview.date, type: "Interview", job_id: interview.job_id });
		}
	});

	jobApplicationUpdates.forEach((update) => {
		if (new Date(update.date) < now) {
			allUpdates.push({ data: update, date: update.date, type: "Job Application Update", job_id: update.job_id });
		}
	});

	allUpdates.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

	return {
		totalJobs: jobs.length,
		jobApplications,
		jobApplicationPending,
		needsChase,
		upcomingDeadlines,
		upcomingInterviews,
		recentActivity: allUpdates.slice(0, currentUser.preferences.update_limit),
	};
}