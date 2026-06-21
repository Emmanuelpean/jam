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

export function getTableIcon(title: string): string {
	const iconMap: Record<string, string> = {
		Jobs: getEntityIcon("job"),
		Companies: getEntityIcon("company"),
		Contacts: getEntityIcon("person"),
		Tags: getEntityIcon("keyword"),
		"Job Application Updates": getEntityIcon("jobApplicationUpdate"),
		Interviews: getEntityIcon("interview"),
		"Job Aggregators": getEntityIcon("aggregator"),
		"Speculative Applications": getEntityIcon("speculativeApplication"),
		Dashboard: "house-door",
		"Job Applications": "person-workspace",
		Users: getEntityIcon("user"),
		Settings: getEntityIcon("setting"),
		"Job Alerts": getEntityIcon("scrapedJob"),
		"Job Emails": getEntityIcon("jobEmail"),
		"My Account": "gear",
		"Job Scraping Dashboard": "envelope-arrow-down",
		About: "info-circle",
		Admin: "person-gear",
		"Job Rating Dashboard": "star-half",
		"Email Templates": "envelope-open",
		Other: "three-dots",
		"Release Notes": "file-earmark-text",
		"Browser Extension": "puzzle-fill",
		"About JAM": "window-sidebar",
		"Service Dashboards": "stack",
		"App Management": "terminal",
		Files: "folder2-open",
		ESM: "bank",
	};
	return iconMap[title] || "bi-table";
}

export function getEntityIcon(entityType: EntityType): string {
	const iconMap: Record<string, string> = {
		job: "briefcase",
		company: "building",
		person: "people",
		location: "geo-alt",
		keyword: "tags",
		interview: "calendar-event",
		jobApplicationUpdate: "bell",
		aggregator: "linkedin",
		user: "person-lines-fill",
		setting: "database-gear",
		speculativeApplication: "envelope-paper",
		scrapedJob: "inboxes",
		scrapingFilter: "funnel",
		jobEmail: "envelope-open",
		file: "files-alt",
	};
	return iconMap[entityType] || "";
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
