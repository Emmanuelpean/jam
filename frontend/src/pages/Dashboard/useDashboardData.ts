import { useDataContext } from "../../contexts/DataContext";
import { useAuth } from "../../contexts/AuthContext";
import { sortByKey } from "../../utils/Utils";
import { EnrichedInterviewData, EnrichedJobApplicationUpdateData, EnrichedJobData } from "../../services/schemas/DataTables";
import { RecentActivity } from "./ActivityFeed";

export interface DashboardData {
	totalJobs: number;
	jobApplications: EnrichedJobData[];
	jobApplicationPending: EnrichedJobData[];
	activeApplications: EnrichedJobData[];
	needsChase: EnrichedJobData[];
	upcomingDeadlines: EnrichedJobData[];
	upcomingInterviews: EnrichedInterviewData[];
	pastInterviews: EnrichedInterviewData[];
	statusUpdates: EnrichedJobApplicationUpdateData[];
	upcomingDeadlinesTimeline: EnrichedJobData[];
	recentActivity: RecentActivity[];
	interviewRate: number;
	avgResponseTime: number;
}

const EMPTY_DATA: DashboardData = {
	totalJobs: 0,
	jobApplications: [],
	jobApplicationPending: [],
	activeApplications: [],
	needsChase: [],
	upcomingDeadlines: [],
	upcomingInterviews: [],
	pastInterviews: [],
	statusUpdates: [],
	upcomingDeadlinesTimeline: [],
	recentActivity: [],
	interviewRate: 0,
	avgResponseTime: 0,
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

	const activeApplications: EnrichedJobData[] = jobApplications.filter(
		(job) => job.application_status && !["rejected", "withdrawn"].includes(job.application_status)
	);

	const applicationsWithInterviews = new Set(interviews.map((i) => i.job_id));
	const interviewRate =
		jobApplications.length > 0
			? Math.round((applicationsWithInterviews.size / jobApplications.length) * 100)
			: 0;

	const appsWithResponse = jobApplications.filter((job) => job.application_date && job.last_update_date);
	const avgResponseTime =
		appsWithResponse.length > 0
			? Math.round(
					appsWithResponse.reduce((sum, job) => {
						const appDate = new Date(job.application_date as string).getTime();
						const updateDate = new Date(job.last_update_date as string).getTime();
						return sum + (updateDate - appDate) / (1000 * 60 * 60 * 24);
					}, 0) / appsWithResponse.length
			  )
			: 0;

	const pastInterviews: EnrichedInterviewData[] = sortByKey(
		interviews.filter((interview) => new Date(interview.date) < now),
		"date",
		false
	);

	const statusUpdates: EnrichedJobApplicationUpdateData[] = [...jobApplicationUpdates]
		.filter((u) => new Date(u.date) <= now)
		.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
		.slice(0, currentUser.preferences.update_limit);

	const upcomingDeadlinesTimeline: EnrichedJobData[] = sortByKey(upcomingDeadlines, "deadline");

	return {
		totalJobs: jobs.length,
		jobApplications,
		jobApplicationPending,
		activeApplications,
		needsChase,
		upcomingDeadlines,
		upcomingInterviews,
		pastInterviews,
		statusUpdates,
		upcomingDeadlinesTimeline,
		recentActivity: allUpdates.slice(0, currentUser.preferences.update_limit),
		interviewRate,
		avgResponseTime,
	};
}