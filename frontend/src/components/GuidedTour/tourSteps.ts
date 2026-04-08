export interface TourStep {
	id: string;
	targetId?: string | null;
	title: string;
	content: string;
	route?: string | null;
	placement: "top" | "bottom" | "left" | "right" | "center";
	/** Auto-advance when this selector APPEARS in the DOM */
	waitForSelector?: string;
	/** Auto-advance when this selector DISAPPEARS from the DOM */
	waitForSelectorGone?: string;
	/** Auto-advance when this input has a non-empty value */
	waitForInput?: string;
	/** When watchSelector gets input, fill fillSelector with fillValue via React's native setter */
	autoFill?: {
		watchSelector: string;
		fillSelector: string;
		fillValue: string;
	};
	/** Hide the Next button — step advances automatically or by user action */
	hideNextButton?: boolean;
}

export interface TourDefinition {
	id: string;
	title: string;
	description: string;
	icon: string;
	steps: TourStep[];
}

const APP_OVERVIEW_STEPS: TourStep[] = [
	{
		id: "intro",
		title: "Welcome to JAM!",
		content: "Let's take a quick tour of your Job Application Manager. It'll only take a minute.",
		route: "jam/dashboard",
		placement: "center",
	},
	{
		id: "dashboard-overview",
		targetId: "dashboard-main",
		title: "Your Dashboard",
		content:
			"This is your personal dashboard - allowing you to keep an eye on your job application progress at a glance.",
		route: "/jam/dashboard",
		placement: "center",
	},
	{
		id: "dashboard-customise",
		targetId: "dashboard-edit-btn",
		title: "Customise Your Dashboard",
		content:
			"Click here to enter edit mode. Add, remove, reorder, and resize widgets to build a dashboard that suits YOU.",
		placement: "bottom",
	},
	{
		id: "sidebar",
		targetId: "nav-jobs",
		title: "Sidebar Navigation",
		content:
			"Use the sidebar to move between sections. Jobs is your central hub - log applications, track every updates and interviews.",
		placement: "right",
	},
	{
		id: "settings",
		targetId: "nav-user-settings",
		title: "User Settings",
		content: "",
		placement: "right",
	},
	{
		id: "command-palette",
		title: "Navigate in Seconds",
		content:
			"Press Ctrl+K (or Cmd+K on Mac) to open the command palette — jump to any page or trigger any action without touching the mouse. Click 'Take a Tour' here any time to revisit these guides.",
		placement: "center",
	},
];

const FIRST_JOB_STEPS: TourStep[] = [
	{
		id: "first-job-intro",
		targetId: null,
		title: "Let's Log Your First Job",
		content:
			"This tour walks you through adding a job application from start to finish. We'll clean up any test data when you're done.",
		route: "/jam/jobs",
		placement: "center",
	},
	{
		id: "open-job-modal",
		targetId: "add-job-button",
		title: "Add a Job Application",
		content: "Click this button to open the job form.",
		placement: "bottom",
		waitForSelector: '.modal.show input[name="title"]',
		hideNextButton: true,
	},
	{
		id: "job-title",
		targetId: "title",
		title: "Enter a Job Title",
		content: "Type any job title to continue.",
		placement: "bottom",
		waitForInput: '.modal.show input[name="title"]',
	},
	{
		id: "add-company",
		targetId: "add-button-company",
		title: "Add a Company",
		content: "Click the + button next to the Company field to create your first company.",
		placement: "right",
		waitForSelector: '.modal.show input[name="name"]',
		hideNextButton: true,
	},
	{
		id: "company-name",
		targetId: "name",
		title: "Name the Company",
		content: "Type a company name to continue.",
		placement: "bottom",
		waitForInput: '.modal.show input[name="name"]',
	},
	{
		id: "save-company",
		targetId: "modal-edit-company-confirm-button",
		title: "Save the Company",
		content: "Click to save. The company will be available to reuse on future job applications.",
		placement: "top",
		waitForSelectorGone: '.modal.show input[name="name"]',
		hideNextButton: true,
	},
	{
		id: "add-location",
		targetId: "add-button-location",
		title: "Location",
		content: "Click the + button to add a new location for this job.",
		placement: "right",
		waitForSelector: '.modal.show input[name="city"]',
		hideNextButton: true,
	},
	{
		id: "location-city",
		targetId: "city",
		title: "Enter a City",
		content: "Type a city name to continue.",
		placement: "bottom",
		waitForInput: '.modal.show input[name="city"]',
	},
	{
		id: "save-location",
		targetId: "modal-edit-location-confirm-button",
		title: "Save the Location",
		content: "Click to save. This location will be available to reuse on future job applications.",
		placement: "top",
		waitForSelectorGone: '.modal.show input[name="city"]',
		hideNextButton: true,
	},
	{
		id: "job-salary",
		targetId: "salary_min-form-group",
		title: "Salary Range",
		content:
			"Record the advertised salary range. The currency is taken from your preferred currency in User Settings.",
		placement: "right",
	},
	{
		id: "job-source",
		targetId: "source_type-form-group",
		title: "How Did You Find It?",
		content:
			"Log where you found the job — a job board, recruiter, LinkedIn, or elsewhere. Tracking your sources helps you see which channels land interviews.",
		placement: "right",
	},
	{
		id: "job-tags",
		targetId: "keywords-form-group",
		title: "Tags",
		content:
			"Add tags to categorise and filter your applications. Use them for tech stack, seniority level, or anything else that helps you stay organised.",
		placement: "right",
	},
	{
		id: "job-contacts",
		targetId: "contacts-form-group",
		title: "Contacts",
		content:
			"Link people to this job — hiring managers, recruiters, or anyone you've spoken to. Click the + icon to add a new contact on the fly.",
		placement: "right",
	},
	{
		id: "save-job",
		targetId: "modal-edit-job-confirm-button",
		title: "Save the Job",
		content: "Everything looks great! Click to save your job application.",
		placement: "top",
		waitForSelectorGone: '.modal.show input[name="title"]',
		hideNextButton: true,
	},
	{
		id: "done",
		targetId: null,
		title: "You're All Set!",
		content:
			"You've added your first job application — great work! The job and company you just created will be removed when you click Done, so your data stays clean.",
		route: null,
		placement: "center",
	},
];

// ── Tour registry ─────────────────────────────────────────────────────────────

export const TOURS: TourDefinition[] = [
	{
		id: "app-overview",
		title: "App Overview",
		description: "Get a quick tour of JAM's main features — the sidebar, dashboard, and command palette.",
		icon: "compass",
		steps: APP_OVERVIEW_STEPS,
	},
	{
		id: "first-job",
		title: "Adding Your First Job",
		description: "A step-by-step walkthrough for logging your first job application.",
		icon: "briefcase",
		steps: FIRST_JOB_STEPS,
	},
];

export function getTourById(id: string): TourDefinition | undefined {
	return TOURS.find((t: TourDefinition): boolean => t.id === id);
}
