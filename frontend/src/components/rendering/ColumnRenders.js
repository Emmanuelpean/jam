import { renderFunctions } from "./Renders";
import { localeDateOnly } from "../../utils/TimeUtils";
import { formatTimeAgo } from "../../utils/TimeUtils";

export const columns = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	name: (overrides = {}) => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	title: (overrides = {}) => ({
		key: "title",
		label: "Title",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	description: (overrides = {}) => ({
		key: "description",
		label: "Description",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.description,
		...overrides,
	}),

	url: (overrides = {}) => ({
		key: "url",
		label: "Website",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.url,
		...overrides,
	}),

	createdAt: (overrides = {}) => ({
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: true,
		searchFields: localeDateOnly,
		render: renderFunctions.createdDate,
		...overrides,
	}),

	note: (overrides = {}) => ({
		key: "note",
		label: "Notes",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.note,
		...overrides,
	}),

	date: (overrides = {}) => ({
		key: "date",
		label: "Date",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: localeDateOnly,
		render: renderFunctions.date,
		...overrides,
	}),

	type: (overrides = {}) => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	updateType: (overrides = {}) => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.updateType,
		...overrides,
	}),

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: (overrides = {}) => ({
		key: "location",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "location.name",
		searchFields: "location.name",
		render: renderFunctions.location,
		...overrides,
	}),

	city: (overrides = {}) => ({
		key: "city",
		label: "City",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	postcode: (overrides = {}) => ({
		key: "postcode",
		label: "Postcode",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	country: (overrides = {}) => ({
		key: "country",
		label: "Country",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	company: (overrides = {}) => ({
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "company.name",
		searchFields: "company.name",
		render: renderFunctions.company,
		...overrides,
	}),

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	persons: (overrides = {}) => ({
		key: "person",
		label: "Contacts",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "person.last_name",
		searchFields: "person.name",
		render: renderFunctions.contacts,
		...overrides,
	}),

	personName: (overrides = {}) => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "last_name",
		...overrides,
	}),

	email: (overrides = {}) => ({
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.email,
		...overrides,
	}),

	phone: (overrides = {}) => ({
		key: "phone",
		label: "Phone",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.phone,
		...overrides,
	}),

	role: (overrides = {}) => ({
		key: "role",
		label: "Role",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	linkedinUrl: (overrides = {}) => ({
		key: "linkedin_url",
		label: "LinkedIn",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.linkedinUrl,
		...overrides,
	}),

	interviewers: (overrides = {}) => ({
		key: "person",
		label: "Interviewers",
		sortable: false,
		searchable: true,
		type: "text",
		sortField: "person.last_name",
		searchFields: "person.name",
		render: (item) => renderFunctions.contacts(item, false, "interviewers"),
		...overrides,
	}),

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	salaryRange: (overrides = {}) => ({
		key: "salary_range",
		label: "Salary",
		sortable: true,
		searchable: false,
		type: "text",
		sortField: "salary_min",
		render: renderFunctions.salaryRange,
		...overrides,
	}),

	personalRating: (overrides = {}) => ({
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: renderFunctions.personalRating,
		...overrides,
	}),

	keywords: (overrides = {}) => ({
		key: "keywords",
		label: "Keywords",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.keywords,
		...overrides,
	}),

	jobapplication: (overrides = {}) => ({
		key: "jobapplication",
		label: "Application Status",
		sortable: true,
		searchable: false,
		sortField: "job_application.status",
		searchFields: "job_application.status",
		render: renderFunctions.jobApplication,
		...overrides,
	}),

	job: (overrides = {}) => ({
		key: "job",
		label: "Job",
		sortable: true,
		searchable: true,
		searchFields: "job.title",
		sortField: "job.title",
		render: renderFunctions.job,
		...overrides,
	}),

	status: (overrides = {}) => ({
		key: "status",
		label: "Status",
		sortable: true,
		searchable: true,
		render: renderFunctions.status,
		...overrides,
	}),

	interviewCount: (overrides = {}) => ({
		key: "interview_count",
		label: "Interviews",
		sortable: true,
		sortField: "interview_count",
		searchable: false,
		render: renderFunctions.interviewCount,
		...overrides,
	}),

	jobApplicationJob: (overrides = {}) => ({
		key: "job",
		accessKey: "job_application",
		label: "Job",
		sortable: true,
		searchable: true,
		searchFields: "job.name",
		sortField: "job.title",
		render: renderFunctions.jobName,
		...overrides,
	}),

	files: (overrides = {}) => ({
		key: "files",
		label: "Files",
		sortable: false,
		searchable: false,
		render: renderFunctions.files,
		...overrides,
	}),

	// ---------------------------------------------- CHASE-SPECIFIC COLUMNS ----------------------------------------------

	daysSinceLastUpdate: (overrides = {}) => ({
		key: "days_since_last_update",
		label: "Days Since Last Update",
		sortable: true,
		searchable: false,
		type: "number",
		render: (item) => {
			const lastUpdateDate = item.job_application?.last_update_date;
			const applicationDate = item.job_application?.date;

			// Use the most recent date between last update and application date
			const referenceDate = lastUpdateDate || applicationDate;

			if (!referenceDate) {
				return <span className="text-muted">No date available</span>;
			}

			const now = new Date();
			const refDate = new Date(referenceDate);
			const diffTime = Math.abs(now - refDate);
			const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

			// Color coding based on urgency
			let className = "text-success";
			if (diffDays > 45) {
				className = "text-danger fw-bold";
			} else if (diffDays > 30) {
				className = "text-warning";
			}

			return (
				<span className={className} title={`Last update: ${formatTimeAgo(referenceDate)}`}>
					{diffDays} days
				</span>
			);
		},
		...overrides,
	}),

	lastUpdateType: (overrides = {}) => ({
		key: "last_update_type",
		label: "Last Update",
		sortable: true,
		searchable: true,
		type: "text",
		render: (item) => {
			const lastUpdate = item.job_application?.last_update;

			if (!lastUpdate) {
				return <span className="text-muted">Application only</span>;
			}

			return (
				<div>
					<div className="fw-bold">{lastUpdate.type}</div>
					{lastUpdate.note && (
						<small className="text-muted d-block" style={{ maxWidth: "200px" }}>
							{lastUpdate.note.length > 50 ? `${lastUpdate.note.substring(0, 50)}...` : lastUpdate.note}
						</small>
					)}
				</div>
			);
		},
		...overrides,
	}),
};
