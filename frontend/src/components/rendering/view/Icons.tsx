import React, { ReactNode } from "react";
import { EntityType } from "../../../contexts/DataContext";

export function getApplicationStatusBadgeClass(status: string | undefined): string {
	switch (status?.toLowerCase()) {
		case "applied":
			return "bg-primary";
		case "interview":
			return "bg-warning";
		case "offer":
			return "bg-success";
		case "rejected":
		case "withdrawn":
			return "bg-secondary";
		default:
			return "bg-primary";
	}
}

export function getUpdateTypeIcon(type: string): string {
	switch (type?.toLowerCase()) {
		case "received":
			return "bi-download";
		default:
			return "bi-upload";
	}
}

// Single source of truth for entity icons — keyed by EntityType so the compiler enforces
// coverage of every entity and catches stale/misspelled keys when the union changes.
const ENTITY_ICONS: Record<EntityType, string> = {
	job: "briefcase",
	company: "building",
	person: "people",
	geolocation: "geo-alt",
	keyword: "tags",
	interview: "calendar-event",
	jobApplicationUpdate: "bell",
	aggregator: "linkedin",
	user: "person-lines-fill",
	setting: "database-gear",
	speculativeApplication: "envelope-paper",
	scrapedJob: "inboxes",
	scrapingExclusionFilter: "funnel",
	scrapingFavouriteFilter: "funnel-fill",
	jobEmail: "envelope-open",
	file: "files",
};

export function getEntityIcon(entityType: EntityType): string {
	return ENTITY_ICONS[entityType];
}

// Single source of truth for icons of pages/sections that aren't backed by a single
// EntityType (dashboards, account/admin pages, static content, tabs that split one
// entity into sub-views). Keyed by a semantic id — never by display title — so renaming
// a label can't silently break its icon, and adding a page requires adding an entry here.
export type PageIconKey =
	| "dashboard"
	| "myAccount"
	| "admin"
	| "about"
	| "aboutJam"
	| "browserExtension"
	| "contactSupport"
	| "jobScrapingDashboard"
	| "jobRatingDashboard"
	| "providerMonitoring"
	| "serviceScheduler"
	| "emailTemplates"
	| "otherMenu"
	| "cvFiles"
	| "coverLetterFiles"
	| "jobApplications"
	| "takeATour"
	| "logout";

const PAGE_ICONS: Record<PageIconKey, string> = {
	dashboard: "house-door",
	myAccount: "gear",
	admin: "person-gear",
	about: "info-circle",
	aboutJam: "window-sidebar",
	browserExtension: "puzzle-fill",
	contactSupport: "envelope",
	jobScrapingDashboard: "envelope-arrow-down",
	jobRatingDashboard: "star-half",
	providerMonitoring: "stack",
	serviceScheduler: "clock-history",
	emailTemplates: "envelope-open",
	otherMenu: "three-dots",
	cvFiles: "folder2-open",
	coverLetterFiles: "files",
	jobApplications: "person-workspace",
	takeATour: "map",
	logout: "box-arrow-right",
};

export function getPageIcon(key: PageIconKey): string {
	return PAGE_ICONS[key];
}

export const getAdminIcon = (isAdmin: boolean): string => {
	if (isAdmin) {
		return "bi bi-person-check text-success";
	} else {
		return "bi bi-person-x text-danger";
	}
};

export const getTrueFalseBadge = (value: boolean): ReactNode => {
	if (value) {
		return <i className="bi bi-check-circle text-success"></i>;
	} else {
		return <i className="bi bi-x-circle text-danger"></i>;
	}
};

export const getLocationIcon = (attendanceType: string | null): string => {
	if (attendanceType === "on-site") return "building";
	if (attendanceType === "hybrid") return "house-door";
	if (attendanceType === "remote") return "house";
	return "";
};
