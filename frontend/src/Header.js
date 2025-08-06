import React from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import { useNavigate, useLocation } from "react-router-dom";
import ThemeToggle from "./components/theme/ThemeToggle";
import { ReactComponent as JamLogo } from "./assets/Logo.svg";

const Header = ({ onLogout }) => {
	const navigate = useNavigate();
	const location = useLocation();

	const handleLogoClick = () => {
		navigate("/dashboard");
	};

	const isActive = (path) => location.pathname === path;

	return (
		<Navbar bg="light" style={{ height: "100px", borderRadius: "0" }}>
			<Container>
				<div style={{ display: "flex", alignItems: "center" }}>
					<Navbar.Brand onClick={handleLogoClick} className="header-logo">
						<div className="logo-container logo-container-horizontal">
							<JamLogo style={{ height: "80px", width: "auto" }} className="logo-image" />
						</div>
					</Navbar.Brand>
					<ThemeToggle />
				</div>

				<Nav className="ms-auto d-flex align-items-center">
					<Nav.Link href="/dashboard" className={`nav-link-custom ${isActive("/dashboard") ? "active" : ""}`}>
						<i className="bi bi-house-door me-2"></i>
						<span>Dashboard</span>
					</Nav.Link>
					<Nav.Link href="/jobs" className={`nav-link-custom ${isActive("/jobs") ? "active" : ""}`}>
						<i className="bi bi-briefcase me-2"></i>
						<span>Jobs</span>
					</Nav.Link>
					<Nav.Link
						href="/jobapplications"
						className={`nav-link-custom ${isActive("/jobapplications") ? "active" : ""}`}
					>
						<i className="bi bi-person-workspace me-2"></i>
						<span>Job Applications</span>
					</Nav.Link>
					<Nav.Link
						href="/interviews"
						className={`nav-link-custom ${isActive("/interviews") ? "active" : ""}`}
					>
						<i className="bi bi-people-fill me-2"></i>
						<span>Interviews</span>
					</Nav.Link>
					<Nav.Link href="/persons" className={`nav-link-custom ${isActive("/persons") ? "active" : ""}`}>
						<i className="bi bi-people me-2"></i>
						<span>People</span>
					</Nav.Link>
					<Nav.Link href="/locations" className={`nav-link-custom ${isActive("/locations") ? "active" : ""}`}>
						<i className="bi bi-geo-alt me-2"></i>
						<span>Locations</span>
					</Nav.Link>
					<Nav.Link href="/companies" className={`nav-link-custom ${isActive("/companies") ? "active" : ""}`}>
						<i className="bi bi-building me-2"></i>
						<span>Companies</span>
					</Nav.Link>
					<Nav.Link
						href="/aggregators"
						className={`nav-link-custom ${isActive("/aggregators") ? "active" : ""}`}
					>
						<i className="bi bi-linkedin me-2"></i>
						<span>Aggregators</span>
					</Nav.Link>
					<Nav.Link href="/keywords" className={`nav-link-custom ${isActive("/keywords") ? "active" : ""}`}>
						<i className="bi bi-tags me-2"></i>
						<span>Tags</span>
					</Nav.Link>
					<Nav.Link onClick={onLogout} className="nav-link-custom text-danger">
						<i className="bi bi-box-arrow-right me-2"></i>
						<span>Logout</span>
					</Nav.Link>
				</Nav>
			</Container>
		</Navbar>
	);
};

export default Header;
