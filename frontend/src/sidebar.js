import React, { useEffect } from "react";
import { CBadge, CSidebar, CSidebarBrand, CSidebarHeader, CSidebarNav, CSidebarToggler, CNavItem } from "@coreui/react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { ReactComponent as JamLogo } from "./assets/Logo.svg";
import ThemeToggle from "./components/theme/ThemeToggle";

export const SidebarExample = () => {
	const navigate = useNavigate();
	const location = useLocation();
	const { logout } = useAuth();

	useEffect(() => {
		// Dynamically import CoreUI CSS
		import("@coreui/coreui/dist/css/coreui.min.css");
	}, []);

	const handleLogoClick = () => {
		navigate("/dashboard");
	};

	const isActive = (path) => location.pathname === path;

	const handleLogout = () => {
		logout();
	};

	return (
		<div className="sidebar-container">
			<CSidebar className="border-end" unfoldable>
				<CSidebarHeader className="border-bottom">
					<CSidebarBrand onClick={handleLogoClick} style={{ cursor: "pointer" }}>
						<div className="logo-container d-flex align-items-center">
							<JamLogo style={{ height: "40px", width: "auto" }} className="logo-image" />
						</div>
					</CSidebarBrand>
				</CSidebarHeader>
				<CSidebarNav>
					<CNavItem href="/dashboard" className={isActive("/dashboard") ? "active" : ""}>
						<span className="nav-icon">
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
					<div className="d-flex justify-content-between align-items-center w-100 px-3">
						<ThemeToggle />
						<div onClick={handleLogout} className="text-danger" style={{ cursor: "pointer" }}>
							<i className="bi bi-box-arrow-right me-2"></i>
							Logout
						</div>
					</div>
					<CSidebarToggler />
				</CSidebarHeader>
			</CSidebar>
		</div>
	);
};
