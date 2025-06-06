import React from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import ThemeToggle from "./ui/ThemeToggle";
import logo from "../assets/jam-jam.png";

const Header = ({ onLogout }) => {
	const navigate = useNavigate();

	const handleLogoClick = () => {
		navigate("/dashboard");
	};

	return (
		<Navbar bg="light" style={{ height: "80px" }}>
			<Container>
				<div style={{ display: "flex", alignItems: "center" }}>
					<Navbar.Brand onClick={handleLogoClick} className="header-logo">
						<div className="logo-container logo-container-horizontal">
							<img src={logo} alt="Logo" className="logo-image" style={{ height: "60px" }} />
							<span className="logo-text logo-text-right text-gradient-primary">JAM</span>
						</div>
					</Navbar.Brand>
					<ThemeToggle />
				</div>

				<Nav className="ms-auto d-flex align-items-center">
					<Nav.Link href="/dashboard">Dashboard</Nav.Link>
					<Nav.Link href="/locations">Locations</Nav.Link>
					<Nav.Link onClick={onLogout}>Logout</Nav.Link>
				</Nav>
			</Container>
		</Navbar>
	);
};

export default Header;
