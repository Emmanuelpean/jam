import React, { JSX, useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { getTableIcon } from "../rendering/view/Icons";
import { ThemeSelector } from "./ThemeSelector";
import "./Sidebar.scss";
import { DEFAULT_THEME } from "../../utils/Theme";

interface NavigationItem {
	path?: string;
	icon?: string;
	text: string;
	submenu?: NavigationSubItem[];
	adminOnly?: boolean;
	position: "top" | "bottom";
	onClick?: () => void;
	className?: string;
}

interface NavigationSubItem {
	path: string;
	icon?: string;
	text: string;
}

export const Sidebar = (): JSX.Element => {
	const location = useLocation();
	const { logout, currentUser } = useAuth();
	const [showDropdown, setShowDropdown] = useState<boolean>(false);
	const [isExpanded, setIsExpanded] = useState<boolean>(false);
	const [expandedSubmenu, setExpandedSubmenu] = useState<string | null>(null);
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
		{ path: "/scraped-jobs", text: "Job Alerts", position: "top" },
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
		{ path: "/about", text: "About", position: "bottom" },
		{
			text: "Admin",
			adminOnly: true,
			position: "bottom",
			submenu: [
				{ path: "/job-scraping-dashboard", text: "Job Scraping Dashboard" },
				{ path: "/job-rating-dashboard", text: "Job Rating Dashboard" },
				{ path: "/users", text: "Users" },
				{ path: "/app-settings", text: "Settings" },
			],
		},
		{
			icon: "box-arrow-right",
			text: "Logout",
			position: "bottom",
			onClick: logout,
			className: "logout-item",
		},
	];

	const getFilteredNavigationItems = (position: string): NavigationItem[] => {
		let filteredItems: NavigationItem[] = navigationItems.filter(
			(item: NavigationItem): boolean => item.position === position
		);
		if (currentUser?.is_admin) {
			return filteredItems;
		} else {
			return filteredItems.filter((item: NavigationItem): boolean => !item.adminOnly);
		}
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
		collapseTimeoutRef.current = setTimeout(() => {
			setIsExpanded(false);
			setShowDropdown(false);
			// Collapse inactive submenus
			navigationItems.forEach((item: NavigationItem): void => {
				if (
					item.submenu &&
					expandedSubmenu === item.text &&
					!isGroupMenuActive(item.submenu)
				) {
					setExpandedSubmenu(null);
				}
			});
		}, 300);
	};

	const isMenuActive = (path: string): boolean => {
		// Check if the current path starts with the menu item's path
		return location.pathname.startsWith(path);
	};

	const isGroupMenuActive = (submenu: NavigationSubItem[]): boolean => {
		// Check if any item in the group menu matches the current path
		return submenu.some((item: NavigationSubItem): boolean => location.pathname === item.path);
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
									className={`nav-item submenu-item ${isMenuActive(subItem.path) ? "active" : ""}`}
									style={{
										transitionDelay: showSubmenu
											? `${subIndex * 0.05 + 0.1}s`
											: `${(item.submenu!.length - subIndex - 1) * 0.03}s`,
									}}
								>
									<span className="nav-icon">
										<i
											className={`bi bi-${subItem?.icon || getTableIcon(subItem.text)}`}
										></i>
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
				<button
					className="sidebar-open-btn"
					onClick={handleSidebarToggle}
					aria-label="Toggle sidebar"
				>
					<i className="bi bi-list" style={{ fontSize: 24 }}></i>
				</button>
			)}
			<div
				className={`custom-sidebar ${isExpanded ? "expanded" : "collapsed"}`}
				onMouseEnter={!isMobile ? handleMouseEnter : undefined}
				onMouseLeave={!isMobile ? handleMouseLeave : undefined}
			>
				{isMobile && isExpanded && (
					<button
						className="sidebar-close-btn"
						onClick={handleSidebarToggle}
						aria-label="Close sidebar"
					>
						<i className="bi bi-x-lg" style={{ fontSize: 24 }}></i>
					</button>
				)}
				<div className="sidebar-header">
					<div ref={dropdownRef}>
						<div
							onClick={() => setShowDropdown(!showDropdown)}
							style={{ cursor: "pointer" }}
						>
							<div className="logo-container">
								<JamLogo
									style={{
										height: "57px",
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

				<nav className="sidebar-nav sidebar-nav-top">
					{renderNavigationItems(topNavigationItems)}
				</nav>

				<nav className="sidebar-nav sidebar-nav-bottom">
					{renderNavigationItems(bottomNavigationItems)}
				</nav>
			</div>
		</>
	);
};
