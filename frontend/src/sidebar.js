import React, { useEffect, useMemo, useRef, useState } from "react";
import { CNavItem, CSidebar, CSidebarBrand, CSidebarHeader, CSidebarNav, CSidebarToggler } from "@coreui/react";
import { useLocation } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { ReactComponent as JamLogo } from "./assets/Logo.svg";
import { authApi } from "./services/api";

export const SidebarExample = () => {
	const location = useLocation();
	const { logout, token } = useAuth();
	const [showDropdown, setShowDropdown] = useState(false);
	const [currentTheme, setCurrentTheme] = useState("mixed-berry");
	const [hoveredItem, setHoveredItem] = useState(null);
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

	useEffect(() => {
		import("@coreui/coreui/dist/css/coreui.min.css");

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
		<div className="sidebar-container">
			<CSidebar className="border-end" unfoldable>
				<CSidebarHeader className="border-bottom">
					<div className="position-relative" ref={dropdownRef}>
						<CSidebarBrand onClick={handleLogoClick} style={{ cursor: "pointer" }}>
							<div className="logo-container logo-container-horizontal d-flex align-items-center">
								<JamLogo style={{ height: "57px", width: "auto" }} />
								<span className="logo-text logo-text-right sidebar-brand-full">JAM</span>
							</div>
						</CSidebarBrand>

						{showDropdown && (
							<div
								className="position-absolute bg-white border rounded shadow-lg p-2"
								style={{
									top: "100%",
									left: "0",
									zIndex: 1000,
									minWidth: "200px",
									marginTop: "5px",
								}}
							>
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
				</CSidebarHeader>
				<CSidebarNav>
					<CNavItem href="/dashboard" className={isActive("/dashboard") ? "active" : ""}>
						<span className="nav-icon" style={{ width: "30px !important" }}>
							<i className="bi bi-house-door"></i>
						</span>
						<span className="nav-text">Dashboard</span>
					</CNavItem>

					<CNavItem href="/jobs" className={isActive("/jobs") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-briefcase"></i>
						</span>
						<span className="nav-text">Jobs</span>
					</CNavItem>

					<CNavItem href="/jobapplications" className={isActive("/jobapplications") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-person-workspace"></i>
						</span>
						<span className="nav-text">Job Applications</span>
					</CNavItem>

					<CNavItem href="/interviews" className={isActive("/interviews") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-people-fill"></i>
						</span>
						<span className="nav-text">Interviews</span>
					</CNavItem>

					<CNavItem href="/persons" className={isActive("/persons") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-people"></i>
						</span>
						<span className="nav-text">People</span>
					</CNavItem>

					<CNavItem href="/locations" className={isActive("/locations") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-geo-alt"></i>
						</span>
						<span className="nav-text">Locations</span>
					</CNavItem>

					<CNavItem href="/companies" className={isActive("/companies") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-building"></i>
						</span>
						<span className="nav-text">Companies</span>
					</CNavItem>

					<CNavItem href="/aggregators" className={isActive("/aggregators") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-linkedin"></i>
						</span>
						<span className="nav-text">Aggregators</span>
					</CNavItem>

					<CNavItem href="/keywords" className={isActive("/keywords") ? "active" : ""}>
						<span className="nav-icon">
							<i className="bi bi-tags"></i>
						</span>
						<span className="nav-text">Tags</span>
					</CNavItem>
				</CSidebarNav>

				<CSidebarHeader className="border-top">
					<div
						onClick={handleLogout}
						className="text-danger d-flex align-items-center"
						style={{ cursor: "pointer" }}
					>
						<i className="bi bi-box-arrow-right me-2"></i>
						<span className="nav-text sidebar-brand-full">Logout</span>
					</div>
				</CSidebarHeader>
			</CSidebar>
		</div>
	);
};
