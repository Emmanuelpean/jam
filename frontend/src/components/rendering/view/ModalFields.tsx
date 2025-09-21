import React, { ReactNode } from "react";
import { renderFunctions, RenderParams, ViewField, renderViewField } from "./ViewRenders";

export interface ModalViewField extends ViewField {
	label?: string;
	type?: string;
	isTitle?: boolean;
	displayCondition?: (item: any) => boolean;
}

interface ModalViewFieldOverride extends Partial<ModalViewField> {}

export const renderModalViewField = (field: ModalViewField, item: any, id: string, onChange?: any): ReactNode => {
	const output = renderViewField(field, item, id, onChange);

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
	} else if (field.label) {
		return (
			<>
				<h6 className="mb-2 fw-bold">{field.label}</h6>
				<div className="mb-3">{output}</div>
			</>
		);
	} else {
		return output;
	}
};

export const modalViewFields = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	name: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "name",
		label: "Name",
		...overrides,
	}),

	title: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "title",
		label: "Title",
		...overrides,
	}),

	value: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "value",
		label: "Value",
		render: (params: RenderParams) => renderFunctions.value({ ...params, view: true }),
		...overrides,
	}),

	description: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "description",
		label: "Description",
		render: (params: RenderParams) => renderFunctions.description({ ...params, view: true }),
		...overrides,
	}),

	note: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "note",
		label: "Notes",
		render: (params: RenderParams) => renderFunctions.note({ ...params, view: true }),
		...overrides,
	}),

	applicationNote: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_note",
		label: "Notes",
		render: (params: RenderParams) => renderFunctions.applicationNote({ ...params, view: true }),
		...overrides,
	}),

	type: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "type",
		label: "Type",
		...overrides,
	}),

	appTheme: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "theme",
		label: "Theme",
		render: renderFunctions.appTheme,
		...overrides,
	}),

	isAdmin: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "is_admin",
		label: "Admin",
		render: (params: RenderParams) => renderFunctions.isAdmin({ ...params, view: true }),
		...overrides,
	}),

	city: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "city",
		label: "City",
		...overrides,
	}),

	postcode: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "postcode",
		label: "Postcode",
		...overrides,
	}),

	country: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "country",
		label: "Country",
		...overrides,
	}),

	personName: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "name",
		label: "Full Name",
		...overrides,
	}),

	updateType: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "type",
		label: "Type",
		render: renderFunctions.updateType,
		...overrides,
	}),

	// --------------------------------------------------- LINK/EMAIL --------------------------------------------------

	url: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "url",
		label: "Website",
		render: (params: RenderParams) => renderFunctions.url({ ...params, view: true }),
		...overrides,
	}),

	applicationUrl: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_url",
		label: "Application URL",
		render: (params: RenderParams) => renderFunctions.applicationUrl({ ...params, view: true }),
		...overrides,
	}),

	email: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "email",
		label: "Email",
		render: (params: RenderParams) => renderFunctions.email({ ...params, view: true }),
		...overrides,
	}),

	linkedinUrl: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "linkedin_url",
		label: "LinkedIn Profile",
		render: (params: RenderParams) => renderFunctions.linkedinUrl({ ...params, view: true }),
		...overrides,
	}),

	role: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "role",
		label: "Role",
		...overrides,
	}),

	// ----------------------------------------------------- BADGE -----------------------------------------------------

	locationBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "location",
		label: "Location",
		render: (params: RenderParams) => renderFunctions.locationBadge({ ...params, view: true }),
		...overrides,
	}),

	companyBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "company",
		label: "Company",
		render: renderFunctions.companyBadge,
		...overrides,
	}),

	keywordBadges: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "keywords",
		label: "Tags",
		render: (params: RenderParams) => renderFunctions.keywordBadges({ ...params, view: true }),
		...overrides,
	}),

	personBadges: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "person",
		label: "Contacts",
		render: (params: RenderParams) => renderFunctions.contactBadges({ ...params, view: true }),
		...overrides,
	}),

	jobBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job",
		label: "Job",
		render: (params: RenderParams) => renderFunctions.jobNameBadge({ ...params }),
		...overrides,
	}),

	interviewerBadges: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "person",
		label: "Interviewers",
		render: (params: RenderParams) => renderFunctions.interviewerBadges({ ...params, view: true }),
		...overrides,
	}),

	appliedViaBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "applied_via",
		label: "Applied Via",
		render: (params: RenderParams) => renderFunctions.appliedViaBadge({ ...params, view: true }),
		...overrides,
	}),

	sourceBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "source",
		label: "Source Aggregator",
		render: renderFunctions.sourceBadge,
		...overrides,
	}),

	// ----------------------------------------------------- OTHER -----------------------------------------------------

	locationMap: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "location_map",
		label: "Location on Map",
		type: "custom",
		render: renderFunctions.locationMap,
		...overrides,
	}),

	phone: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "phone",
		label: "Phone",
		render: (params: RenderParams) => renderFunctions.phone({ ...params, view: true }),
		...overrides,
	}),

	salaryRange: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "salary_range",
		label: "Salary Range",
		render: (params: RenderParams) => renderFunctions.salaryRange({ ...params, view: true }),
		...overrides,
	}),

	personalRating: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "personal_rating",
		label: "Personal Rating",
		render: (params: RenderParams) => renderFunctions.personalRating({ ...params, view: true }),
		...overrides,
	}),

	applicationStatus: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_status",
		label: "Status",
		render: (params: RenderParams) => renderFunctions.applicationStatus({ ...params, view: true }),
		...overrides,
	}),

	// ----------------------------------------------------- TABLE -----------------------------------------------------

	interviewTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "interviews",
		render: renderFunctions.interviewTable,
		...overrides,
	}),

	updateTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "updates",
		render: renderFunctions.jobApplicationUpdateTable,
		...overrides,
	}),

	accordionInterviewTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "interviews",
		render: renderFunctions.accordionInterviewTable,
		...overrides,
	}),

	accordionJobTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job",
		render: renderFunctions.accordionJobTable,
		...overrides,
	}),

	accordionJobApplicationTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job_application",
		render: renderFunctions.accordionJobApplicationTable,
		...overrides,
	}),

	accordionPersonTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "persons",
		render: renderFunctions.accordionPersonTable,
		...overrides,
	}),

	// ---------------------------------------------------- DATETIME ---------------------------------------------------

	applicationDate: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_date",
		label: "Application Date",
		render: (params: RenderParams) => renderFunctions.applicationDate({ ...params, view: true }),
		...overrides,
	}),

	date: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "date",
		label: "Date",
		render: (params: RenderParams) => renderFunctions.date({ ...params, view: true }),
		...overrides,
	}),

	datetime: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "date",
		label: "Date & Time",
		render: (params: RenderParams) => renderFunctions.datetime({ ...params, view: true }),
		...overrides,
	}),

	deadline: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "deadline",
		label: "Application Deadline",
		render: (params: RenderParams) => renderFunctions.deadline({ ...params, view: true }),
		...overrides,
	}),
};
