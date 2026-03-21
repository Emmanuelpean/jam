import React, { JSX } from "react";
import JamLogo from "../../assets/Logo.svg?react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.scss";
import packageJson from "../../../package.json";
import { useWhatsNew } from "../../contexts/WhatsNewContext";

interface Feature {
	icon: string;
	title: string;
	description: string;
}

const AboutPage = (): JSX.Element => {
	const { showWelcome } = useWhatsNew();

	const features: Feature[] = [
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
			icon: "bi-bar-chart",
			title: "Progress Monitoring",
			description: "Monitor application status, progress, and deadlines",
		},
		{
			icon: "bi-inboxes",
			title: "Job Alert Scraping",
			description: "Automatically scrape job alerts from popular job board email alerts",
		},
		{
			icon: "bi-star-half",
			title: "Job Rating",
			description: "Automatically rate scraped jobs based on your preferences to prioritise applications",
		},
		{
			icon: "bi-envelope-arrow-up",
			title: "Follow-Up Email Generator",
			description: "Automatically generate personalised follow-up email drafts for your applications",
		},
	];

	return (
		<>
			<div className="gradient-bg" style={{ borderRadius: "18px", overflow: "hidden" }}>
				{/* Hero Section */}
				<div className="hero-overlay">
					<Container className="py-5">
						<Row className="justify-content-center text-center py-5">
							<Col lg={8}>
								<div className="auth-logo">
									<div className="logo-container logo-container-vertical">
										<JamLogo style={{ height: "157.5px", width: "auto" }} />
										<div
											className="logo-text-below text-gradient-primary"
											style={{ fontSize: "45px", fontWeight: "bold" }}
										>
											Job Application Manager
										</div>
									</div>
								</div>

								<div
									className="d-flex flex-column flex-sm-row align-items-center justify-content-center gap-3"
									style={{ fontSize: "15.3px" }}
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
									<h2 className="display-5 fw-bold mb-4">Streamline Your Job Search Journey</h2>
									<p className="fs-5 about-text-muted mb-4" style={{ lineHeight: "1.625" }}>
										Job searching is overwhelming. Between tracking applications, following up with
										contacts, and preparing for interviews, it's easy to lose sight of opportunities
										that could change your career.{" "}
										<strong style={{ color: "var(--primary-mid)" }}>JAM</strong> brings everything
										together in one place—applications - interviews, contacts, and notes - so you
										can stay organised and focused on landing your dream job.
									</p>
								</Card.Body>
							</Card>
						</Col>
					</Row>

					{/* Features Section */}
					<Row className="justify-content-center mb-5">
						<Col lg={8} className="text-center mb-2">
							<h2 className="display-5 fw-bold">What Jam Can Do For You</h2>
						</Col>
						<div className="d-flex justify-content-center gap-2 mt-3">
							<Button variant="outline-primary" onClick={showWelcome}>
								<i className="bi bi-stars me-2" />
								Discover JAM
							</Button>
						</div>
					</Row>
					<div className="features-grid mb-5">
						{features.map(
							(feature: Feature, index: number): JSX.Element => (
								<div className="feature-card p-4" key={index}>
									<div className="d-flex align-items-start align-items-center">
										<div className="feature-icon me-3">
											<i className={`bi ${feature.icon}`} style={{ fontSize: "2rem" }}></i>
										</div>
										<div>
											<h5 className="fw-bold mb-2">{feature.title}</h5>
											<p className="about-text-muted mb-0">{feature.description}</p>
										</div>
									</div>
								</div>
							)
						)}
					</div>
				</Container>
			</div>
		</>
	);
};

export default AboutPage;
