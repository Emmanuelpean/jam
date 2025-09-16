import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { authApi } from "../../services/Api";
import "./Sidebar.css";
import { getTableIcon } from "../rendering/view/ViewRenders";
import { DEFAULT_THEME, isValidTheme, THEMES } from "../../utils/Theme";

interface NavigationItem {
	path?: string;
	icon?: string;
	text: string;
	submenu?: NavigationSubItem[];
	adminOnly?: boolean;
	position?: "top" | "bottom"; // New positioning option
}

interface NavigationSubItem {
	path: string;
	icon?: string;
	text: string;
}

interface SidebarProps {
	onHoverChange?: (isHovering: boolean) => void;
}

interface CSSColors {
	start: string;
	mid: string;
	end: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ onHoverChange }) => {
	const location = useLocation();
	const { logout, token, is_admin } = useAuth();
	const [showDropdown, setShowDropdown] = useState<boolean>(false);
	const [currentTheme, setCurrentTheme] = useState<string>(DEFAULT_THEME);
	const [hoveredItem, setHoveredItem] = useState<string | null>(null);
	const [isHovering, setIsHovering] = useState<boolean>(false);
	const [expandedSubmenu, setExpandedSubmenu] = useState<string | null>(null);
	const dropdownRef = useRef<HTMLDivElement>(null);
	const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

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
		// Bottom positioned items
		{ path: "/settings", icon: "bi-gear", text: "User Settings", position: "bottom" },
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
	];

	// Filter navigation items based on admin status
	const navigationItems = useMemo(() => {
		return allNavigationItems.filter((item) => {
			// If item has adminOnly flag and user is not admin, exclude it
			return !(item.adminOnly && !is_admin);
		});
	}, [is_admin]);

	// Split items by position
	const topNavigationItems = useMemo(() => {
		return navigationItems.filter((item) => item.position !== "bottom");
	}, [navigationItems]);

	const bottomNavigationItems = useMemo(() => {
		return navigationItems.filter((item) => item.position === "bottom");
	}, [navigationItems]);

	useEffect(() => {
		// Initialize theme
		const savedTheme = localStorage.getItem("theme");
		const initTheme = savedTheme && isValidTheme(savedTheme) ? savedTheme : DEFAULT_THEME;
		setCurrentTheme(initTheme);
		document.documentElement.setAttribute("data-theme", initTheme);
	}, []);

	// Auto-expand submenu if any of its items is active
	useEffect(() => {
		navigationItems.forEach((item) => {
			if (item.submenu && isSubmenuActive(item.submenu)) {
				setExpandedSubmenu(item.text);
			}
		});
	}, [location.pathname, navigationItems]);

	// Close dropdown when clicking outside
	useEffect(() => {
		const handleClickOutside = (event: MouseEvent) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
				setShowDropdown(false);
			}
		};

		document.addEventListener("mousedown", handleClickOutside);
		return () => {
			document.removeEventListener("mousedown", handleClickOutside);
		};
	}, []);

	// Notify parent component about hover state changes
	useEffect(() => {
		if (onHoverChange) {
			onHoverChange(isHovering);
		}
	}, [isHovering, onHoverChange]);

	// Cleanup timeout on unmount
	useEffect(() => {
		return () => {
			if (hoverTimeoutRef.current) {
				clearTimeout(hoverTimeoutRef.current);
			}
		};
	}, []);

	const handleLogoClick = (e: React.MouseEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		setShowDropdown(!showDropdown);
	};

	const handleThemeChange = async (themeKey: string) => {
		setCurrentTheme(themeKey);
		document.documentElement.setAttribute("data-theme", themeKey);
		localStorage.setItem("theme", themeKey);

		if (token) {
			try {
				await authApi.updateCurrentUser({ theme: themeKey }, token);
			} catch (error) {
				console.error("Error saving theme:", error);
			}
		}
		setShowDropdown(false);
	};

	const handleMouseEnter = () => {
		// Clear any existing timeout when mouse re-enters
		if (hoverTimeoutRef.current) {
			clearTimeout(hoverTimeoutRef.current);
			hoverTimeoutRef.current = null;
		}
		setIsHovering(true);
	};

	const handleMouseLeave = () => {
		// Set a delay before collapsing the menu
		hoverTimeoutRef.current = setTimeout(() => {
			setIsHovering(false);
			setShowDropdown(false);
			// Only collapse submenu if none of its items are active
			navigationItems.forEach((item) => {
				if (item.submenu && expandedSubmenu === item.text && !isSubmenuActive(item.submenu)) {
					setExpandedSubmenu(null);
				}
			});
		}, 300);
	};

	const isActive = (path: string) => location.pathname === path;

	const isSubmenuActive = (submenu: NavigationSubItem[]) => {
		return submenu.some((item) => location.pathname === item.path);
	};

	const handleSubmenuToggle = (submenuText: string) => {
		setExpandedSubmenu(expandedSubmenu === submenuText ? null : submenuText);
	};

	const shouldShowSubmenu = (item: NavigationItem) => {
		if (!item.submenu) return false;
		const isExpanded = expandedSubmenu === item.text;
		const hasActiveItem = isSubmenuActive(item.submenu);

		return (isHovering && isExpanded) || hasActiveItem;
	};

	const handleLogout = () => {
		logout();
	};

	const getCurrentCSSColors = (): CSSColors => {
		const computedStyle = getComputedStyle(document.documentElement);
		return {
			start: computedStyle.getPropertyValue("--primary-start").trim(),
			mid: computedStyle.getPropertyValue("--primary-mid").trim(),
			end: computedStyle.getPropertyValue("--primary-end").trim(),
		};
	};

	const getThemeColors = (themeKey: string): CSSColors => {
		const originalTheme = document.documentElement.getAttribute("data-theme");
		document.documentElement.setAttribute("data-theme", themeKey);
		const colors = getCurrentCSSColors();
		if (originalTheme) {
			document.documentElement.setAttribute("data-theme", originalTheme);
		}
		return colors;
	};

	const renderColorPreview = (colors: CSSColors) => (
		<div style={{ display: "flex", alignItems: "center", marginRight: "8px" }}>
			{Object.values(colors).map((color, index) => (
				<div
					key={index}
					style={{
						backgroundColor: color,
						width: "10px",
						height: "10px",
						borderRadius: "50%",
						marginRight: index < 2 ? "3px" : "0",
					}}
				/>
			))}
		</div>
	);

	const getDropdownItemStyle = (itemKey: string, isActive: boolean): React.CSSProperties => {
		const baseStyle: React.CSSProperties = {
			display: "flex",
			alignItems: "center",
			padding: "8px 12px",
			borderRadius: "6px",
			cursor: "pointer",
			transition: "background-color 0.2s ease",
			backgroundColor: "transparent",
		};

		if (isActive) {
			return {
				...baseStyle,
				backgroundColor: "var(--bs-primary, #0d6efd)",
				color: "white",
			};
		}

		if (hoveredItem === itemKey) {
			return {
				...baseStyle,
				backgroundColor: "#dcdcdc",
			};
		}

		return baseStyle;
	};

	// Render navigation items helper function
	const renderNavigationItems = (items: NavigationItem[]) => {
		return items.map((item, index) => {
			// Handle submenu items
			if (item.submenu) {
				const isSubmenuItemActive = isSubmenuActive(item.submenu);
				const isExpanded = expandedSubmenu === item.text;
				const showSubmenu = shouldShowSubmenu(item);

				return (
					<div key={`submenu-${item.text}-${index}`}>
						<div
							className={`nav-item ${isSubmenuItemActive ? "active" : ""}`}
							onClick={() => isHovering && handleSubmenuToggle(item.text)}
							title={!isHovering ? item.text : ""}
							style={{ cursor: isHovering ? "pointer" : "default" }}
						>
							<span className="nav-icon">
								<i className={`bi ${item?.icon || getTableIcon(item.text)}`}></i>
							</span>
							{isHovering && (
								<>
									<span className="nav-text">{item.text}</span>
									<span className={`submenu-arrow ms-auto ${isExpanded ? "expanded" : ""}`}>
										<i className="bi bi-chevron-right"></i>
									</span>
								</>
							)}
						</div>

						<div
							className={`submenu ${!isHovering ? "collapsed-submenu" : ""} ${showSubmenu ? "open" : ""}`}
						>
							{item.submenu.map((subItem, subIndex) => (
								<Link
									key={subItem.path}
									to={subItem.path}
									className={`nav-item submenu-item ${isActive(subItem.path) ? "active" : ""}`}
									title={!isHovering ? subItem.text : subItem.text}
									style={{
										transitionDelay: showSubmenu
											? `${subIndex * 0.05 + 0.1}s`
											: //@ts-ignore
												`${(item.submenu.length - subIndex - 1) * 0.03}s`,
									}}
								>
									<span className="nav-icon">
										<i className={`bi ${subItem?.icon || getTableIcon(subItem.text)}`}></i>
									</span>
									{isHovering && <span className="nav-text">{subItem.text}</span>}
								</Link>
							))}
						</div>
					</div>
				);
			}

			// Handle regular nav items
			return (
				<Link
					key={item.path || `nav-${item.text}-${index}`}
					to={item.path!}
					className={`nav-item ${isActive(item.path!) ? "active" : ""}`}
					title={!isHovering ? item.text : ""}
				>
					<span className="nav-icon">
						<i className={`bi ${item?.icon || getTableIcon(item.text)}`}></i>
					</span>
					{isHovering && <span className="nav-text">{item.text}</span>}
				</Link>
			);
		});
	};

	return (
		<div
			className={`custom-sidebar collapsed ${isHovering ? "hovering" : ""}`}
			onMouseEnter={handleMouseEnter}
			onMouseLeave={handleMouseLeave}
		>
			<div className="sidebar-header border-bottom" style={{ paddingBottom: 0, paddingTop: 0, height: "100px" }}>
				<div className="position-relative" ref={dropdownRef}>
					<div className="sidebar-brand" onClick={handleLogoClick} style={{ cursor: "pointer" }}>
						<div className="logo-container d-flex align-items-center">
							<JamLogo style={{ height: "57px", width: "auto" }} />
							{isHovering && <span className="logo-text">JAM</span>}
						</div>
					</div>

					{showDropdown && isHovering && (
						<div className="theme-dropdown">
							<div className="fw-medium text-muted small mb-2 px-2">Themes</div>
							{THEMES.map((theme) => {
								const previewColors = getThemeColors(theme.key);
								const isCurrentTheme = currentTheme === theme.key;
								return (
									<div
										key={theme.key}
										style={getDropdownItemStyle(theme.key, isCurrentTheme)}
										onClick={() => handleThemeChange(theme.key)}
										onMouseEnter={() => setHoveredItem(theme.key)}
										onMouseLeave={() => setHoveredItem(null)}
									>
										{renderColorPreview(previewColors)}
										<div>
											<div className="fw-medium">{theme.name}</div>
										</div>
									</div>
								);
							})}
						</div>
					)}
				</div>
			</div>

			{/* Top Navigation Items */}
			<nav className="sidebar-nav sidebar-nav-top">{renderNavigationItems(topNavigationItems)}</nav>

			{/* Bottom Navigation Items */}
			<nav className="sidebar-nav sidebar-nav-bottom">{renderNavigationItems(bottomNavigationItems)}</nav>

			<div className="sidebar-footer border-top">
				<div
					onClick={handleLogout}
					className="nav-item logout-item text-danger d-flex align-items-center"
					style={{ cursor: "pointer" }}
					title={!isHovering ? "Logout" : ""}
				>
					<i className="bi bi-box-arrow-right logout-icon"></i>
					{isHovering && <span className="nav-text ms-2">Logout</span>}
				</div>
			</div>
		</div>
	);
};
