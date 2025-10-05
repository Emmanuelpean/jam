import React, { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import "./Sidebar.css";
import { getTableIcon } from "../rendering/view/Icons";
import { DEFAULT_THEME, isValidTheme } from "../../utils/Theme";
import { ThemeSelector } from "./ThemeSelector";

interface NavigationItem {
	path?: string;
	icon?: string;
	text: string;
	submenu?: NavigationSubItem[];
	adminOnly?: boolean;
	position?: "top" | "bottom";
	onClick?: () => void;
	className?: string;
}

interface NavigationSubItem {
	path: string;
	icon?: string;
	text: string;
}

export const Sidebar = () => {
	const location = useLocation();
	const { logout, token, currentUser } = useAuth();
	const [showDropdown, setShowDropdown] = useState<boolean>(false);
	const [currentTheme, setCurrentTheme] = useState<string>(DEFAULT_THEME);
	const [isExpanded, setIsExpanded] = useState<boolean>(false);
	const [expandedSubmenu, setExpandedSubmenu] = useState<string | null>(null);
	const collapseTimeoutRef = useRef<NodeJS.Timeout | null>(null);

	const allNavigationItems: NavigationItem[] = [
		{ path: "/dashboard", icon: "bi-house-door", text: "Dashboard", position: "top" },
		{ path: "/jobs", text: "Jobs", position: "top" },
		{ path: "/interviews", text: "Interviews", position: "top" },
		{ path: "/jobapplicationupdates", text: "Job Application Updates", position: "top" },
		{
			text: "Other",
			icon: "bi-three-dots",
			position: "top",
			submenu: [
				{ path: "/persons", text: "People" },
				{ path: "/locations", text: "Locations" },
				{ path: "/companies", text: "Companies" },
				{ path: "/aggregators", text: "Job Aggregators" },
				{ path: "/keywords", text: "Tags" },
			],
		},
		{ path: "/settings", icon: "bi-gear", text: "User Settings", position: "bottom" },
		{ path: "/about", icon: "bi-info-circle", text: "About", position: "bottom" },
		{
			text: "Admin",
			icon: "bi-person-gear",
			adminOnly: true,
			position: "bottom",
			submenu: [
				{ path: "/eis_dashboard", icon: "bi-envelope-arrow-down", text: "EIS Dashboard" },
				{ path: "/users", text: "Users" },
				{ path: "/app_settings", text: "Settings" },
			],
		},
		{ icon: "bi-box-arrow-right", text: "Logout", position: "bottom", onClick: logout, className: "logout-item" },
	];

	const navigationItems: NavigationItem[] = allNavigationItems.filter(
		(item: NavigationItem): boolean => !(item.adminOnly && !currentUser?.is_admin),
	);

	const topNavigationItems: NavigationItem[] = navigationItems.filter(
		(item: NavigationItem): boolean => item.position !== "bottom",
	);

	const bottomNavigationItems: NavigationItem[] = navigationItems.filter(
		(item: NavigationItem): boolean => item.position === "bottom",
	);

	// Load the saved theme
	useEffect((): void => {
		const savedTheme: string | null = localStorage.getItem("theme");
		const initTheme: string = savedTheme && isValidTheme(savedTheme) ? savedTheme : DEFAULT_THEME;
		setCurrentTheme(initTheme);
		document.documentElement.setAttribute("data-theme", initTheme);
	}, []);

	const handleThemeChange = (themeKey: string) => {
		setCurrentTheme(themeKey);
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
				if (item.submenu && expandedSubmenu === item.text && !isSubmenuActive(item.submenu)) {
					setExpandedSubmenu(null);
				}
			});
		}, 300);
	};

	const isActive = (path: string): boolean => location.pathname === path;

	const isSubmenuActive = (submenu: NavigationSubItem[]): boolean => {
		// Check if any item in the submenu matches the current path
		return submenu.some((item: NavigationItem): boolean => location.pathname === item.path);
	};

	const handleSubmenuToggle = (submenuText: string): void => {
		// Toggle submenu with specified text expansion
		setExpandedSubmenu(expandedSubmenu === submenuText ? null : submenuText);
	};

	const shouldShowSubmenu = (item: NavigationItem) => {
		// Determine if a submenu should be shown based on expansion state and active items
		if (!item.submenu) return false;
		const isSubmenuExpanded = expandedSubmenu === item.text;
		const hasActiveItem = isSubmenuActive(item.submenu);
		return (isExpanded && isSubmenuExpanded) || hasActiveItem;
	};

	const renderNavigationItems = (items: NavigationItem[]) => {
		return items.map((item: NavigationItem) => {
			if (item.submenu) {
				const isSubmenuItemActive = isSubmenuActive(item.submenu);
				const isSubmenuExpanded = expandedSubmenu === item.text;
				const showSubmenu = shouldShowSubmenu(item);

				return (
					<div key={`submenu-${item.text}`}>
						<div
							className={`nav-item ${isSubmenuItemActive ? "active" : ""}`}
							onClick={() => isExpanded && handleSubmenuToggle(item.text)}
							style={{ cursor: isExpanded ? "pointer" : "default" }}
						>
							<span className="nav-icon">
								<i className={`bi ${item?.icon || getTableIcon(item.text)}`}></i>
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
									key={subItem.path}
									to={subItem.path}
									className={`nav-item submenu-item ${isActive(subItem.path) ? "active" : ""}`}
									style={{
										transitionDelay: showSubmenu
											? `${subIndex * 0.05 + 0.1}s`
											: `${(item.submenu!.length - subIndex - 1) * 0.03}s`,
									}}
								>
									<span className="nav-icon">
										<i className={`bi ${subItem?.icon || getTableIcon(subItem.text)}`}></i>
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
					key={item.path}
					to={item.path!}
					className={`nav-item ${isActive(item.path!) ? "active" : ""} ${item.className || ""}`}
					onClick={item.onClick}
				>
					<span className="nav-icon">
						<i className={`bi ${item?.icon || getTableIcon(item.text)}`}></i>
					</span>
					<span className="nav-text-container">
						<span className="nav-text">{item.text}</span>
					</span>
				</Link>
			);
		});
	};

	return (
		<div
			className={`custom-sidebar ${isExpanded ? "expanded" : "collapsed"}`}
			onMouseEnter={handleMouseEnter}
			onMouseLeave={handleMouseLeave}
		>
			<div className="sidebar-header">
				<div onClick={() => setShowDropdown(!showDropdown)} style={{ cursor: "pointer" }}>
					<div className="logo-container">
						<JamLogo style={{ height: "57px", width: "auto" }} />
						<span className="logo-text">JAM</span>
					</div>
				</div>

				<ThemeSelector
					currentTheme={currentTheme}
					token={token}
					onThemeChange={handleThemeChange}
					isVisible={showDropdown && isExpanded}
				/>
			</div>

			<nav className="sidebar-nav sidebar-nav-top">{renderNavigationItems(topNavigationItems)}</nav>

			<nav className="sidebar-nav sidebar-nav-bottom">{renderNavigationItems(bottomNavigationItems)}</nav>
		</div>
	);
};
