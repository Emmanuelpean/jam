import React, { ReactNode } from "react";
import { renderFunctions, RenderParams, RenderViewFieldWithContext, ViewField } from "./ViewRenders";

export interface ModalViewField extends ViewField {
	label?: string;
	type?: string;
	isTitle?: boolean;
	displayCondition?: (item: any) => boolean;
}

interface ModalViewFieldOverride extends Partial<ModalViewField> {}

export const renderModalViewField = (field: ModalViewField, item: any, id: string): ReactNode => {
	const output = <RenderViewFieldWithContext field={field} item={item} id={id} />;

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
		render: renderFunctions.isAdmin,
		...overrides,
	}),

	toastActive: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "toast_active",
		label: "TOAST",
		render: renderFunctions.toastActive,
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
		render: (params: RenderParams) => renderFunctions.LocationBadge({ ...params, view: true }),
		...overrides,
	}),

	companyBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "CompanyBadge",
		label: "Company",
		render: renderFunctions.CompanyBadge,
		...overrides,
	}),

	keywordBadges: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "keywords",
		label: "Tags",
		render: (params: RenderParams) => renderFunctions.KeywordBadges({ ...params, view: true }),
		...overrides,
	}),

	personBadges: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "person",
		label: "Contacts",
		render: (params: RenderParams) => renderFunctions.ContactBadges({ ...params, view: true }),
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
		render: (params: RenderParams) => renderFunctions.InterviewerBadges({ ...params, view: true }),
		...overrides,
	}),

	appliedViaBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "applied_via",
		label: "Applied Via",
		render: (params: RenderParams) => renderFunctions.AppliedViaBadge({ ...params, view: true }),
		...overrides,
	}),

	sourceBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "source",
		label: "Source Aggregator",
		render: renderFunctions.SourceBadge,
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

	isActive: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "is_active",
		label: "Active",
		render: (params: RenderParams) => renderFunctions.isActive({ ...params, view: true }),
		...overrides,
	}),

	// ----------------------------------------------------- TABLE -----------------------------------------------------

	interviewTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "interviews",
		render: renderFunctions.InterviewTable,
		...overrides,
	}),

	updateTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "updates",
		render: renderFunctions.JobApplicationUpdateTable,
		...overrides,
	}),

	accordionInterviewTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "interviews",
		render: (param) => renderFunctions.AccordionInterviewTable(param, "location_id"),
		...overrides,
	}),

	accordionJobTableAggregator: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (param: RenderParams) => renderFunctions._accordionJobTable(param, "source_id"),
		...overrides,
	}),

	accordionJobTableCompany: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (param: RenderParams) => renderFunctions._accordionJobTable(param, "company_id"),
		...overrides,
	}),

	accordionJobTableKeyword: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (param: RenderParams) => renderFunctions._accordionJobTable(param, "keywords"),
		...overrides,
	}),

	accordionJobTableLocation: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (param: RenderParams) => renderFunctions._accordionJobTable(param, "location_id"),
		...overrides,
	}),

	accordionJobApplicationTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job_applications",
		render: renderFunctions.accordionJobApplicationTable,
		...overrides,
	}),

	accordionPersonTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "persons",
		render: renderFunctions.AccordionPersonTable,
		...overrides,
	}),

	// ---------------------------------------------------- DATETIME ---------------------------------------------------

	applicationDate: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_date",
		label: "Application Date",
		render: (params: RenderParams) => renderFunctions._date(params, "application_date"),
		...overrides,
	}),

	date: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "date",
		label: "Date",
		render: (params: RenderParams) => renderFunctions._date(params, "date"),
		...overrides,
	}),

	datetime: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "date",
		label: "Date & Time",
		render: renderFunctions.datetime,
		...overrides,
	}),

	deadline: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "deadline",
		label: "Application Deadline",
		render: (params: RenderParams) => renderFunctions._date(params, "deadline"),
		...overrides,
	}),

	followupSnoozeDateTime: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "followup_snooze_datetime",
		label: "Follow-up Snooze Until",
		render: (param: RenderParams) => renderFunctions._date(param, "followup_snooze_datetime"),
		...overrides,
		displayCondition: (item: any) => item.followup_snooze_datetime !== null,
	}),
};
