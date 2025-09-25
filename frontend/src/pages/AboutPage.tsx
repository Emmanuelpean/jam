import React from "react";
import { ReactComponent as JamLogo } from "../assets/Logo.svg";
import packageJson from "../../package.json";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.css";
import { Accordion } from "react-bootstrap";

const AboutPage = () => {
	const releaseNotes = {
		"1.0.0":
			"Initial release of Jam, the Job Application Manager. Features include job application tracking, interview scheduling, company and contact management, and application status monitoring.",
	};

	const features = [
		{
			icon: "bi-briefcase",
			title: "Job Application Records",
			description: "Create and manage comprehensive job application records",
		},
		{
			icon: "bi-calendar-check",
			title: "Interview Scheduling",
			description: "Track interview schedules and outcomes efficiently",
		},
		{
			icon: "bi-building",
			title: "Company Management",
			description: "Store detailed company and contact information",
		},
		{
			icon: "bi-bar-chart",
			title: "Progress Monitoring",
			description: "Monitor application status, progress, and deadlines",
		},
	];

	return (
		<>
			<div className="gradient-bg" style={{ borderRadius: "20px", overflow: "hidden" }}>
				{/* Hero Section */}
				<div className="hero-overlay">
					<Container className="py-5">
						<Row className="justify-content-center text-center py-5">
							<Col lg={8}>
								<div className="auth-logo">
									<div className="logo-container logo-container-vertical">
										<JamLogo style={{ height: "175px", width: "auto" }} />
										<div
											className="logo-text-below text-gradient-primary"
											style={{ fontSize: "50px", fontWeight: "bold" }}
										>
											Job Application Manager
										</div>
									</div>
								</div>

								<div
									className="d-flex flex-column flex-sm-row align-items-center justify-content-center gap-3"
									style={{ fontSize: "17px" }}
								>
									<div className="glass-badge">
										<span className="about-text-muted">Version</span>
										<a
											href="https://github.com/Emmanuelpean/jam"
											target="_blank"
											rel="noopener noreferrer"
											className="link-gradient ms-2 align-items-center"
										>
											{packageJson.version}
											<i className="bi bi-github ms-2"></i>
										</a>
									</div>
									<div className="glass-badge">
										<span className="about-text-muted">Created by</span>
										<a
											href="https://emmanuelpean.me/"
											target="_blank"
											rel="noopener noreferrer"
											className="link-gradient-purple ms-2  align-items-center"
										>
											Emmanuel V. Péan
											<i className="bi bi-person-raised-hand ms-1"></i>
										</a>
									</div>
								</div>
							</Col>
						</Row>
					</Container>
				</div>

				<Container className="py-5">
					{/* About Section */}
					<Row className="justify-content-center mb-5">
						<Col lg={10}>
							<Card className="glass-card border-0 p-4">
								<Card.Body className="text-center">
									<h2 className="display-5 fw-bold text-dark mb-4">
										Streamline Your Job Search Journey
									</h2>
									<p className="fs-5 text-muted mb-4" style={{ lineHeight: "1.625" }}>
										<strong className="text-primary">Jam</strong> is a user-friendly web app
										designed to help you manage your jobs, applications, interviews, and everything
										in-between. Job search can be a time-consuming and tedious process, requiring
										you to keep track of many jobs and applications at the same time.
									</p>
									<p className="fs-5 text-muted" style={{ lineHeight: "1.625" }}>
										<strong className="text-primary">Jam</strong> aims to make this process easier
										so that you can get the job of your dreams.
									</p>
								</Card.Body>
							</Card>
						</Col>
					</Row>

					{/* Features Section */}
					<Row className="justify-content-center mb-5">
						<Col lg={8} className="text-center mb-2">
							<h2 className="display-5 fw-bold text-dark">What Jam Can Do For You</h2>
						</Col>
					</Row>
					<Row className="g-4 mb-5">
						{features.map((feature, index) => (
							<Col md={6} key={index}>
								<div className="feature-card p-4 h-100">
									<div className="d-flex align-items-start align-items-center">
										<div className="feature-icon me-3">
											<i className={`bi ${feature.icon}`} style={{ fontSize: "2rem" }}></i>
										</div>
										<div>
											<h5 className="fw-bold text-dark mb-2">{feature.title}</h5>
											<p className="about-text-muted mb-0">{feature.description}</p>
										</div>
									</div>
								</div>
							</Col>
						))}
					</Row>

					{/* Release Notes Section */}
					<Row className="justify-content-center">
						<Col lg={10}>
							<div style={{ width: "100%", maxWidth: 1200, marginTop: "10px" }}>
								<h4>Release Notes</h4>
								<Accordion>
									{Object.entries(releaseNotes).map(([version, note], idx) => (
										<Accordion.Item eventKey={String(idx)} key={version}>
											<Accordion.Header>V{version}</Accordion.Header>
											<Accordion.Body style={{ margin: "3px" }}>{note}</Accordion.Body>
										</Accordion.Item>
									))}
								</Accordion>
							</div>
						</Col>
					</Row>
				</Container>
			</div>
		</>
	);
};

export default AboutPage;
