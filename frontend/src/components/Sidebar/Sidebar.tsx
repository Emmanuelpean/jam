import React, { JSX, useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useTour } from "../../contexts/TourContext";
import JamLogo from "../../assets/Logo.svg?react";
import { getTableIcon } from "../rendering/view/Icons";
import { TOURS } from "../GuidedTour/tourSteps";
import { ThemeSelector } from "./ThemeSelector";
import "./Sidebar.scss";
import { DEFAULT_THEME } from "../../utils/Theme";
import { UserData } from "../../services/schemas/Core";
import { useAlert } from "../../contexts/AlertContext";
import { useViewport } from "../../contexts/ViewportContext";

interface NavigationItem {
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

interface NavigationSubItem {
	path?: string;
	icon?: string;
	text: string;
	alsoActiveFor?: string[];
	onClick?: () => void;
	id?: string;
}

export const Sidebar = (): JSX.Element => {
	const location = useLocation();
	const { logout, currentUser } = useAuth();
	const { isMobile } = useViewport();
	const { toggleTourSelect, closeTourSelect, isTourActive, completedTourIds } = useTour();
	const { showLogout } = useAlert();
	const isPremium = currentUser?.premium.is_active ?? false;
	const implementedTours = TOURS.filter(
		(t) => !t.comingSoon && (isPremium || !["import-scraped-job", "scraping-filters"].includes(t.id))
	);
	const allToursCompleted = implementedTours.length > 0 && implementedTours.every((t) => completedTourIds.has(t.id));
	const [showDropdown, setShowDropdown] = useState<boolean>(false);
	const [dropdownTop, setDropdownTop] = useState<number>(72);
	const [isExpanded, setIsExpanded] = useState<boolean>(false);
	const [expandedSubmenu, setExpandedSubmenu] = useState<string | null>(null);

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

	const collapseTimeoutRef = useRef<NodeJS.Timeout | null>(null);
	const dropdownRef = useRef<HTMLDivElement | null>(null);
	const sidebarRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		const handleClickOutside = (event: MouseEvent) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
				setShowDropdown(false);
			}
		};

		// Only add listener when dropdown is visible
		if (showDropdown) {
			document.addEventListener("mousedown", handleClickOutside);
		}

		return () => {
			document.removeEventListener("mousedown", handleClickOutside);
		};
	}, [showDropdown]);

	useEffect(() => {
		if (!isMobile || !isExpanded) return;
		const blockEvent = (event: Event) => {
			event.stopPropagation();
			event.preventDefault();
		};
		const handleClickOutside = (event: MouseEvent) => {
			if (sidebarRef.current && !sidebarRef.current.contains(event.target as Node)) {
				event.stopPropagation();
				event.preventDefault();
				setIsExpanded(false);
				document.addEventListener("click", blockEvent, { capture: true, once: true });
			}
		};
		document.addEventListener("mousedown", handleClickOutside, { capture: true });
		return () => document.removeEventListener("mousedown", handleClickOutside, { capture: true });
	}, [isMobile, isExpanded]);

	const handleSidebarToggle = (): void => setIsExpanded((prev: boolean): boolean => !prev);

	const navigationItems: NavigationItem[] = [
		{ path: "/dashboard", text: "Dashboard", position: "top" },
		{ path: "/jobs", text: "Jobs", position: "top", id: "nav-jobs", tourId: "nav-jobs" },
		{
			path: "/scraped-jobs",
			text: "Job Alerts",
			position: "top",
			condition: (user: UserData): boolean => user.premium.is_active,
		},
		{ path: "/speculative-applications", text: "Speculative Applications", position: "top" },
		{ path: "/persons", text: "People", position: "top" },
		{ path: "/companies", text: "Companies", position: "top" },
		{
			text: "Other",
			position: "top",
			submenu: [
				{ path: "/aggregators", text: "Job Aggregators" },
				{ path: "/keywords", text: "Tags" },
				{ path: "/interviews", text: "Interviews" },
				{ path: "/job-application-updates", text: "Job Application Updates" },
			],
		},
		{ path: "/settings", text: "User Settings", id: "nav-user-settings", position: "bottom" },
		{
			text: "About",
			position: "bottom",
			id: "nav-about",
			submenu: [
				{ path: "/about", text: "About JAM" },
				{ path: "/browser-extension", text: "Browser Extension" },
				{ path: "/release-notes", text: "Release Notes" },
			],
		},
		{
			text: "Admin",
			condition: (user: UserData): boolean => user.is_admin,
			position: "bottom",
			submenu: [
				{ path: "/services/job-scraping", text: "Service Dashboards", alsoActiveFor: ["/services/job-rating"] },
				{
					path: "/app/users",
					text: "App Management",
					alsoActiveFor: ["/app/settings", "/app/email-templates"],
				},
			],
		},
		...(!allToursCompleted
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

	const getFilteredNavigationItems = (position: string): NavigationItem[] => {
		return navigationItems
			.filter((item: NavigationItem): boolean => item.position === position)
			.filter((item: NavigationItem): boolean => {
				// If no condition exists, always include the item
				if (!item.condition) return true;
				// If condition exists but no user, treat as false
				if (!currentUser) return false;
				// If both condition and user exist, evaluate the condition
				return item.condition(currentUser);
			});
	};

	const topNavigationItems: NavigationItem[] = getFilteredNavigationItems("top");

	const bottomNavigationItems: NavigationItem[] = getFilteredNavigationItems("bottom");

	const handleThemeChange = (): void => {
		setShowDropdown(false);
	};

	const handleMouseEnter = () => {
		if (collapseTimeoutRef.current) {
			clearTimeout(collapseTimeoutRef.current);
			collapseTimeoutRef.current = null;
		}
		setIsExpanded(true);
	};

	const handleMouseLeave = () => {
		if (isTourActive) return;
		collapseTimeoutRef.current = setTimeout(() => {
			setIsExpanded(false);
			setShowDropdown(false);
			// Collapse inactive submenus
			navigationItems.forEach((item: NavigationItem): void => {
				if (item.submenu && expandedSubmenu === item.text && !isGroupMenuActive(item.submenu)) {
					setExpandedSubmenu(null);
				}
			});
		}, 300);
	};

	const isSubMenuItemActive = (item: NavigationSubItem): boolean => {
		if (!item.path) return false;
		if (location.pathname.startsWith(item.path)) return true;
		return item.alsoActiveFor?.some((p: string): boolean => location.pathname.startsWith(p)) ?? false;
	};

	const isMenuActive = (path: string): boolean => {
		return location.pathname.startsWith(path);
	};

	const isGroupMenuActive = (submenu: NavigationSubItem[]): boolean => {
		return submenu.some(isSubMenuItemActive);
	};

	const handleGroupMenuToggle = (submenuText: string): void => {
		// Toggle submenu with specified text expansion
		setExpandedSubmenu(expandedSubmenu === submenuText ? null : submenuText);
	};

	const shouldShowGroupMenu = (item: NavigationItem): boolean => {
		// Determine if a submenu should be shown based on expansion state and active items
		if (!item.submenu) return false;
		const isSubmenuExpanded = expandedSubmenu === item.text;
		const hasActiveItem = isGroupMenuActive(item.submenu);
		return (isExpanded && isSubmenuExpanded) || hasActiveItem;
	};

	const renderNavigationItems = (items: NavigationItem[]): JSX.Element[] => {
		return items.map((item: NavigationItem): JSX.Element => {
			if (item.submenu) {
				const isSubmenuItemActive: boolean = isGroupMenuActive(item.submenu);
				const isSubmenuExpanded: boolean = expandedSubmenu === item.text;
				const showSubmenu: boolean = shouldShowGroupMenu(item);

				return (
					<div key={`submenu-${item.text}`}>
						<div
							id={item.id}
							className={`nav-item ${isSubmenuItemActive ? "active" : ""}`}
							onClick={() => isExpanded && handleGroupMenuToggle(item.text)}
							style={{ cursor: isExpanded ? "pointer" : "default" }}
						>
							<span className="nav-icon">
								<i className={`bi bi-${item?.icon || getTableIcon(item.text)}`}></i>
							</span>
							<span className="nav-text-container">
								<span className="nav-text">{item.text}</span>
							</span>
							<span
								className={`submenu-arrow ${isSubmenuExpanded || isSubmenuItemActive ? "expanded" : ""}`}
							>
								<i className="bi bi-chevron-right"></i>
							</span>
						</div>

						<div className={`submenu ${showSubmenu ? "open" : ""}`}>
							{/*Create the submenus*/}
							{item.submenu.map((subItem: NavigationSubItem, subIndex: number) => {
								const transitionDelay = showSubmenu
									? `${subIndex * 0.05 + 0.1}s`
									: `${(item.submenu!.length - subIndex - 1) * 0.03}s`;
								const inner = (
									<>
										<span className="nav-icon">
											<i className={`bi bi-${subItem?.icon || getTableIcon(subItem.text)}`}></i>
										</span>
										<span className="nav-text-container">
											<span className="nav-text">{subItem.text}</span>
										</span>
									</>
								);
								if (subItem.onClick) {
									return (
										<div
											key={subItem.text}
											id={subItem.id}
											className="nav-item submenu-item"
											style={{ transitionDelay, cursor: "pointer" }}
											onClick={subItem.onClick}
											role="button"
											tabIndex={0}
											onKeyDown={(e) => {
												if (e.key === "Enter" || e.key === " ") subItem.onClick?.();
											}}
										>
											{inner}
										</div>
									);
								}
								return (
									<Link
										key={subItem.text}
										to={subItem.path!}
										className={`nav-item submenu-item ${isSubMenuItemActive(subItem) ? "active" : ""}`}
										style={{ transitionDelay }}
									>
										{inner}
									</Link>
								);
							})}
						</div>
					</div>
				);
			}

			if (!item.path && item.onClick) {
				return (
					<div
						key={item.text}
						className={`nav-item ${item.className || ""}`}
						onClick={item.onClick}
						role="button"
						tabIndex={0}
						id={item.id}
						{...(item.tourId ? { "data-tour": item.tourId } : {})}
						onKeyDown={(e) => {
							if (e.key === "Enter" || e.key === " ") item.onClick?.();
						}}
					>
						<span className="nav-icon">
							<i className={`bi bi-${item?.icon || getTableIcon(item.text)}`}></i>
						</span>
						<span className="nav-text-container">
							<span className="nav-text">{item.text}</span>
						</span>
					</div>
				);
			}

			return (
				<Link
					key={item.text}
					to={item.path!}
					className={`nav-item ${isMenuActive(item.path!) ? "active" : ""} ${item.className || ""}`}
					onClick={item.onClick}
					id={item.id}
					{...(item.tourId ? { "data-tour": item.tourId } : {})}
				>
					<span className="nav-icon">
						<i className={`bi bi-${item?.icon || getTableIcon(item.text)}`}></i>
					</span>
					<span className="nav-text-container">
						<span className="nav-text">{item.text}</span>
					</span>
				</Link>
			);
		});
	};

	return (
		<>
			{isMobile && <div className="sidebar-chevron-spacer" />}
			<div
				ref={sidebarRef}
				className={`custom-sidebar ${isExpanded ? "expanded" : "collapsed"}`}
				onMouseEnter={!isMobile ? handleMouseEnter : undefined}
				onMouseLeave={!isMobile ? handleMouseLeave : undefined}
			>
				{isMobile && (
					<button className="sidebar-chevron-btn" onClick={handleSidebarToggle} aria-label="Toggle sidebar">
						<i className={`bi bi-chevron-${isExpanded ? "left" : "right"}`}></i>
					</button>
				)}
				<div className="sidebar-header">
					<div ref={dropdownRef}>
						<div
							onClick={(): void => {
								if (!showDropdown && dropdownRef.current) {
									const r = dropdownRef.current.getBoundingClientRect();
									setDropdownTop(Math.round(r.top + 72));
								}
								setShowDropdown(!showDropdown);
							}}
							style={{ cursor: "pointer" }}
						>
							<div className="logo-container">
								<JamLogo
									style={{
										height: "51px",
										width: "auto",
										userSelect: "none",
									}}
								/>
								<span className="logo-text">JAM</span>
							</div>
						</div>

						<ThemeSelector
							currentTheme={currentUser?.preferences.theme || DEFAULT_THEME}
							onThemeChange={handleThemeChange}
							isVisible={showDropdown && isExpanded}
							dropdownTop={dropdownTop}
						/>
					</div>
				</div>

				<nav
					className="sidebar-nav sidebar-nav-top"
					onClick={(e) => {
						if (!(e.target as HTMLElement).closest("#take-a-tour-btn")) closeTourSelect();
					}}
				>
					{renderNavigationItems(topNavigationItems)}
				</nav>

				<nav
					className="sidebar-nav sidebar-nav-bottom"
					onClick={(e) => {
						if (!(e.target as HTMLElement).closest("#take-a-tour-btn")) closeTourSelect();
					}}
				>
					{renderNavigationItems(bottomNavigationItems)}
				</nav>
			</div>
		</>
	);
};
