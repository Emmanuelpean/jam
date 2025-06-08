import React from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import ThemeToggle from "./ui/ThemeToggle";
import { ReactComponent as JamLogo } from "../assets/Logo.svg";

const Header = ({ user, onLogout }) => {
	const navigate = useNavigate();

	const handleLogoClick = () => {
		navigate("/dashboard");
	};

	return (
		<Navbar bg="light" style={{ height: "100px" }}>
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
					<Nav.Link href="/dashboard">Dashboard</Nav.Link>
					<Nav.Link href="/jobs">Jobs</Nav.Link>
					<Nav.Link href="/persons">People</Nav.Link>
					<Nav.Link href="/companies">Companies</Nav.Link>
					<Nav.Link href="/keywords">Keywords</Nav.Link>
					<Nav.Link href="/locations">Locations</Nav.Link>
					<Nav.Link onClick={onLogout}>Logout</Nav.Link>
				</Nav>
			</Container>
		</Navbar>
	);
};

export default Header;
