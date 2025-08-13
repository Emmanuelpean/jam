import { renderFunctions } from "./Renders";
import LocationMap from "../maps/LocationMap";

export const viewFields = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	name: (overrides = {}) => ({
		key: "name",
		label: "Name",
		...overrides,
	}),

	title: (overrides = {}) => ({
		key: "title",
		label: "Title",
		...overrides,
	}),

	description: (overrides = {}) => ({
		key: "description",
		label: "Description",
		render: (x) => renderFunctions.description(x, true),
		...overrides,
	}),

	url: (overrides = {}) => ({
		key: "url",
		label: "Website",
		render: (x) => renderFunctions.url(x, true),
		...overrides,
	}),

	createdAt: (overrides = {}) => ({
		key: "created_at",
		label: "Date Added",
		render: (x) => renderFunctions.createdDate(x, true),
		...overrides,
	}),

	modifiedAt: (overrides = {}) => ({
		key: "modified_at",
		label: "Modified On",
		render: (x) => renderFunctions.modifiedDate(x, true),
		...overrides,
	}),

	note: (overrides = {}) => ({
		key: "note",
		label: "Notes",
		render: (x) => renderFunctions.note(x, true),
		...overrides,
	}),

	date: (overrides = {}) => ({
		key: "date",
		label: "Date",
		render: (x) => renderFunctions.date(x, true),
		...overrides,
	}),

	datetime: (overrides = {}) => ({
		key: "date",
		label: "Date & Time",
		render: (x) => renderFunctions.datetime(x, true),
		...overrides,
	}),

	type: (overrides = {}) => ({
		key: "type",
		label: "Type",
		...overrides,
	}),

	updateType: (overrides = {}) => ({
		key: "type",
		label: "Type",
		render: (x) => renderFunctions.updateType(x, true),
		...overrides,
	}),

	appTheme: (overrides = {}) => ({
		key: "theme",
		label: "Theme",
		...overrides,
	}),

	isAdmin: (overrides = {}) => ({
		key: "is_admin",
		label: "Admin",
		render: (x) => renderFunctions.isAdmin(x, true),
		...overrides,
	}),

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: (overrides = {}) => ({
		key: "location",
		label: "Location",
		render: (x) => renderFunctions.location(x, true),
		...overrides,
	}),

	city: (overrides = {}) => ({
		key: "city",
		label: "City",
		...overrides,
	}),

	postcode: (overrides = {}) => ({
		key: "postcode",
		label: "Postcode",
		...overrides,
	}),

	country: (overrides = {}) => ({
		key: "country",
		label: "Country",
		...overrides,
	}),

	locationMap: (overrides = {}) => ({
		key: "location_map",
		label: "📍 Location on Map",
		type: "custom",
		columnClass: "col-12",
		render: (data) => {
			if (data.remote) {
				return (
					<div className="p-3 bg-light rounded">
						<div className="text-center">
							<div className="mb-2" style={{ fontSize: "4rem" }}>
								<i className="bi bi-house-heart-fill"></i>
							</div>
							<h6 className="text-muted">Remote Location</h6>
							<p className="text-muted mb-0 small">
								This location allows remote work and does not have a physical address.
							</p>
						</div>
					</div>
				);
			} else {
				return <LocationMap locations={data ? [data] : []} height={overrides.height || "300px"} />;
			}
		},
		...overrides,
	}),

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	company: (overrides = {}) => ({
		key: "company",
		label: "Company",
		render: (x) => renderFunctions.company(x, true),
		...overrides,
	}),

	// ---------------------------------------------------- KEYWORDS ---------------------------------------------------

	keywords: (overrides = {}) => ({
		key: "keywords",
		label: "Tags",
		render: (x) => renderFunctions.keywords(x, true),
		...overrides,
	}),

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	persons: (overrides = {}) => ({
		key: "person",
		label: "Contacts",
		render: (x) => renderFunctions.contacts(x, true),
		...overrides,
	}),

	personName: (overrides = {}) => ({
		key: "name",
		label: "Full Name",
		...overrides,
	}),

	email: (overrides = {}) => ({
		key: "email",
		label: "Email",
		render: (x) => renderFunctions.email(x, true),
		...overrides,
	}),

	phone: (overrides = {}) => ({
		key: "phone",
		label: "Phone",
		render: (x) => renderFunctions.phone(x, true),
		...overrides,
	}),

	linkedinUrl: (overrides = {}) => ({
		key: "linkedin_url",
		label: "LinkedIn Profile",
		render: (x) => renderFunctions.linkedinUrl(x, true),
		...overrides,
	}),

	role: (overrides = {}) => ({
		key: "role",
		label: "Role",
		...overrides,
	}),

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	salaryRange: (overrides = {}) => ({
		key: "salary_range",
		label: "Salary Range",
		render: (x) => renderFunctions.salaryRange(x, true),
		...overrides,
	}),

	personalRating: (overrides = {}) => ({
		key: "personal_rating",
		label: "Personal Rating",
		render: (x) => renderFunctions.personalRating(x, true),
		...overrides,
	}),

	jobApplication: (overrides = {}) => ({
		key: "job_application",
		label: "Application Status",
		render: (x) => renderFunctions.jobApplication(x, true),
		...overrides,
	}),

	status: (overrides = {}) => ({
		key: "status",
		label: "Status",
		render: (x) => renderFunctions.status(x, true),
		...overrides,
	}),

	interviewers: (overrides = {}) => ({
		key: "person",
		label: "Interviewers",
		render: (x) => renderFunctions.contacts(x, true, "interviewers"),
		...overrides,
	}),

	job: (overrides = {}) => ({
		key: "job",
		label: "Job",
		render: (x) => renderFunctions.job(x, true),
		...overrides,
	}),

	appliedVia: (overrides = {}) => ({
		key: "applied_via",
		label: "Applied Via",
		render: (x) => renderFunctions.appliedVia(x, true),
		...overrides,
	}),

	files: (overrides = {}) => ({
		key: "files",
		label: "Files",
		render: (x) => renderFunctions.files(x, true),
		...overrides,
	}),

	interviews: (overrides = {}) => ({
		key: "interviews",
		label: "Interviews",
		render: renderFunctions.interviewTable,
		...overrides,
	}),

	updates: (overrides = {}) => ({
		key: "updates",
		label: "Updates",
		render: renderFunctions.jobApplicationUpdateTable,
		...overrides,
	}),
};
