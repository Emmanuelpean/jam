import React, { JSX, useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import JamLogo from "../../assets/Logo.svg?react";
import { getTableIcon } from "../rendering/view/Icons";
import { ThemeSelector } from "./ThemeSelector";
import "./Sidebar.scss";
import { DEFAULT_THEME } from "../../utils/Theme";
import { UserData } from "../../services/schemas/Core";
import { useAlert } from "../../contexts/AlertContext";

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
}

interface NavigationSubItem {
	path: string;
	icon?: string;
	text: string;
	alsoActiveFor?: string[];
}

export const Sidebar = (): JSX.Element => {
	const location = useLocation();
	const { logout, currentUser } = useAuth();
	const { showDelete } = useAlert();
	const [showDropdown, setShowDropdown] = useState<boolean>(false);
	const [isExpanded, setIsExpanded] = useState<boolean>(false);
	const [expandedSubmenu, setExpandedSubmenu] = useState<string | null>(null);

	const handleLogoutClick = async (): Promise<void> => {
		if (currentUser?.is_demo) {
			const confirmed: boolean = await showDelete({
				title: "Log out of demo account?",
				message:
					"All demo data — including your jobs, companies, and settings — will be permanently deleted when you log out.",
				cancelText: "Stay",
				confirmText: "Log out",
			});
			if (confirmed) logout();
		} else {
			logout();
		}
	};

	const expandTimeoutRef = useRef<NodeJS.Timeout | null>(null);
	const collapseTimeoutRef = useRef<NodeJS.Timeout | null>(null);
	const dropdownRef = useRef<HTMLDivElement | null>(null);
	const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth <= 990);

	useEffect(() => {
		const handleResize = (): void => setIsMobile(window.innerWidth <= 990);
		window.addEventListener("resize", handleResize);
		return (): void => window.removeEventListener("resize", handleResize);
	}, []);

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

	const handleSidebarToggle = (): void => setIsExpanded((prev: boolean): boolean => !prev);

	const navigationItems: NavigationItem[] = [
		{ path: "/dashboard", text: "Dashboard", position: "top" },
		{ path: "/jobs", text: "Jobs", position: "top" },
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
				{ path: "/locations", text: "Locations" },
				{ path: "/aggregators", text: "Job Aggregators" },
				{ path: "/keywords", text: "Tags" },
				{ path: "/interviews", text: "Interviews" },
				{ path: "/job-application-updates", text: "Job Application Updates" },
			],
		},
		{ path: "/settings", text: "User Settings", position: "bottom" },
		{
			text: "About",
			position: "bottom",
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
		expandTimeoutRef.current = setTimeout(() => {
			setIsExpanded(true);
		}, 200);
	};

	const handleMouseLeave = () => {
		if (expandTimeoutRef.current) {
			clearTimeout(expandTimeoutRef.current);
			expandTimeoutRef.current = null;
		}
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
							{item.submenu.map((subItem: NavigationSubItem, subIndex: number) => (
								<Link
									key={subItem.text}
									to={subItem.path}
									className={`nav-item submenu-item ${isSubMenuItemActive(subItem) ? "active" : ""}`}
									style={{
										transitionDelay: showSubmenu
											? `${subIndex * 0.05 + 0.1}s`
											: `${(item.submenu!.length - subIndex - 1) * 0.03}s`,
									}}
								>
									<span className="nav-icon">
										<i className={`bi bi-${subItem?.icon || getTableIcon(subItem.text)}`}></i>
									</span>
									<span className="nav-text-container">
										<span className="nav-text">{subItem.text}</span>
									</span>
								</Link>
							))}
						</div>
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
			{isMobile && !isExpanded && (
				<button className="sidebar-open-btn" onClick={handleSidebarToggle} aria-label="Toggle sidebar">
					<i className="bi bi-list" style={{ fontSize: 21.6 }}></i>
				</button>
			)}
			<div
				className={`custom-sidebar ${isExpanded ? "expanded" : "collapsed"}`}
				onMouseEnter={!isMobile ? handleMouseEnter : undefined}
				onMouseLeave={!isMobile ? handleMouseLeave : undefined}
			>
				{isMobile && isExpanded && (
					<button className="sidebar-close-btn" onClick={handleSidebarToggle} aria-label="Close sidebar">
						<i className="bi bi-x-lg" style={{ fontSize: 21.6 }}></i>
					</button>
				)}
				<div className="sidebar-header">
					<div ref={dropdownRef}>
						<div onClick={() => setShowDropdown(!showDropdown)} style={{ cursor: "pointer" }}>
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
						/>
					</div>
				</div>

				<nav className="sidebar-nav sidebar-nav-top">{renderNavigationItems(topNavigationItems)}</nav>

				<nav className="sidebar-nav sidebar-nav-bottom">{renderNavigationItems(bottomNavigationItems)}</nav>
			</div>
		</>
	);
};
