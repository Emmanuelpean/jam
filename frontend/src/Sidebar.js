import React, { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { ReactComponent as JamLogo } from "./assets/Logo.svg";
import { authApi } from "./services/api";
import "./Sidebar.css";

export const Sidebar = ({ onHoverChange }) => {
	const location = useLocation();
	const { logout, token } = useAuth();
	const [showDropdown, setShowDropdown] = useState(false);
	const [currentTheme, setCurrentTheme] = useState("mixed-berry");
	const [hoveredItem, setHoveredItem] = useState(null);
	const [isHovering, setIsHovering] = useState(false);
	const dropdownRef = useRef(null);

	const themes = useMemo(
		() => [
			{ key: "strawberry", name: "Strawberry" },
			{ key: "blueberry", name: "Blueberry" },
			{ key: "raspberry", name: "Raspberry" },
			{ key: "mixed-berry", name: "Mixed Berry" },
			{ key: "forest-berry", name: "Forest Berry" },
			{ key: "blackberry", name: "Blackberry" },
		],
		[],
	);

	const navigationItems = [
		{ path: "/dashboard", icon: "bi-house-door", text: "Dashboard" },
		{ path: "/jobs", icon: "bi-briefcase", text: "Jobs" },
		{ path: "/jobapplications", icon: "bi-person-workspace", text: "Job Applications" },
		{ path: "/interviews", icon: "bi-people-fill", text: "Interviews" },
		{ path: "/persons", icon: "bi-people", text: "People" },
		{ path: "/locations", icon: "bi-geo-alt", text: "Locations" },
		{ path: "/companies", icon: "bi-building", text: "Companies" },
		{ path: "/aggregators", icon: "bi-linkedin", text: "Aggregators" },
		{ path: "/keywords", icon: "bi-tags", text: "Tags" },
	];

	useEffect(() => {
		// Initialize theme
		const savedTheme = localStorage.getItem("theme");
		const initTheme = savedTheme && themes.some((theme) => theme.key === savedTheme) ? savedTheme : "mixed-berry";
		setCurrentTheme(initTheme);
		document.documentElement.setAttribute("data-theme", initTheme);
	}, [themes]);

	// Close dropdown when clicking outside
	useEffect(() => {
		const handleClickOutside = (event) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
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

	const handleLogoClick = (e) => {
		e.preventDefault();
		e.stopPropagation();
		setShowDropdown(!showDropdown);
	};

	const handleThemeChange = async (themeKey) => {
		setCurrentTheme(themeKey);
		document.documentElement.setAttribute("data-theme", themeKey);
		localStorage.setItem("theme", themeKey);

		if (token) {
			try {
				await authApi.updateUserTheme(themeKey, token);
			} catch (error) {
				console.error("Error saving theme:", error);
			}
		}
		setShowDropdown(false);
	};

	const handleMouseEnter = () => {
		setIsHovering(true);
	};

	const handleMouseLeave = () => {
		setIsHovering(false);
		setShowDropdown(false);
	};

	const isActive = (path) => location.pathname === path;

	const handleLogout = () => {
		logout();
	};

	const getCurrentCSSColors = () => {
		const computedStyle = getComputedStyle(document.documentElement);
		return {
			start: computedStyle.getPropertyValue("--primary-start").trim(),
			mid: computedStyle.getPropertyValue("--primary-mid").trim(),
			end: computedStyle.getPropertyValue("--primary-end").trim(),
		};
	};

	const getThemeColors = (themeKey) => {
		const originalTheme = document.documentElement.getAttribute("data-theme");
		document.documentElement.setAttribute("data-theme", themeKey);
		const colors = getCurrentCSSColors();
		if (originalTheme) {
			document.documentElement.setAttribute("data-theme", originalTheme);
		}
		return colors;
	};

	const renderColorPreview = (colors) => (
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

	const getDropdownItemStyle = (itemKey, isActive) => {
		const baseStyle = {
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

	return (
		<div
			className={`custom-sidebar collapsed ${isHovering ? "hovering" : ""}`}
			onMouseEnter={handleMouseEnter}
			onMouseLeave={handleMouseLeave}
		>
			<div className="sidebar-header border-bottom">
				<div className="position-relative" ref={dropdownRef}>
					<div className="sidebar-brand" onClick={handleLogoClick} style={{ cursor: "pointer" }}>
						<div className="logo-container logo-container-horizontal d-flex align-items-center">
							<JamLogo style={{ height: "57px", width: "auto" }} />
							{isHovering && <span className="logo-text logo-text-right">JAM</span>}
						</div>
					</div>

					{showDropdown && isHovering && (
						<div className="theme-dropdown">
							<div className="fw-medium text-muted small mb-2 px-2">Themes</div>
							{themes.map((theme) => {
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

			<nav className="sidebar-nav">
				{navigationItems.map((item) => (
					<Link
						key={item.path}
						to={item.path}
						className={`nav-item ${isActive(item.path) ? "active" : ""}`}
						title={!isHovering ? item.text : ""}
					>
						<span className="nav-icon">
							<i className={`bi ${item.icon}`}></i>
						</span>
						{isHovering && <span className="nav-text">{item.text}</span>}
					</Link>
				))}
			</nav>

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
