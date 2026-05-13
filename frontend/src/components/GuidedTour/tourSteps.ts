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
	/** Disable Next while the matched input has content that is not a valid email (empty = allowed) */
	waitForValidEmailIfFilled?: string;
	/** Auto-focus this selector when the step activates (no effect on Next button) */
	autoFocusSelector?: string;
	/** Tour goes completely silent — no overlay, no popover. Use when the user needs free access to a modal. */
	freeInteraction?: boolean;
	/** When watchSelector gets input, fill fillSelector with fillValue via React's native setter */
	autoFill?: {
		watchSelector: string;
		fillSelector: string;
		fillValue: string;
	};
	/** Hide the Next button - step advances automatically or by user action */
	hideNextButton?: boolean;
	/** Show a Back button even when hideNextButton is true */
	showBack?: boolean;
	/** When Back is clicked, jump to this step id instead of step - 1 */
	backStepId?: string;
	/** Render choice buttons that jump to a specific step by id */
	choices?: Array<{ label: string; icon: string; targetStepId: string }>;
	/** After Next is clicked, jump to this step id instead of the next index */
	nextStepId?: string;
	/** When the waitForSelector/waitForSelectorGone condition fires (auto-advance), jump to this step id instead of nextStepId */
	autoAdvanceStepId?: string;
}

export interface TourDefinition {
	id: string;
	title: string;
	description: string;
	icon: string;
	steps: TourStep[];
	/** Not yet implemented - shown in the panel as disabled with a "Soon" badge */
	comingSoon?: boolean;
	/** Premium-only tour — hidden for non-premium users and shown with a badge */
	premium?: boolean;
}

export interface TourGroup {
	type: "group";
	id: string;
	title: string;
	icon: string;
	/** Optional badge label shown next to the group heading (e.g. "Premium") */
	badge?: string;
	tours: TourDefinition[];
}

export type TourStructureItem = TourDefinition | TourGroup;

export function isTourGroup(item: TourStructureItem): item is TourGroup {
	return (item as TourGroup).type === "group";
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
		content: "Click the + button to create a new company, or select one you've already added from the dropdown. Click Next to skip.",
		placement: "right",
		waitForSelector: "#modal-edit-company",
		autoAdvanceStepId: "company-filling",
		nextStepId: "job-location",
	},
	{
		id: "company-filling",
		targetId: "#modal-edit-company .modal-content",
		title: "Fill in the Company Details",
		content: "Enter a name and any other details, then click Confirm to save. The company will be available to reuse on future applications.",
		placement: "left",
		waitForSelectorGone: "#modal-edit-company",
		hideNextButton: true,
	},
	{
		id: "job-location",
		targetId: "location-form-group",
		title: "Location",
		content:
			"Type a location for this job - e.g. 'London, UK'. JAM will geocode it automatically so it appears on the map.",
		placement: "right",
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
			"Log where you found the job - a job board, recruiter, LinkedIn, or elsewhere. Tracking your sources helps you see which channels land interviews.",
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
			"Link people to this job - hiring managers, recruiters, or anyone you've spoken to. Click the + icon to add a new contact on the fly.",
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
		id: "show-job-in-table",
		targetId: "[demo-job-row]",
		title: "Job Saved!",
		content:
			"Your new job application now appears in the table. Use the columns to track status, deadline, and last activity at a glance.",
		placement: "top",
	},
	{
		id: "done",
		targetId: null,
		title: "You're All Set!",
		content:
			"You've added your first job application - great work! The job and company you just created will be removed when you click Done, so your data stays clean.",
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
			"A professional follow-up message is generated automatically. Personalise it before sending - especially the opening line.",
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
			"JAM automatically scans your email alert subscriptions from LinkedIn, Indeed, and similar platforms -" +
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
			"Open an email to see exactly which alerts came from it - useful for tracing the source of a job or diagnosing why an alert wasn't picked up.",
		route: "/scraped-jobs",
		placement: "bottom",
	},
	{
		id: "scraped-ai-score",
		targetId: "table-header-job_rating.overall_score",
		title: "AI Score",
		content:
			"JAM rates each alert against your profile - skills, experience, and preferences. " +
			"Higher scores mean a stronger match. Set up your profile in User Settings to tune the ratings.",
		route: "/scraped-jobs",
		placement: "bottom",
	},
	{
		id: "scraped-filters",
		targetId: "scraping-filters-button",
		title: "Scraping Filters",
		content:
			"Click here to configure what gets scraped - include or exclude keywords, locations, and platforms. " +
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
			"The scraped data is pre-filled - title, company, salary, location, and more. " +
			"Edit any field before importing. When you're happy, click Import.",
		placement: "left",
	},
	{
		id: "scraped-company-location",
		targetId: "company_id-form-group",
		title: "Check Company & Location",
		content:
			"JAM automatically tries to match the scraped company to one you've already created. " +
			"The field is highlighted when a match is found - always verify it's correct before importing.",
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
			"The job is now in your job list. JAM will keep pulling in new alerts automatically -" +
			"just visit Job Alerts whenever you want to review and import the latest matches.",
		placement: "center",
	},
];

const SCRAPING_FILTER_STEPS: TourStep[] = [
	{
		id: "sf-intro",
		targetId: null,
		title: "Scraping Filters",
		content:
			"Scraping filters let you control exactly which job alerts get pulled into JAM. " +
			"Exclusion filters silently drop alerts that match - keeping your table free of irrelevant results. " +
			"This tour walks you through creating and testing one.",
		route: "/scraped-jobs",
		placement: "center",
	},
	{
		id: "sf-open",
		targetId: "scraping-filters-button",
		title: "Open the Filter Panel",
		content: "Click the Scraping Filters button to open the filter manager.",
		route: "/scraped-jobs",
		placement: "bottom",
		waitForSelector: "#scraping-filters-modal",
		hideNextButton: true,
	},
	{
		id: "sf-overview",
		targetId: "scraping-filters-tables",
		title: "The Filter Panel",
		content:
			"This panel lists all your exclusion filters. Active filters run automatically during each scrape - " +
			"any alert that matches is silently dropped before it reaches your table.",
		placement: "left",
		hideNextButton: false,
	},
	{
		id: "sf-tabs",
		targetId: "active-tab",
		title: "Active & Inactive Filters",
		content:
			"Filters have two states: Active filters are applied on every scrape. " +
			"Switch to the Inactive tab to see filters you have paused - deactivate a filter to temporarily stop it without deleting it.",
		placement: "bottom",
	},
	{
		id: "sf-add",
		targetId: "add-scrapingFilter-button",
		title: "Create a Filter",
		content: "Click here to open the filter form and create your first filter.",
		placement: "bottom",
		waitForSelector: "#modal-edit-scrapingFilter",
		hideNextButton: true,
	},
	{
		id: "sf-type",
		targetId: "type-form-group",
		title: "Filter Type",
		content:
			"Choose what part of the job alert to match against - for example Title, Company, or Location. " +
			"Selecting Title will check the job title of every incoming alert.",
		placement: "right",
		waitForInput: "#type-form-group .jam-select__input",
	},
	{
		id: "sf-operator",
		targetId: "operator-form-group",
		title: "Operator",
		content:
			"Pick how the match is performed. Contains checks for a substring anywhere in the field; " +
			"Equals requires an exact match; Starts With and Ends With match the beginning or end.",
		placement: "right",
		waitForInput: "#operator-form-group .jam-select__input",
	},
	{
		id: "sf-value",
		targetId: "value-form-group",
		title: "Filter Value",
		content: "Type the word or phrase to match against. For example, enter 'Senior' to exclude senior-level roles.",
		placement: "right",
		waitForInput: "#modal-edit-scrapingFilter input[name='value']",
	},
	{
		id: "sf-test",
		targetId: "scraping-filter-test-btn",
		title: "Test the Filter",
		content:
			"Before saving, click Test to preview which existing job alerts this filter would match. " +
			"A table of matching alerts appears below - if it looks right, go ahead and save.",
		placement: "top",
	},
	{
		id: "sf-save",
		targetId: "modal-edit-scrapingFilter-confirm-button",
		title: "Save the Filter",
		content: "Happy with the filter? Click Save to activate it. It will be applied on the next scraping run.",
		placement: "top",
		waitForSelectorGone: "#modal-edit-scrapingFilter",
		hideNextButton: true,
	},
	{
		id: "sf-manage",
		targetId: "[demo-scraping-filter-row]",
		title: "Managing Filters",
		content:
			"Your new filter now appears in the table. Right-click any row to edit, deactivate, or delete a filter. " +
			"The filter created during this tour will be removed automatically when you click Done.",
		placement: "top",
	},
	{
		id: "sf-done",
		targetId: null,
		title: "All Done!",
		content:
			"You know how to create and manage scraping filters. " +
			"Use them to keep irrelevant alerts out of your table and surface only the roles that matter to you.",
		placement: "center",
	},
];

const LOG_APPLICATION_STEPS: TourStep[] = [
	{
		id: "log-application-intro",
		targetId: null,
		title: "Logging a Job Application",
		content:
			"Once you've applied for a job, JAM lets you record the details - when you applied, the status, and how you submitted. We've added a demo job so you can try it now.",
		route: "/jam/jobs",
		placement: "center",
	},
	{
		id: "log-application-open-job",
		targetId: "[demo-job-row]",
		title: "Open the Job",
		content: "Click this job row to open the details.",
		route: "/jam/jobs",
		placement: "top",
		waitForSelector: "#application-tab",
		hideNextButton: true,
	},
	{
		id: "log-application-tab",
		targetId: "application-tab",
		title: "Switch to the Job Application Tab",
		content: "Click here to see the application section for this job.",
		placement: "bottom",
		waitForSelector: "#add-interview-button",
		hideNextButton: true,
	},
	{
		id: "log-application-edit",
		targetId: "modal-view-job-edit-button",
		title: "Edit the Job",
		content: "Click Edit to fill in your application details.",
		placement: "top",
		waitForSelector: "#application_date-form-group",
		hideNextButton: true,
	},
	{
		id: "log-application-date",
		targetId: "application_date-form-group",
		title: "Application Date",
		content:
			"Record when you submitted the application. JAM uses this for your dashboard timeline and to calculate days since last activity.",
		placement: "right",
		waitForInput: '.modal.show input[name="application_date"]',
	},
	{
		id: "log-application-status",
		targetId: "application_status-form-group",
		title: "Application Status",
		content:
			"Set the current status - Applied, Under Review, Rejected, Offer Received, and more. This feeds your dashboard stats and highlights stalled applications.",
		placement: "right",
		waitForInput: "#application_status-form-group .jam-select__input",
	},
	{
		id: "log-application-via",
		targetId: "applied_via-form-group",
		title: "How Did You Apply?",
		content:
			"Log how you submitted - directly on the company site, via a job board, LinkedIn, or through a recruiter. Tracking this helps you see which channels get the best results.",
		placement: "right",
	},
	{
		id: "log-application-url",
		targetId: "application_url-form-group",
		title: "Application URL",
		content:
			"Paste the link to your application confirmation or the original job listing. Useful if you need to refer back to it later.",
		placement: "right",
	},
	{
		id: "log-application-note",
		targetId: "application_note-form-group",
		title: "Application Notes",
		content:
			"Add anything worth remembering - cover letter highlights, the recruiter's name, or a reminder to follow up.",
		placement: "right",
	},
	{
		id: "log-application-save",
		targetId: "modal-edit-job-confirm-button",
		title: "Save the Application",
		content:
			"Click Update to save your application details. The Job Application tab will show the status badge once saved.",
		placement: "top",
		waitForSelectorGone: '.modal.show input[name="application_date"]',
		hideNextButton: true,
	},
	{
		id: "log-application-done",
		targetId: null,
		title: "All Done!",
		content:
			"You've logged your application details. Keep updating the status as things progress - your dashboard will always reflect where you really stand. The demo job will be removed when you click Done.",
		placement: "center",
	},
];

const LOG_INTERVIEW_STEPS: TourStep[] = [
	{
		id: "interview-intro",
		targetId: null,
		title: "Logging an Interview",
		content:
			"Once you've heard back about an interview, JAM lets you record every detail - type, date, location, and who you spoke with. We've added a demo application so you can try it now.",
		route: "/jam/jobs",
		placement: "center",
	},
	{
		id: "interview-open-job",
		targetId: "[demo-job-row]",
		title: "Open the Application",
		content: "Click this job row to open the application details.",
		route: "/jam/jobs",
		placement: "top",
		waitForSelector: "#application-tab",
		hideNextButton: true,
	},
	{
		id: "interview-application-tab",
		targetId: "application-tab",
		title: "Switch to the Application Tab",
		content: "Click here to see your application history, including interviews and status updates.",
		placement: "bottom",
		waitForSelector: "#add-interview-button",
		hideNextButton: true,
	},
	{
		id: "interview-add",
		targetId: "add-interview-button",
		title: "Add an Interview",
		content: "Click this button to log a new interview.",
		placement: "bottom",
		waitForSelector: "#modal-edit-interview",
		hideNextButton: true,
	},
	{
		id: "interview-date",
		targetId: "date-form-group",
		title: "Date & Time",
		content: "Set when the interview took place (or is scheduled). JAM uses this to keep your timeline in order.",
		placement: "right",
		waitForInput: '.modal.show input[name="date"]',
	},
	{
		id: "interview-type",
		targetId: "type-form-group",
		title: "Interview Type",
		content:
			"Record the format - phone screen, video call, technical, or on-site. Tracking types helps you spot patterns across your applications.",
		placement: "right",
		waitForInput: "#type-form-group .jam-select__input",
	},
	{
		id: "interview-attendance",
		targetId: "attendance_type-form-group",
		title: "Attendance",
		content: "Log whether the interview is remote, on-site, or hybrid.",
		placement: "right",
	},
	{
		id: "interview-interviewers",
		targetId: "interviewers-form-group",
		title: "Interviewers",
		content:
			"Link the people who interviewed you. Contacts already in JAM appear here - or add someone new on the fly.",
		placement: "right",
	},
	{
		id: "interview-note",
		targetId: "note-form-group",
		title: "Notes",
		content: "Capture anything worth remembering - questions asked, impressions, or things to follow up on.",
		placement: "right",
	},
	{
		id: "interview-save",
		targetId: "modal-edit-interview-confirm-button",
		title: "Save the Interview",
		content:
			"Click Save to record the interview. It'll appear in the application timeline and feed into your dashboard stats.",
		placement: "top",
		waitForSelectorGone: "#modal-edit-interview",
		hideNextButton: true,
	},
	{
		id: "interview-show-in-table",
		targetId: "interview-data-table",
		title: "Interview Logged!",
		content: "Your interview now appears in the timeline. Right-click any row to edit or delete it.",
		placement: "top",
	},
	{
		id: "interview-done",
		targetId: null,
		title: "All Done!",
		content:
			"You've logged your first interview. The demo application will be cleaned up automatically when you click Done.",
		placement: "center",
	},
];

const LOG_UPDATE_STEPS: TourStep[] = [
	{
		id: "update-intro",
		targetId: null,
		title: "Logging an Application Update",
		content:
			"Heard back from a company? JAM lets you log any status change - rejection, offer, under review - so your application history stays complete. We've added a demo application to try it on.",
		route: "/jam/jobs",
		placement: "center",
	},
	{
		id: "update-open-job",
		targetId: "[demo-job-row]",
		title: "Open the Application",
		content: "Click this job row to open the application details.",
		route: "/jam/jobs",
		placement: "top",
		waitForSelector: "#application-tab",
		hideNextButton: true,
	},
	{
		id: "update-application-tab",
		targetId: "application-tab",
		title: "Switch to the Application Tab",
		content: "Click here to see your application history.",
		placement: "bottom",
		waitForSelector: "#add-jobApplicationUpdate-button",
		hideNextButton: true,
	},
	{
		id: "update-add",
		targetId: "add-jobApplicationUpdate-button",
		title: "Log an Update",
		content: "Click this button to record a new status update.",
		placement: "bottom",
		waitForSelector: "#modal-edit-jobApplicationUpdate",
		hideNextButton: true,
	},
	{
		id: "update-date",
		targetId: "date-form-group",
		title: "Date",
		content:
			"When did you receive this update? JAM uses this to order your timeline and calculate days since last activity.",
		placement: "right",
		waitForInput: '.modal.show input[name="date"]',
	},
	{
		id: "update-type",
		targetId: "type-form-group",
		title: "Update Type",
		content:
			"Choose the status - Rejected, Offer Received, Under Review, and more. This feeds your dashboard stats and helps you spot where applications are stalling.",
		placement: "right",
		waitForInput: "#type-form-group .jam-select__input",
	},
	{
		id: "update-note",
		targetId: "note-form-group",
		title: "Notes",
		content: "Add any details - feedback received, next steps, or a reminder for yourself.",
		placement: "right",
	},
	{
		id: "update-save",
		targetId: "modal-edit-jobApplicationUpdate-confirm-button",
		title: "Save the Update",
		content:
			"Click Save to record it. The update appears in the application timeline and updates the job's last activity date.",
		placement: "top",
		waitForSelectorGone: "#modal-edit-jobApplicationUpdate",
		hideNextButton: true,
	},
	{
		id: "update-show-in-table",
		targetId: "jobApplicationUpdate-data-table",
		title: "Update Logged!",
		content: "Your update now appears in the application timeline. Right-click any row to edit or delete it.",
		placement: "top",
	},
	{
		id: "update-done",
		targetId: null,
		title: "All Done!",
		content:
			"Keep logging updates as they come in and your dashboard will always reflect where you really stand. The demo application will be removed when you click Done.",
		placement: "center",
	},
];


const ADD_CONTACT_STEPS: TourStep[] = [
	{
		id: "contact-intro",
		targetId: null,
		title: "Adding a Contact",
		content:
			"Contacts in JAM are the people behind your job search - hiring managers, recruiters, and anyone you've spoken to. Linking them to jobs makes it easy to track relationships and generate follow-up emails. We'll clean up any test data when you're done.",
		route: "/persons",
		placement: "center",
	},
	{
		id: "contact-add-btn",
		targetId: "add-person-button",
		title: "Add a Contact",
		content: "Click this button to open the contact form.",
		route: "/persons",
		placement: "bottom",
		waitForSelector: "#modal-edit-person",
		hideNextButton: true,
	},
	{
		id: "contact-first-name",
		targetId: "first_name-form-group",
		title: "First Name",
		content: "Enter the contact's first name.",
		placement: "bottom",
		waitForInput: '.modal.show input[name="first_name"]',
	},
	{
		id: "contact-last-name",
		targetId: "last_name-form-group",
		title: "Last Name",
		content: "Enter the contact's last name.",
		placement: "bottom",
		waitForInput: '.modal.show input[name="last_name"]',
	},
	{
		id: "contact-role",
		targetId: "role-form-group",
		title: "Role",
		content: "Add their job title - Hiring Manager, Recruiter, Engineering Lead, or whatever fits.",
		placement: "right",
		autoFocusSelector: '.modal.show input[name="role"]',
	},
	{
		id: "contact-email",
		targetId: "email-form-group",
		title: "Email Address",
		content:
			"If you have their email, add it here. JAM uses it to pre-fill the recipient in the follow-up email generator.",
		placement: "right",
		waitForValidEmailIfFilled: '.modal.show input[name="email"]',
	},
	{
		id: "contact-company",
		targetId: "company_id-form-group",
		title: "Company",
		content:
			"Link the contact to a company you've already created. Click + to add a new company on the fly, or click Next to skip.",
		placement: "right",
		waitForSelector: "#modal-edit-company",
		autoAdvanceStepId: "contact-company-filling",
		nextStepId: "contact-save",
	},
	{
		id: "contact-company-filling",
		targetId: "#modal-edit-company .modal-content",
		title: "Fill in the Company Details",
		content: "Enter a name and any other details, then click Confirm to save.",
		placement: "left",
		waitForSelectorGone: "#modal-edit-company",
		hideNextButton: true,
		nextStepId: "contact-save",
	},
	{
		id: "contact-save",
		targetId: "modal-edit-person-confirm-button",
		title: "Save the Contact",
		content: "Click Confirm to save. The contact is now available to link to any job.",
		placement: "top",
		waitForSelectorGone: '.modal.show input[name="first_name"]',
		hideNextButton: true,
		showBack: true,
		backStepId: "contact-company",
	},
	{
		id: "contact-done",
		targetId: null,
		title: "All Done!",
		content:
			"Your contact is saved. Open any job, go to the Tags & Contacts section, and add them - they'll appear as a badge you can right-click for quick actions. The contact created during this tour will be removed when you click Done.",
		placement: "center",
	},
];

const SPECULATIVE_APPLICATIONS_STEPS: TourStep[] = [
	{
		id: "speculative-intro",
		targetId: "nav-speculative-applications",
		title: "Speculative Applications",
		content:
			"A speculative application is a proactive outreach to a company that hasn't posted a specific vacancy. JAM tracks these separately so you can follow up and stay organised. We'll clean up any test data when you're done.",
		route: "/speculative-applications",
		placement: "right",
	},
	{
		id: "speculative-add",
		targetId: "add-speculativeApplication-button",
		title: "Log an Application",
		content: "Click this button to log a new speculative outreach.",
		placement: "bottom",
		waitForSelector: "#modal-edit-speculativeApplication",
		hideNextButton: true,
	},
	{
		id: "speculative-company",
		targetId: "company_id-form-group",
		title: "Company",
		content: "Select the company you're reaching out to — this is the only required field. Click + to create a new company on the fly.",
		placement: "right",
		waitForInput: "#company_id-form-group .jam-select__input",
		waitForSelector: "#modal-edit-company",
		autoAdvanceStepId: "speculative-company-filling",
		nextStepId: "speculative-date",
	},
	{
		id: "speculative-company-filling",
		targetId: "#modal-edit-company .modal-content",
		title: "Fill in the Company Details",
		content: "Enter a name and any other details, then click Confirm to save.",
		placement: "left",
		waitForSelectorGone: "#modal-edit-company",
		hideNextButton: true,
		autoAdvanceStepId: "speculative-company",
	},
	{
		id: "speculative-date",
		targetId: "date-form-group",
		title: "Date",
		content:
			"Log when you sent the application or made contact. JAM uses this to order your list and flag overdue follow-ups.",
		placement: "right",
	},
	{
		id: "speculative-email",
		targetId: "contact_email-form-group",
		title: "Contact Email",
		content: "If you contacted a specific person, add their email here to track who you spoke to.",
		placement: "right",
	},
	{
		id: "speculative-contacts",
		targetId: "contacts-form-group",
		title: "Contacts",
		content: "Link a person to this application — select an existing contact or click + to add a new one on the fly. Click Next to skip.",
		placement: "right",
		waitForSelector: "#modal-edit-person",
		autoAdvanceStepId: "speculative-contact-filling",
		nextStepId: "speculative-note",
	},
	{
		id: "speculative-contact-filling",
		targetId: "#modal-edit-person .modal-content",
		title: "Fill in the Contact Details",
		content: "Enter a name and any other details, then click Confirm to save.",
		placement: "left",
		waitForSelectorGone: "#modal-edit-person",
		hideNextButton: true,
		autoAdvanceStepId: "speculative-contacts",
	},
	{
		id: "speculative-note",
		targetId: "note-form-group",
		title: "Notes",
		content: "Record what you sent, who you addressed it to, or any response you received.",
		placement: "right",
	},
	{
		id: "speculative-save",
		targetId: "modal-edit-speculativeApplication-confirm-button",
		title: "Save",
		content: "Click Confirm to log the speculative application.",
		placement: "top",
		waitForSelectorGone: "#modal-edit-speculativeApplication",
		hideNextButton: true,
	},
	{
		id: "speculative-done",
		targetId: null,
		title: "All Done!",
		content:
			"The application is logged. Right-click any row to edit or delete entries. The record created during this tour will be removed when you click Done.",
		placement: "center",
	},
];


// ── Tour registry ─────────────────────────────────────────────────────────────

export const TOUR_STRUCTURE: TourDefinition[] = [
	{
		id: "app-overview",
		title: "App Overview",
		description: "Get a quick tour of JAM's main features - the sidebar, dashboard, and command palette.",
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
		id: "log-application",
		title: "Logging a Job Application",
		description:
			"Walk through filling in your application details - when you applied, the status, and how you submitted.",
		icon: "send",
		steps: LOG_APPLICATION_STEPS,
	},
	{
		id: "log-interview",
		title: "Logging an Interview",
		description: "Walk through recording an interview - type, date, location, and who you spoke with.",
		icon: "camera-video",
		steps: LOG_INTERVIEW_STEPS,
	},
	{
		id: "log-update",
		title: "Logging an Application Update",
		description:
			"Learn how to log a status change - rejection, offer, under review - to keep your application history complete.",
		icon: "arrow-repeat",
		steps: LOG_UPDATE_STEPS,
	},
	{
		id: "follow-up-email",
		title: "Generating Follow-up Emails",
		description: "Learn how to generate and send a personalised follow-up email for a job application.",
		icon: "envelope",
		steps: FOLLOW_UP_EMAIL_STEPS,
	},
	{
		id: "add-contact",
		title: "Adding a Contact",
		description:
			"Walk through creating a contact - hiring manager, recruiter, or anyone you've spoken to - and linking them to a job.",
		icon: "person-plus",
		steps: ADD_CONTACT_STEPS,
	},
	{
		id: "speculative-applications",
		title: "Speculative Applications",
		description:
			"Learn how to log and track proactive outreach to companies that haven't posted a specific vacancy.",
		icon: "megaphone",
		steps: SPECULATIVE_APPLICATIONS_STEPS,
	},
	{
		id: "import-scraped-job",
		title: "Overview & Importing Job Alerts",
		description:
			"See how JAM scrapes job alerts from your emails, rates them with AI, and lets you import them in one click.",
		icon: "envelope-arrow-down",
		steps: IMPORT_SCRAPED_JOB_STEPS,
		premium: true,
	},
	{
		id: "scraping-filters",
		title: "Creating & Managing Scraping Filters",
		description: "Learn how to set up filters to control which job alerts get scraped into JAM.",
		icon: "funnel",
		steps: SCRAPING_FILTER_STEPS,
		premium: true,
	},
];

/** Flat list of every tour (including coming-soon). Used by getTourById. */
export const TOURS: TourDefinition[] = TOUR_STRUCTURE;

export function getTourById(id: string): TourDefinition | undefined {
	return TOURS.find((t: TourDefinition): boolean => t.id === id);
}
