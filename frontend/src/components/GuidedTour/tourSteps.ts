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
	/** Render choice buttons that jump to a specific step by id */
	choices?: Array<{ label: string; icon: string; targetStepId: string }>;
	/** After this step auto-advances (or Next is clicked), jump to this step id instead of the next index */
	nextStepId?: string;
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
		route: "dashboard",
		placement: "center",
	},
	{
		id: "dashboard-overview",
		targetId: "dashboard-main",
		title: "Your Dashboard",
		route: "dashboard",
		content:
			"This is your personal dashboard - allowing you to keep an eye on your job application progress at a glance.",
		placement: "center",
	},
	{
		id: "dashboard-customise",
		targetId: "dashboard-edit-btn",
		title: "Customise Your Dashboard",
		route: "dashboard",
		content:
			"Click here to enter edit mode. Add, remove, reorder, and resize widgets to build a dashboard that suits YOU.",
		placement: "bottom",
	},
	{
		id: "sidebar",
		targetId: "nav-jobs",
		title: "Jobs",
		route: "jobs",
		content:
			"Use the sidebar to move between sections. Jobs is your central hub - log applications, track every updates and interviews.",
		placement: "right",
	},
	{
		id: "premium",
		title: "Go Further with Premium",
		route: "settings/premium",
		content:
			"Land your dream job faster with JAM Premium - automatically scrape jobs from LinkedIn, Indeed, and more " +
			"straight into JAM, then let AI rate each one against your profile so the best matches rise to the top.",
		targetId: "premium-tab",
		placement: "center",
	},
	{
		id: "command-palette",
		title: "Navigate in Seconds",
		content:
			"Press Ctrl+K (or Cmd+K on Mac) to open the command palette - jump to any page or trigger any action " +
			"without touching the mouse. Click 'Take a Tour' here any time to revisit these guides.",
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

const FOLLOW_UP_EMAIL_STEPS: TourStep[] = [
	{
		id: "follow-up-intro",
		targetId: null,
		title: "Follow-up Email Generator",
		content:
			"JAM can draft a personalised follow-up email for any job application in seconds. How would you like to open it?",
		route: "/jam/jobs",
		placement: "center",
		hideNextButton: true,
		choices: [
			{ label: "Right-click a job row", icon: "bi-table", targetStepId: "follow-up-open-via-table" },
			{
				label: "Right-click a contact badge",
				icon: "bi-person-badge-fill",
				targetStepId: "follow-up-open-via-badge-1",
			},
			{
				label: "Button in the Application tab",
				icon: "bi-send-fill",
				targetStepId: "follow-up-open-via-button-1",
			},
		],
	},
	// ── Method 1: right-click job row ────────────────────────────────────────
	{
		id: "follow-up-open-via-table",
		targetId: "[demo-job-row]",
		title: "Right-click the Job Row",
		content:
			"Right-click this job row and select Follow-up Email. The tour will continue automatically once the generator is open.",
		route: "/jam/jobs",
		placement: "top",
		waitForSelector: "#follow-up-modal",
		hideNextButton: true,
		nextStepId: "follow-up-contact",
	},
	// ── Method 2: right-click contact badge ──────────────────────────────────
	{
		id: "follow-up-open-via-badge-1",
		targetId: "[demo-job-row]",
		title: "Open the Job",
		content: "Click this job row to open the job details.",
		route: "/jam/jobs",
		placement: "top",
		waitForSelector: "#job-tab",
		hideNextButton: true,
		nextStepId: "follow-up-open-via-badge-2",
	},
	{
		id: "follow-up-open-via-badge-2",
		targetId: "modal-view-job-person-0",
		title: "Right-click the Contact Badge",
		content:
			"Right-click this contact badge and select Follow-up Email. The tour will continue automatically once the generator is open.",
		placement: "bottom",
		waitForSelector: "#follow-up-modal",
		hideNextButton: true,
		nextStepId: "follow-up-contact",
	},
	// ── Method 3: button in Application tab ──────────────────────────────────
	{
		id: "follow-up-open-via-button-1",
		targetId: "[demo-job-row]",
		title: "Open the Job",
		content: "Click this job row to open the job details.",
		route: "/jam/jobs",
		placement: "top",
		waitForSelector: "#application-tab",
		hideNextButton: true,
		nextStepId: "follow-up-open-via-button-2",
	},
	{
		id: "follow-up-open-via-button-2",
		targetId: "application-tab",
		title: "Switch to the Application Tab",
		content: "Click the Application tab to see your application details.",
		placement: "bottom",
		waitForSelector: "#job-modal-follow-up-button",
		hideNextButton: true,
		nextStepId: "follow-up-open-via-button-3",
	},
	{
		id: "follow-up-open-via-button-3",
		targetId: "job-modal-follow-up-button",
		title: "Click Follow-up Email",
		content:
			"Click this button to open the Follow-up Email Generator. The tour will continue automatically once the generator is open.",
		placement: "top",
		waitForSelector: "#follow-up-modal",
		hideNextButton: true,
		nextStepId: "follow-up-contact",
	},
	{
		id: "follow-up-contact",
		targetId: "contactId-form-group",
		title: "Select a Contact",
		content:
			"Choose who you want to email. Switching contacts updates the greeting in the email body and pre-fills their email address.",
		placement: "right",
	},
	{
		id: "follow-up-subject",
		targetId: "subject-form-group",
		title: "Email Subject",
		content: "The subject is pre-filled based on the job title. Edit it if you'd like a different subject line.",
		placement: "right",
	},
	{
		id: "follow-up-body",
		targetId: "body-form-group",
		title: "Email Body",
		content:
			"A professional follow-up message is generated automatically. Personalise it before sending — especially the opening line.",
		placement: "right",
	},
	{
		id: "follow-up-send",
		targetId: "email-service-dropdown",
		title: "Send Your Email",
		content:
			"Click Send Email to open your default email client. Use the dropdown arrow to send via Gmail or Outlook instead.",
		placement: "top",
		hideNextButton: true,
		waitForSelector: "#confirm-alert-modal-buttons",
	},
	{
		id: "follow-up-log-update",
		targetId: "confirm-alert-modal-dialog",
		title: "Log the Email",
		content:
			"After clicking Send, JAM asks if you want to record the email as a job application update. Click Yes to keep a full history of your follow-ups, or No to skip.",
		placement: "top",
		hideNextButton: true,
		waitForSelectorGone: "#confirm-alert-modal-dialog",
	},
	{
		id: "follow-up-done",
		targetId: null,
		title: "All Done!",
		content:
			"That's the Follow-up Email Generator! Use it to stay on top of your applications and keep your job history complete.",
		placement: "center",
	},
];

const IMPORT_SCRAPED_JOB_STEPS: TourStep[] = [
	{
		id: "scraped-intro",
		targetId: null,
		title: "Job Alert Scraping",
		content:
			"JAM automatically scans your email alert subscriptions from LinkedIn, Indeed, and similar platforms — " +
			"pulling matching jobs straight into JAM so you never miss an opportunity. " +
			"We've added a demo alert so you can try the full import flow.",
		route: "/scraped-jobs",
		placement: "center",
	},
	{
		id: "scraped-table",
		targetId: "scrapedJob-data-table",
		title: "Your Job Alerts",
		content:
			"Every job found in your alert emails appears here. " +
			"New alerts since your last login are highlighted. " +
			"Use the search bar and column headers to sort and filter.",
		route: "/scraped-jobs",
		placement: "center",
	},
	{
		id: "scraped-emails-tab",
		targetId: "job-emails-header",
		title: "Job Emails",
		content:
			"The Job Emails tab shows the raw alert emails that triggered each scraping run. " +
			"Open an email to see exactly which alerts came from it — useful for tracing the source of a job or diagnosing why an alert wasn't picked up.",
		route: "/scraped-jobs",
		placement: "bottom",
	},
	{
		id: "scraped-ai-score",
		targetId: "table-header-job_rating.overall_score",
		title: "AI Score",
		content:
			"JAM rates each alert against your profile — skills, experience, and preferences. " +
			"Higher scores mean a stronger match. Set up your profile in User Settings to tune the ratings.",
		route: "/scraped-jobs",
		placement: "bottom",
	},
	{
		id: "scraped-filters",
		targetId: "scraping-filters-button",
		title: "Scraping Filters",
		content:
			"Click here to configure what gets scraped — include or exclude keywords, locations, and platforms. " +
			"Only alerts matching your active filters will appear in the table.",
		route: "/scraped-jobs",
		placement: "bottom",
	},
	{
		id: "scraped-open-row",
		targetId: "[demo-scraped-job-row]",
		title: "Open the Demo Alert",
		content: "Click this demo job alert to open the import form.",
		route: "/scraped-jobs",
		placement: "top",
		waitForSelector: "#modal-import-scrapedJob",
		hideNextButton: true,
	},
	{
		id: "scraped-review-form",
		targetId: "modal-import-scrapedJob",
		title: "Review the Import Form",
		content:
			"The scraped data is pre-filled — title, company, salary, location, and more. " +
			"Edit any field before importing. When you're happy, click Import.",
		placement: "left",
	},
	{
		id: "scraped-company-location",
		targetId: "company_id-form-group",
		title: "Check Company & Location",
		content:
			"JAM automatically tries to match the scraped company and location to entries you've already created. " +
			"These fields are highlighted when a match is found — always verify they're correct before importing, " +
			"as a partial match could link the job to the wrong entry.",
		placement: "right",
	},
	{
		id: "scraped-import-btn",
		targetId: "modal-import-scrapedJob-import-button",
		title: "Import the Job",
		content:
			"Click Import to add this job to your applications. " +
			"The demo data will be cleaned up automatically when the tour ends.",
		placement: "top",
		waitForSelectorGone: "#modal-import-scrapedJob",
		hideNextButton: true,
	},
	{
		id: "scraped-done",
		targetId: null,
		title: "All Done!",
		content:
			"The job is now in your job list. JAM will keep pulling in new alerts automatically — " +
			"just visit Job Alerts whenever you want to review and import the latest matches.",
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
	{
		id: "follow-up-email",
		title: "Sending a Follow-up Email",
		description: "Learn how to generate and send a personalised follow-up email for a job application.",
		icon: "envelope",
		steps: FOLLOW_UP_EMAIL_STEPS,
	},
	{
		id: "import-scraped-job",
		title: "Importing Job Alerts",
		description:
			"See how JAM scrapes job alerts from your emails, rates them with AI, and lets you import them in one click.",
		icon: "envelope-arrow-down",
		steps: IMPORT_SCRAPED_JOB_STEPS,
	},
];

export function getTourById(id: string): TourDefinition | undefined {
	return TOURS.find((t: TourDefinition): boolean => t.id === id);
}
