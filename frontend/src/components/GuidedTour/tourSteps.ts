export interface TourStep {
	id: string;
	targetSelector: string | null;
	title: string;
	content: string;
	route: string | null;
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

// ── Passive spotlight steps ──────────────────────────────────────────────────

export const TOUR_STEPS: TourStep[] = [
	{
		id: "intro",
		targetSelector: null,
		title: "Welcome to JAM!",
		content: "Let's take a quick tour of your Job Application Manager. It'll only take a minute.",
		route: null,
		placement: "center",
	},
	{
		id: "sidebar",
		targetSelector: '[data-tour="nav-jobs"]',
		title: "Sidebar Navigation",
		content:
			"Use the sidebar to move between sections. Jobs is your central hub — log applications, track every status, and link each job to People and Interviews.",
		route: "/jam/dashboard",
		placement: "right",
	},
	{
		id: "dashboard-stats",
		targetSelector: "#stat-card-total_jobs",
		title: "Your Overview at a Glance",
		content:
			"Stat cards show your pipeline at a glance — total applications, pending responses, upcoming deadlines, and more.",
		route: "/jam/dashboard",
		placement: "bottom",
	},
	{
		id: "dashboard-customise",
		targetSelector: '[data-tour="dashboard-customise"]',
		title: "Customise Your Dashboard",
		content:
			"Click here to enter edit mode. Add, remove, reorder, and resize widgets to build a dashboard that suits your workflow.",
		route: "/jam/dashboard",
		placement: "bottom",
	},
	{
		id: "command-palette",
		targetSelector: '[data-tour="take-a-tour-btn"]',
		title: "Navigate in Seconds",
		content:
			"Press Ctrl+K (or Cmd+K on Mac) to open the command palette — jump to any page or trigger any action without touching the mouse. You can also re-run this tour any time from here.",
		route: "/jam/dashboard",
		placement: "right",
	},

	// ── Interactive job-creation walkthrough ─────────────────────────────────

	{
		id: "open-job-modal",
		targetSelector: '[data-tour="add-job-btn"]',
		title: "Let's Add Your First Job",
		content: "Click this button to log your first job application.",
		route: "/jam/jobs",
		placement: "bottom",
		waitForSelector: '.modal.show input[name="title"]',
		hideNextButton: true,
	},
	{
		id: "job-title",
		targetSelector: '.modal.show input[name="title"]',
		title: "Enter a Job Title",
		content: "Type any job title to continue. We'll automatically fill in a sample URL for you.",
		route: null,
		placement: "bottom",
		waitForInput: '.modal.show input[name="title"]',
		autoFill: {
			watchSelector: '.modal.show input[name="title"]',
			fillSelector: '.modal.show input[name="url"]',
			fillValue: "https://example.com/jobs/software-engineer-tour",
		},
		hideNextButton: true,
	},
	{
		id: "add-company",
		targetSelector: '.modal.show [id="add-button"]',
		title: "Add a Company",
		content: "Click the + button next to the Company field to create your first company.",
		route: null,
		placement: "right",
		waitForSelector: '.modal.show input[name="name"]',
		hideNextButton: true,
	},
	{
		id: "company-name",
		targetSelector: '.modal.show input[name="name"]',
		title: "Name Your Company",
		content: "Type a company name and click Save to add it.",
		route: null,
		placement: "bottom",
		waitForSelectorGone: '.modal.show input[name="name"]',
		hideNextButton: true,
	},
	{
		id: "save-job",
		targetSelector: '.modal.show .modal-footer .btn-primary',
		title: "Save the Job",
		content: "Everything looks great! Click to save your job application.",
		route: null,
		placement: "top",
		waitForSelectorGone: '.modal.show input[name="title"]',
		hideNextButton: true,
	},
	{
		id: "done",
		targetSelector: null,
		title: "You're All Set!",
		content:
			"You've added your first job application — great work! The job and company you just created will be removed when you click Done, so your data stays clean.",
		route: null,
		placement: "center",
	},
];
