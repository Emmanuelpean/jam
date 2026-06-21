import React, { JSX, useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useTour } from "../../contexts/TourContext";
import JamLogo from "../../assets/Logo.svg?react";
import { getTableIcon } from "../rendering/view/Icons";
import { ThemeSelector } from "./ThemeSelector";
import "./Sidebar.scss";
import { DEFAULT_THEME } from "../../utils/Theme";
import { useViewport } from "../../contexts/ViewportContext";
import { NavigationItem, NavigationSubItem, useNavigation } from "./useNavigation";

export const Sidebar = (): JSX.Element | null => {
	const location = useLocation();
	const { currentUser } = useAuth();
	const { isMobile } = useViewport();
	const { closeTourSelect, isTourActive } = useTour();
	const { navigationItems, topItems: topNavigationItems, bottomItems: bottomNavigationItems } = useNavigation();
	const [showDropdown, setShowDropdown] = useState<boolean>(false);
	const [dropdownTop, setDropdownTop] = useState<number>(72);
	const [isExpanded, setIsExpanded] = useState<boolean>(false);
	const [expandedSubmenu, setExpandedSubmenu] = useState<string | null>(null);

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
		if (location.pathname.startsWith(path)) return true;
		const parts = path.split("/").filter(Boolean);
		if (parts.length > 1) {
			const parent = "/" + parts.slice(0, -1).join("/") + "/";
			return location.pathname.startsWith(parent);
		}
		return false;
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

	// On mobile the sidebar is replaced entirely by the page-header dropdown menu
	// (see MobileNavMenu / PageHeader).
	if (isMobile) return null;

	return (
		<>
			<div
				ref={sidebarRef}
				className={`custom-sidebar ${isExpanded ? "expanded" : "collapsed"}`}
				onMouseEnter={handleMouseEnter}
				onMouseLeave={handleMouseLeave}
			>
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
