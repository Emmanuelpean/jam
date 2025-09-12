import React, { ReactNode } from "react";
import { renderFunctions, RenderParams, Field, renderViewElement } from "./ViewRenders";
import { TableColumn } from "./TableColumnRenders";

export interface ViewField extends Field {
	label: string;
	type?: string;
	columnClass?: string;
	isTitle?: boolean;
	columns?: TableColumn[];
	helpText?: string;
}

export const renderViewField = (field: ViewField, item: any, id: string): ReactNode => {
	const output = renderViewElement(field, item, id);

	if (field.isTitle) {
		return (
			<>
				<div className="text-center p-1">
					<h2 className="display-6 fw-bold mt-4 mb-4" style={{ color: "var(--primary-mid)" }}>
						{output}
					</h2>
				</div>
			</>
		);
	} else {
		return (
			<>
				<h6 className="mb-2 fw-bold">{field.label}</h6>
				<div className="mb-3">{output}</div>
			</>
		);
	}
};

interface ViewFieldOverride extends Partial<ViewField> {}

export const viewFields = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	name: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "name",
		label: "Name",
		...overrides,
	}),

	title: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "title",
		label: "Title",
		...overrides,
	}),

	description: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "description",
		label: "Description",
		render: (params: RenderParams) => renderFunctions.description({ ...params, view: true }),
		...overrides,
	}),

	note: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "note",
		label: "Notes",
		render: (params: RenderParams) => renderFunctions.note({ ...params, view: true }),
		...overrides,
	}),

	applicationNote: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "application_note",
		label: "Notes",
		render: (params: RenderParams) => renderFunctions.applicationNote({ ...params, view: true }),
		...overrides,
	}),

	type: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "type",
		label: "Type",
		...overrides,
	}),

	appTheme: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "theme",
		label: "Theme",
		render: renderFunctions.appTheme,
		...overrides,
	}),

	isAdmin: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "is_admin",
		label: "Admin",
		render: (params: RenderParams) => renderFunctions.isAdmin({ ...params, view: true }),
		...overrides,
	}),

	city: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "city",
		label: "City",
		...overrides,
	}),

	postcode: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "postcode",
		label: "Postcode",
		...overrides,
	}),

	country: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "country",
		label: "Country",
		...overrides,
	}),

	personName: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "name",
		label: "Full Name",
		...overrides,
	}),

	updateType: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "type",
		label: "Type",
		render: renderFunctions.updateType,
		...overrides,
	}),

	// --------------------------------------------------- LINK/EMAIL --------------------------------------------------

	url: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "url",
		label: "Website",
		render: (params: RenderParams) => renderFunctions.url({ ...params, view: true }),
		...overrides,
	}),

	applicationUrl: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "application_url",
		label: "Application URL",
		render: (params: RenderParams) => renderFunctions.applicationUrl({ ...params, view: true }),
		...overrides,
	}),

	email: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "email",
		label: "Email",
		render: (params: RenderParams) => renderFunctions.email({ ...params, view: true }),
		...overrides,
	}),

	linkedinUrl: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "linkedin_url",
		label: "LinkedIn Profile",
		render: (params: RenderParams) => renderFunctions.linkedinUrl({ ...params, view: true }),
		...overrides,
	}),

	role: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "role",
		label: "Role",
		...overrides,
	}),

	// ----------------------------------------------------- BADGE -----------------------------------------------------

	locationBadge: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "location",
		label: "Location",
		render: (params: RenderParams) => renderFunctions.locationBadge({ ...params, view: true }),
		...overrides,
	}),

	companyBadge: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "company",
		label: "Company",
		render: renderFunctions.companyBadge,
		...overrides,
	}),

	keywordBadges: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "keywords",
		label: "Tags",
		render: (params: RenderParams) => renderFunctions.keywordBadges({ ...params, view: true }),
		...overrides,
	}),

	personBadges: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "person",
		label: "Contacts",
		render: (params: RenderParams) => renderFunctions.contactBadges({ ...params, view: true }),
		...overrides,
	}),

	jobBadge: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "job",
		label: "Job",
		render: (params: RenderParams) => renderFunctions.jobNameBadge({ ...params }),
		...overrides,
	}),

	interviewerBadges: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "person",
		label: "Interviewers",
		render: (params: RenderParams) => renderFunctions.interviewerBadges({ ...params, view: true }),
		...overrides,
	}),

	appliedViaBadge: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "applied_via",
		label: "Applied Via",
		render: (params: RenderParams) => renderFunctions.appliedViaBadge({ ...params, view: true }),
		...overrides,
	}),

	sourceBadge: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "source",
		label: "Source Aggregator",
		render: renderFunctions.sourceBadge,
		...overrides,
	}),

	// ----------------------------------------------------- OTHER -----------------------------------------------------

	locationMap: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "location_map",
		label: "Location on Map",
		type: "custom",
		columnClass: "col-12",
		render: renderFunctions.locationMap,
		...overrides,
	}),

	phone: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "phone",
		label: "Phone",
		render: (params: RenderParams) => renderFunctions.phone({ ...params, view: true }),
		...overrides,
	}),

	salaryRange: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "salary_range",
		label: "Salary Range",
		render: (params: RenderParams) => renderFunctions.salaryRange({ ...params, view: true }),
		...overrides,
	}),

	personalRating: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "personal_rating",
		label: "Personal Rating",
		render: (params: RenderParams) => renderFunctions.personalRating({ ...params, view: true }),
		...overrides,
	}),

	applicationStatus: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "application_status",
		label: "Status",
		render: (params: RenderParams) => renderFunctions.applicationStatus({ ...params, view: true }),
		...overrides,
	}),

	// ----------------------------------------------------- TABLE -----------------------------------------------------

	interviewTable: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "interviews",
		label: "Interviews",
		render: renderFunctions.interviewTable,
		...overrides,
	}),

	updateTable: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "updates",
		label: "Updates",
		render: renderFunctions.jobApplicationUpdateTable,
		...overrides,
	}),

	accordionInterviewTable: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "interviews",
		label: "Interviews",
		render: renderFunctions.accordionInterviewTable,
		...overrides,
	}),

	accordionJobTable: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "job",
		label: "Jobs",
		render: renderFunctions.accordionJobTable,
		...overrides,
	}),

	accordionJobApplicationTable: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "job_application",
		label: "Job Applications",
		render: renderFunctions.accordionJobApplicationTable,
		...overrides,
	}),

	accordionPersonTable: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "persons",
		label: "Persons",
		render: renderFunctions.accordionPersonTable,
		...overrides,
	}),

	// ---------------------------------------------------- DATETIME ---------------------------------------------------

	applicationDate: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "application_date",
		label: "Application Date",
		render: (params: RenderParams) => renderFunctions.applicationDate({ ...params, view: true }),
		...overrides,
	}),

	date: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "date",
		label: "Date",
		render: (params: RenderParams) => renderFunctions.date({ ...params, view: true }),
		...overrides,
	}),

	datetime: (overrides: ViewFieldOverride = {}): ViewField => ({
		key: "date",
		label: "Date & Time",
		render: (params: RenderParams) => renderFunctions.datetime({ ...params, view: true }),
		...overrides,
	}),
};
