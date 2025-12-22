import React, { ReactNode } from "react";

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
		Jobs: "bi-briefcase",
		Companies: "bi-building",
		Persons: "bi-people",
		People: "bi-people",
		Locations: "bi-geo-alt",
		Tags: "bi-tags",
		Interviews: "bi-calendar-event",
		"Job Applications": "bi-person-workspace",
		"Job Application Updates": "bi-bell",
		"Job Aggregators": "bi-linkedin",
		Users: "bi-person-lines-fill",
		Settings: "bi-database-gear",
		"User Settings": "bi-gear",
		"TOAST Dashboard": "bi-envelope-arrow-down",
		About: "bi-info-circle",
		Admin: "bi-person-gear",
		"Job Rating Dashboard": "bi-star-half",
	};
	return iconMap[title] || "bi-table";
}

export const getAdminIcon = (isAdmin: boolean): string => {
	if (isAdmin) {
		return "bi bi-person-check text-success";
	} else {
		return "bi bi-person-x text-danger";
	}
};

export const getToastIcon = (toastActive: boolean): string => {
	if (toastActive) {
		return "bi bi-cup-hot text-success";
	} else {
		return "bi bi-cup text-danger";
	}
};

export const getActiveBadge = (isActive: boolean): ReactNode => {
	if (isActive) {
		return <span className="badge bg-success">Active</span>;
	} else {
		return <span className="badge bg-secondary">Inactive</span>;
	}
};

export const getTrueFalseBadge = (value: boolean): ReactNode => {
	if (value) {
		return <i className="bi bi-check-circle text-success"></i>;
	} else {
		return <i className="bi bi-x-circle text-danger"></i>;
	}
};
