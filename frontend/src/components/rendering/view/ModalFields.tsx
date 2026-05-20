import React, { ReactNode } from "react";
import { renderFunctions, RenderParams, RenderViewFieldWithContext, ViewField } from "./ViewRenders";

export interface ModalViewField extends ViewField {
	label?: string;
	type?: string;
	isTitle?: boolean;
	displayCondition?: (item: any) => boolean;
	icon?: string;
}

export type ModalViewFields = (ModalViewField | ModalViewField[])[];

interface ModalViewFieldOverride extends Partial<ModalViewField> {}

export const ModalViewFieldRenderer = ({ field, item, id }: { field: ModalViewField; item: any; id: string }): ReactNode => {
	const output = <RenderViewFieldWithContext field={field} item={item} id={id} view={true} />;

	if (field.isTitle) {
		return (
			<div className="text-center p-1">
				<h2 className="display-6 fw-bold mt-4 mb-4" style={{ color: "var(--primary-mid)" }}>
					{output}
				</h2>
			</div>
		);
	}
	if (field.label) {
		return (
			<>
				<h6 className="mb-2 fw-bold">
					{field.icon && <i className={`bi ${field.icon} me-2`} />}
					{field.label}
				</h6>
				<div className="mb-3">{output}</div>
			</>
		);
	}
	return <div className="mb-3">{output}</div>;
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

	company: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "company",
		label: "Company",
		...overrides,
	}),

	location: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "location",
		label: "Location",
		render: renderFunctions.locationAttendance,
		displayCondition: (item: any) => !!item.location,
		...overrides,
	}),

	platform: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "platform",
		label: "Aggregator",
		render: renderFunctions.platform,
		...overrides,
	}),

	value: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "value",
		label: "Value",
		render: (params: RenderParams) => renderFunctions.value({ ...params }),
		...overrides,
	}),

	description: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "description",
		label: "Description",
		render: (params: RenderParams) => renderFunctions.description({ ...params }),
		...overrides,
	}),

	note: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "note",
		label: "Notes",
		render: (params: RenderParams) => renderFunctions.note({ ...params }),
		...overrides,
	}),

	applicationNote: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_note",
		render: (params: RenderParams) => renderFunctions.applicationNote({ ...params }),
		...overrides,
	}),

	interviewType: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "type",
		label: "Type",
		render: renderFunctions.interviewType,
		...overrides,
	}),

	isAdmin: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "is_admin",
		label: "Admin",
		render: renderFunctions.isAdmin,
		...overrides,
	}),

	premiumActive: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "premium_active",
		label: "Premium Active",
		render: renderFunctions.premiumActive,
		...overrides,
	}),

	jobRatingActive: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job_rating_active",
		label: "Job Rating Active",
		render: renderFunctions.jobRatingActive,
		...overrides,
	}),

	jobScrapingActive: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job_scraping_active",
		label: "Job Rating Active",
		render: renderFunctions.jobScrapingActive,
		...overrides,
	}),

	city: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "city",
		label: "City",
		render: (param: RenderParams) => param.item?.geolocation?.city ?? param.item?.city ?? null,
		displayCondition: (item: any) => !!(item.geolocation?.city ?? item.city),
		...overrides,
	}),

	postcode: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "postcode",
		label: "Postcode",
		render: (param: RenderParams) => param.item?.geolocation?.postcode ?? param.item?.postcode ?? null,
		displayCondition: (item: any) => !!(item.geolocation?.postcode ?? item.postcode),
		...overrides,
	}),

	country: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "country",
		label: "Country",
		render: (param: RenderParams) => param.item?.geolocation?.country ?? param.item?.country ?? null,
		displayCondition: (item: any) => !!(item.geolocation?.country ?? item.country),
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

	scrapingFilterName: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "name",
		label: "Filter Name",
		render: renderFunctions.scrapingFilterName,
		...overrides,
	}),

	sourceType: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "source_type",
		label: "Source",
		render: renderFunctions.sourceType,
		...overrides,
	}),

	// --------------------------------------------------- LINK/EMAIL --------------------------------------------------

	url: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "url",
		label: "Website",
		render: renderFunctions.url,
		...overrides,
	}),

	jobUrl: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job_url",
		label: "Job URL",
		render: renderFunctions.url,
		...overrides,
	}),

	applicationUrl: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_url",
		label: "Application URL",
		render: renderFunctions.applicationUrl,
		...overrides,
	}),

	applicationCv: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "cv_id",
		label: "CV",
		render: renderFunctions.applicationCv,
		...overrides,
	}),

	applicationCoverLetter: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "cover_letter_id",
		label: "Cover Letter",
		render: renderFunctions.applicationCoverLetter,
		...overrides,
	}),

	email: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "email",
		label: "Email",
		render: renderFunctions.email,
		...overrides,
	}),

	contactEmail: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "contact_email",
		label: "Contact Email",
		render: renderFunctions.contactEmail,
		...overrides,
	}),

	linkedinUrl: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "linkedin_url",
		label: "LinkedIn Profile",
		render: renderFunctions.linkedinUrl,
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
		render: renderFunctions.locationBadge,
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
		render: renderFunctions.KeywordBadges,
		...overrides,
	}),

	personBadges: (overrides: ModalViewFieldOverride = {}, menuItemKeys?: string[]): ModalViewField => ({
		key: "person",
		label: "Contacts",
		render: (params: RenderParams): ReactNode => renderFunctions.ContactBadges(params, menuItemKeys),
		...overrides,
	}),

	jobBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job",
		label: "Job",
		render: (params: RenderParams) => renderFunctions.jobBadge(params),
		...overrides,
	}),

	interviewerBadges: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "person",
		label: "Interviewers",
		render: renderFunctions.InterviewerBadges,
		...overrides,
	}),

	appliedViaBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "applied_via",
		label: "Applied Via",
		render: renderFunctions.AppliedViaBadge,
		...overrides,
	}),

	sourceAggregatorBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "source",
		label: "Source Aggregator",
		render: renderFunctions.SourceBadge,
		...overrides,
	}),

	recruiterBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "recruiter_id",
		label: "Source Recruiter",
		render: renderFunctions.recruiterBadge,
		...overrides,
	}),

	recruitmentCompanyBadge: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "recruiter_company_id",
		label: "Source Recruitment Company",
		render: renderFunctions.recruitmentCompanyBadge,
		...overrides,
	}),

	// ----------------------------------------------------- OTHER -----------------------------------------------------

	geolocationMap: (scrollWheelZoom = true, overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "location_map",
		label: "Location on Map",
		type: "custom",
		render: (param) => renderFunctions.locationMap(param, scrollWheelZoom),
		displayCondition: (item): boolean => !!item.location && item.attendance_type !== "remote",
		...overrides,
	}),

	phone: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "phone",
		label: "Phone",
		render: renderFunctions.phone,
		...overrides,
	}),

	salaryRange: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "salary_range",
		label: "Salary Range",
		render: renderFunctions.salaryRange,
		...overrides,
	}),

	personalRating: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "personal_rating",
		label: "Personal Rating",
		render: (params: RenderParams) => renderFunctions.personalRating({ ...params }),
		...overrides,
	}),

	isFavourite: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "is_favourite",
		label: "Favourite",
		render: renderFunctions.isFavourite,
		...overrides,
	}),

	applicationStatus: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "application_status",
		label: "Status",
		render: renderFunctions.applicationStatus,
		...overrides,
	}),

	isActive: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "is_active",
		label: "Active",
		render: renderFunctions.isActive,
		...overrides,
	}),

	isRecruiter: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "is_recruiter",
		label: "Recruiter",
		render: renderFunctions.isRecruiter,
		...overrides,
	}),

	caseSensitive: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "case_sensitive",
		label: "Case Sensitive",
		render: renderFunctions.caseSensitive,
		...overrides,
	}),

	jobRatingSection: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job_rating_section",
		render: (params: RenderParams) => renderFunctions.jobRatingSection(params),
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

	accordionInterviewTablePerson: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "interviews",
		render: (param) => renderFunctions.AccordionInterviewTable(param, "interviewers"),
		...overrides,
	}),

	accordionJobTableAggregator: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (param: RenderParams) => renderFunctions._accordionJobTable(param, "source_aggregator_id"),
		...overrides,
	}),

	accordionJobTablePerson: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (param: RenderParams) => renderFunctions._accordionJobTable(param, "contacts"),
		...overrides,
	}),

	accordionRecruitedJobTablePerson: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "recruited_jobs",
		render: (param: RenderParams) => renderFunctions._accordionJobTable(param, "recruiter_id", "Submitted Jobs"),
		...overrides,
	}),

	accordionRecruitedJobTableCompany: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "recruited_jobs",
		render: (param: RenderParams) =>
			renderFunctions._accordionJobTable(param, "recruitment_company_id", "Submitted Jobs"),
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

	accordionScrapedJobTable: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "filtered_jobs",
		render: renderFunctions.accordionScrapedJobTable,
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

	// --------------------------------------------------- JOB EMAIL --------------------------------------------------

	emailSender: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "sender",
		label: "From",
		...overrides,
	}),

	emailAlertName: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "alert_name",
		label: "Alert Name",
		...overrides,
	}),

	emailJobFoundN: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "job_found_n",
		label: "Jobs Found",
		...overrides,
	}),

	emailDateReceived: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "date_received",
		label: "Date Received",
		render: (params: RenderParams) => renderFunctions._date(params, "date_received"),
		...overrides,
	}),

	emailBody: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "body",
		label: "Email Body",
		render: (params: RenderParams) => renderFunctions.htmlBody(params, "body"),
		...overrides,
	}),

	emailScrapedJobs: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (params: RenderParams) => renderFunctions.emailScrapedJobTable(params),
		displayCondition: (item) => Array.isArray(item.jobs) && item.jobs.length > 0,
		...overrides,
	}),

	emailScrapedJobsReadOnly: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "jobs",
		render: (params: RenderParams) => renderFunctions.emailScrapedJobTableReadOnly(params),
		displayCondition: (item) => Array.isArray(item.jobs) && item.jobs.length > 0,
		...overrides,
	}),

	scrapedJobEmails: (overrides: ModalViewFieldOverride = {}): ModalViewField => ({
		key: "emails",
		render: (params: RenderParams) => renderFunctions.scrapedJobEmailTable(params),
		displayCondition: (item) => Array.isArray(item.emails) && item.emails.length > 0,
		...overrides,
	}),
};
