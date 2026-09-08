import { useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useTour } from "../../contexts/TourContext";
import { useAlert } from "../../contexts/AlertContext";
import { useConfig } from "../../contexts/ConfigContext";
import { useViewport } from "../../contexts/ViewportContext";
import { TOURS } from "../GuidedTour/tourSteps";
import { UserData } from "../../services/schemas/Core";
import { getEntityIcon, getPageIcon } from "../rendering/view/Icons";

export interface NavigationSubItem {
	path?: string;
	icon: string;
	text: string;
	alsoActiveFor?: string[];
	onClick?: () => void;
	id?: string;
}

export interface NavigationItem {
	path?: string;
	icon: string;
	text: string;
	submenu?: NavigationSubItem[];
	condition?: (user: UserData) => boolean;
	position: "top" | "bottom";
	onClick?: () => void;
	className?: string;
	id?: string;
	tourId?: string;
	alsoActiveFor?: string[];
}

interface UseNavigationResult {
	navigationItems: NavigationItem[];
	topItems: NavigationItem[];
	bottomItems: NavigationItem[];
	toggleTourSelect: () => void;
	isMenuActive: (item: NavigationItem) => boolean;
	isSubItemActive: (item: NavigationSubItem) => boolean;
}

export const useNavigation = (): UseNavigationResult => {
	const location = useLocation();
	const { logout, currentUser } = useAuth();
	const { isMobile } = useViewport();
	const { toggleTourSelect, completedTourIds } = useTour();
	const { showLogout } = useAlert();
	const { config } = useConfig();

	const isPremium = currentUser?.premium.is_active ?? false;
	const implementedTours = TOURS.filter(
		(t) => isPremium || !["import-scraped-job", "scraping-filters"].includes(t.id)
	);
	const allToursCompleted = implementedTours.length > 0 && implementedTours.every((t) => completedTourIds.has(t.id));
	const tourPanelDismissed = currentUser?.preferences.tour_panel_dismissed ?? false;

	const handleLogoutClick = async (): Promise<void> => {
		if (currentUser?.is_demo) {
			const confirmed: boolean = await showLogout({
				title: "Log out of demo account?",
				message:
					"All demo data - including your jobs, companies, and settings - will be permanently deleted when you log out.",
				cancelText: "Stay",
				confirmText: "Log out",
			});
			if (confirmed) logout();
		} else {
			const confirmed: boolean = await showLogout({
				title: "Log out?",
				message: "Are you sure you want to log out?",
				cancelText: "Stay",
				confirmText: "Log out",
			});
			if (confirmed) logout();
		}
	};

	const navigationItems: NavigationItem[] = [
		{ path: "/dashboard", text: "Dashboard", icon: getPageIcon("dashboard"), position: "top", id: "nav-dashboard" },
		{ path: "/jobs", text: "Jobs", icon: getEntityIcon("job"), position: "top", id: "nav-jobs", tourId: "nav-jobs" },
		{
			path: "/job-alerts/jobs",
			text: "Job Alerts",
			icon: getEntityIcon("scrapedJob"),
			position: "top",
			id: "nav-scraped-jobs",
			tourId: "nav-scraped-jobs",
			condition: (user: UserData): boolean => user.premium.is_active,
			alsoActiveFor: isMobile ? undefined : ["/job-alerts/emails"],
		},
		{
			path: "/job-alerts/emails",
			text: "Job Emails",
			icon: getEntityIcon("jobEmail"),
			position: "top",
			id: "nav-job-emails",
			condition: (user: UserData): boolean => isMobile && user.premium.is_active,
		},
		{
			path: "/speculative-applications",
			text: "Speculative Applications",
			icon: getEntityIcon("speculativeApplication"),
			position: "top",
			id: "nav-speculative-applications",
			tourId: "nav-speculative-applications",
		},
		{ path: "/contacts", text: "Contacts", icon: getEntityIcon("person"), position: "top", id: "nav-contacts" },
		{ path: "/companies", text: "Companies", icon: getEntityIcon("company"), position: "top", id: "nav-companies" },
		{
			text: "Other",
			icon: getPageIcon("otherMenu"),
			position: "top",
			id: "nav-other",
			submenu: [
				{
					path: "/aggregators",
					text: "Job Aggregators",
					icon: getEntityIcon("aggregator"),
					id: "nav-aggregators",
				},
				{ path: "/keywords", text: "Tags", icon: getEntityIcon("keyword"), id: "nav-tags" },
				{ path: "/interviews", text: "Interviews", icon: getEntityIcon("interview"), id: "nav-interviews" },
				{
					path: "/job-application-updates",
					text: "Job Application Updates",
					icon: getEntityIcon("jobApplicationUpdate"),
					id: "nav-job-application-updates",
				},
				{
					path: "/files/cv",
					text: isMobile ? "CVs" : "Files",
					icon: getPageIcon("cvFiles"),
					id: "nav-files",
					alsoActiveFor: isMobile ? undefined : ["/files/cover-letters"],
				},
				...(isMobile
					? [
							{
								path: "/files/cover-letters",
								text: "Cover Letters",
								icon: getPageIcon("coverLetterFiles"),
								id: "nav-cover-letters",
							},
						]
					: []),
			],
		},
		{
			path: "/settings",
			text: "My Account",
			icon: getPageIcon("myAccount"),
			id: "nav-user-settings",
			position: "bottom",
		},
		{
			text: "About",
			icon: getPageIcon("about"),
			position: "bottom",
			id: "nav-about",
			submenu: [
				{ path: "/about", text: "About JAM", icon: getPageIcon("aboutJam"), id: "nav-about-jam" },
				{
					path: "/browser-extension",
					text: "Browser Extension",
					icon: getPageIcon("browserExtension"),
					id: "nav-browser-extension",
				},
				{
					text: "Contact Support",
					icon: getPageIcon("contactSupport"),
					id: "nav-contact-support",
					onClick: (): void => {
						if (config?.support_email) {
							window.location.href = `mailto:${config.support_email}`;
						}
					},
				},
			],
		},
		{
			path: "/admin",
			text: "Admin",
			icon: getPageIcon("admin"),
			condition: (user: UserData): boolean => user.is_admin,
			position: "bottom",
			id: "nav-admin",
		},
		...(!allToursCompleted && !tourPanelDismissed && !isMobile
			? [
					{
						icon: getPageIcon("takeATour"),
						text: "Take a Tour",
						position: "bottom" as const,
						id: "take-a-tour-btn",
						onClick: toggleTourSelect,
					},
				]
			: []),
		{
			icon: getPageIcon("logout"),
			text: "Logout",
			position: "bottom",
			onClick: handleLogoutClick,
			className: "logout-item",
			id: "logout-btn",
		},
	];

	const isMenuActive = (item: NavigationItem): boolean => {
		if (!item.path) return false;
		if (location.pathname.startsWith(item.path)) return true;
		return item.alsoActiveFor?.some((p: string): boolean => location.pathname.startsWith(p)) ?? false;
	};

	const isSubItemActive = (item: NavigationSubItem): boolean => {
		if (!item.path) return false;
		if (location.pathname.startsWith(item.path)) return true;
		return item.alsoActiveFor?.some((p: string): boolean => location.pathname.startsWith(p)) ?? false;
	};

	const filterByPosition = (position: "top" | "bottom"): NavigationItem[] =>
		navigationItems
			.filter((item: NavigationItem): boolean => item.position === position)
			.filter((item: NavigationItem): boolean => {
				// If no condition exists, always include the item
				if (!item.condition) return true;
				// If condition exists but no user, treat as false
				if (!currentUser) return false;
				// If both condition and user exist, evaluate the condition
				return item.condition(currentUser);
			});

	return {
		navigationItems,
		topItems: filterByPosition("top"),
		bottomItems: filterByPosition("bottom"),
		toggleTourSelect,
		isMenuActive,
		isSubItemActive,
	};
};
