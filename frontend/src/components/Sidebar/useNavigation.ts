import { useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useTour } from "../../contexts/TourContext";
import { useAlert } from "../../contexts/AlertContext";
import { useConfig } from "../../contexts/ConfigContext";
import { useViewport } from "../../contexts/ViewportContext";
import { TOURS } from "../GuidedTour/tourSteps";
import { UserData } from "../../services/schemas/Core";

export interface NavigationSubItem {
	path?: string;
	icon?: string;
	text: string;
	alsoActiveFor?: string[];
	onClick?: () => void;
	id?: string;
}

export interface NavigationItem {
	path?: string;
	icon?: string;
	text: string;
	submenu?: NavigationSubItem[];
	condition?: (user: UserData) => boolean;
	position: "top" | "bottom";
	onClick?: () => void;
	className?: string;
	id?: string;
	tourId?: string;
}

interface UseNavigationResult {
	navigationItems: NavigationItem[];
	topItems: NavigationItem[];
	bottomItems: NavigationItem[];
	toggleTourSelect: () => void;
	isMenuActive: (path: string) => boolean;
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
		{ path: "/dashboard", text: "Dashboard", position: "top", id: "nav-dashboard" },
		{ path: "/jobs", text: "Jobs", position: "top", id: "nav-jobs", tourId: "nav-jobs" },
		{
			path: "/job-alerts/jobs",
			text: "Job Alerts",
			position: "top",
			id: "nav-scraped-jobs",
			tourId: "nav-scraped-jobs",
			condition: (user: UserData): boolean => user.premium.is_active,
		},
		{
			path: "/speculative-applications",
			text: "Speculative Applications",
			position: "top",
			id: "nav-speculative-applications",
			tourId: "nav-speculative-applications",
		},
		{ path: "/contacts", text: "Contacts", position: "top", id: "nav-contacts" },
		{ path: "/companies", text: "Companies", position: "top", id: "nav-companies" },
		{
			text: "Other",
			position: "top",
			id: "nav-other",
			submenu: [
				{ path: "/aggregators", text: "Job Aggregators", id: "nav-aggregators" },
				{ path: "/keywords", text: "Tags", id: "nav-tags" },
				{ path: "/interviews", text: "Interviews", id: "nav-interviews" },
				{ path: "/job-application-updates", text: "Job Application Updates", id: "nav-job-application-updates" },
				{ path: "/files", text: "Files", id: "nav-files" },
			],
		},
		{ path: "/settings", text: "My Account", id: "nav-user-settings", position: "bottom" },
		{
			text: "About",
			position: "bottom",
			id: "nav-about",
			submenu: [
				{ path: "/about", text: "About JAM", id: "nav-about-jam" },
				{ path: "/browser-extension", text: "Browser Extension", id: "nav-browser-extension" },
				{
					text: "Contact Support",
					icon: "envelope",
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
			condition: (user: UserData): boolean => user.is_admin,
			position: "bottom",
			id: "nav-admin",
		},
		...(!allToursCompleted && !tourPanelDismissed && !isMobile
			? [
					{
						icon: "map",
						text: "Take a Tour",
						position: "bottom" as const,
						id: "take-a-tour-btn",
						onClick: toggleTourSelect,
					},
				]
			: []),
		{
			icon: "box-arrow-right",
			text: "Logout",
			position: "bottom",
			onClick: handleLogoutClick,
			className: "logout-item",
			id: "logout-btn",
		},
	];

	const isMenuActive = (path: string): boolean => {
		if (location.pathname.startsWith(path)) return true;
		const parts = path.split("/").filter(Boolean);
		if (parts.length > 1) {
			const parent = "/" + parts.slice(0, -1).join("/") + "/";
			return location.pathname.startsWith(parent);
		}
		return false;
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
