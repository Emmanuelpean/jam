import V1_0_0 from "./V1_0_0";
import V1_1_0 from "./V1_1_0";
import V1_2_0 from "./V1_2_0";
import V1_3_0 from "./V1_3_0";
import followupGif from "../assets/demo_gifs/followup_email.gif";
import speculativeApplicationGif from "../assets/demo_gifs/speculative_application.gif";
import scrapingFilterGif from "../assets/demo_gifs/scraping_filter.gif";
import jobsGif from "../assets/demo_gifs/job_page.gif";
import scrapedJobsPng from "../assets/screenshots/scraped-jobs.png";
import dashboardPng from "../assets/screenshots/dashboard.png";
import { PREMIUM_PRICE } from "../pages/UserSettings/PremiumTab";
import interviewsPng from "../assets/screenshots/interviews.png";
import deadlinesPng from "../assets/screenshots/deadlines.png";
import { getEntityIcon } from "../components/rendering/view/Icons";

export type version = "1.0.0" | "1.1.0" | "1.2.0" | "1.3.0";
export const VERSIONS: version[] = ["1.0.0", "1.1.0", "1.2.0", "1.3.0"];
export const LAST_VERSION: version = VERSIONS[VERSIONS.length - 1]!;

export interface ReleaseSlide {
	icon?: string;
	title: string;
	description: string;
	image?: string;
	version?: string;
}

export const releaseNotes: Record<version, string> = {
	"1.0.0": V1_0_0,
	"1.1.0": V1_1_0,
	"1.2.0": V1_2_0,
	"1.3.0": V1_3_0,
};

export const WELCOME_SLIDES: ReleaseSlide[] = [
	{
		title: "Welcome to JAM!",
		description:
			"You have taken the first step toward landing your dream job. JAM is your all-in-one job application " +
			"manager - designed to keep your search organized so you can focus on interviews, not admin work. Let us show " +
			"you what is inside.",
		image: dashboardPng,
	},
	{
		icon: "briefcase",
		title: "Job Application Records",
		description:
			"Store every detail of your job applications in one place. Track roles, companies, contacts, dates, " +
			"and notes so nothing slips through the cracks.",
		image: jobsGif,
	},
	{
		icon: "calendar-check",
		title: "Interview Scheduling",
		description:
			"Stay on top of your interviews with clear scheduling and status tracking. Log dates, stages, " +
			"interviewers, and outcomes so you always know what's coming up next.",
		image: interviewsPng,
	},
	{
		icon: "clock",
		title: "Deadline & Follow-Up Reminder",
		description: "Get reminded of upcoming application deadlines and job requiring a follow-up",
		image: deadlinesPng,
	},
	{
		icon: "inboxes",
		title: "Premium - Job Alert Scraping and Rating",
		description:
			"Typical job seekers receive hundreds of job alerts every month from job aggregators like LinkedIn and Indeed. " +
			"For only " + PREMIUM_PRICE + "/month, JAM automatically scrapes these job details, rates them against your qualifications, " +
			"and highlights the best matches for you.",
		image: scrapedJobsPng,
	},
	{
		icon: "envelope-arrow-up",
		title: "Follow-Up Email Generator",
		description:
			"Automatically generate personalised follow-up emails in seconds. Right-click any job, pick a contact, " +
			"and get a ready-to-send message signed with your name.",
		image: followupGif,
	},
];

export const RELEASE_SLIDES: Record<version, ReleaseSlide[]> = {
	"1.0.0": [
		{
			icon: getEntityIcon("job"),
			title: "Job Application Tracking",
			description:
				"Create and manage detailed job application records. Track role titles, companies, " +
				"application dates, locations, salaries, and links — all from a centralised dashboard.",
		},
		{
			icon: "calendar-check",
			title: "Interview Scheduling",
			description:
				"Log interview dates, times, and types for each application. " +
				"Keep a clear timeline of your interview stages and never miss an upcoming meeting.",
		},
		{
			icon: getEntityIcon("company"),
			title: "Company & Contact Management",
			description:
				"Store company details and link contacts to your applications. " +
				"Track phone numbers, emails, LinkedIn profiles, and notes for every person you interact with.",
		},
		{
			icon: "bar-chart",
			title: "Application Status Monitoring",
			description:
				"Track each application through customisable statuses — from Applied to Offered. " +
				"Monitor deadlines, follow-ups, and see where every opportunity stands at a glance.",
		},
		{
			icon: "envelope-check",
			title: "Email Verification & Password Reset",
			description:
				"Secure your account with email verification on sign-up. " +
				"Forgot your password? Reset it easily via a verification code sent to your email.",
		},
	],
	"1.1.0": [
		{
			icon: "inboxes",
			title: "Job Scraping & Rating (Alpha)",
			description:
				"Introducing TOAST — automatically extract and organise job alert data from your emails. " +
				"Forward job alerts to a designated address and TOAST parses job titles, companies, locations, and salaries. " +
				"Each job is rated by an AI based on your qualifications.",
		},
		{
			icon: "star-half",
			title: "AI Job Rating",
			description:
				"Every scraped job is automatically rated by an LLM based on the qualifications " +
				"you set on your user page, helping you prioritise the best opportunities.",
		},
		{
			icon: "palette",
			title: "UI Improvements",
			description:
				"Improved raspberry theme contrast for better visibility. Select widget options are now sorted alphabetically " +
				"and auto-selected after adding. Company names are displayed in job and person selects for easier identification.",
		},
		{
			icon: "bug",
			title: "Bug Fixes",
			description:
				"The source aggregator is now consistently shown when editing a job. " +
				"Modal content refreshes correctly after edits, and the theme name updates immediately when changed in the sidebar.",
		},
	],
	"1.2.0": [
		{
			icon: getEntityIcon("scrapingFilter"),
			title: "Job Scraping Filters",
			description:
				"Create custom filtering rules to exclude unwanted jobs from your job scraping results. " +
				"Filter by company name, job title, or other parameters using flexible operators like Equals To or Contains. " +
				"Manage your filters directly from the Job Alerts table on your dashboard or on the Job Alerts page.",
			image: scrapingFilterGif,
		},
		{
			icon: getEntityIcon("speculativeApplication"),
			title: "Speculative Applications",
			description:
				"A new dedicated page for tracking speculative and spontaneous job applications. " +
				"Record the company name, submission date, contact email, relevant contacts, and any additional notes.",
			image: speculativeApplicationGif,
		},
		{
			title: "Follow-Up Email Generator",
			description:
				"Generate personalized follow-up emails for any job application. Right-click a job to create a " +
				"ready-to-send email to that job’s contacts—auto-filled with the role title and signed with your name",
			image: followupGif,
		},
		{
			icon: "gem",
			title: "JAM Premium (TOAST)",
			description:
				"TOAST (Turn Opportunity Alerts into Structured Tracking) is now available to everyone. " +
				"Subscribe in your user settings under Premium. New users can try TOAST free for 14 days.",
			image: scrapedJobsPng,
		},
		{
			icon: "moon-stars",
			title: "Dark Mode & UI Refresh",
			description:
				"Dark mode has been added. The user settings page has been reworked, " +
				"and you can now update your first and last name, mark contacts as recruiters, " +
				"edit badge data via right-click, and delete your account.",
			image: dashboardPng,
		},
		{
			icon: "wrench",
			title: "Quality of Life Improvements",
			description:
				"Data export now includes speculative applications and scraped jobs. " +
				"Job sources can be specified as Recruiter, Recruitment Company, Aggregator, or Other. " +
				"Improved error messages with one-click support email. " +
				"Rejected, Offered, and Withdrawn jobs are hidden from the Needs Chase table.",
		},
	],
	"1.3.0": [
		{
			icon: "grid-1x2",
			title: "Customisable Dashboard",
			description:
				"Your dashboard is now fully customisable. Add, remove, resize, and rearrange widgets in edit mode. " +
				"Choose from Metric, Table, Timeline, Graph, and Map widget types, or build a custom graph from your own data.",
			image: dashboardPng,
		},
		{
			icon: "table",
			title: "Customisable Table Columns",
			description:
				"All data tables now support column customisation. Show or hide columns to focus on what matters, " +
				"with preferences saved per table.",
		},
		{
			icon: "star-fill",
			title: "Favourite Filters for Job Alerts",
			description:
				"Save your favourite filter configurations on the Job Alerts page and apply them with a single click. " +
				"A dedicated Favourite Job Alerts dashboard widget highlights matching jobs at a glance.",
		},
	],
};

function compareVersions(a: string, b: string): number {
	const pa: number[] = a.split(".").map(Number);
	const pb: number[] = b.split(".").map(Number);
	for (let i: number = 0; i < Math.max(pa.length, pb.length); i++) {
		const na: number = pa[i] ?? 0;
		const nb: number = pb[i] ?? 0;
		if (na !== nb) return na - nb;
	}
	return 0;
}

export function getReleaseSlidesForLastVersion(): ReleaseSlide[] {
	return RELEASE_SLIDES[LAST_VERSION] ?? [];
}

export function getNewerReleaseSlides(userVersion: string): ReleaseSlide[] {
	const newer: version[] = VERSIONS.filter((v: version): boolean => compareVersions(v, userVersion) > 0);
	newer.sort(compareVersions);
	const multipleVersions: boolean = newer.length > 1;
	return newer.flatMap((v: version): ReleaseSlide[] =>
		(RELEASE_SLIDES[v] ?? []).map(
			(slide: ReleaseSlide): ReleaseSlide => (multipleVersions ? { ...slide, version: v } : slide)
		)
	);
}
