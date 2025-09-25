import React, { useState } from "react";
import { ReactComponent as JamLogo } from "../assets/Logo.svg";
import packageJson from "../../package.json";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import Button from "react-bootstrap/Button";
import Collapse from "react-bootstrap/Collapse";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.css";

const AboutPage = () => {
	const [expandedAccordion, setExpandedAccordion] = useState(null);

	const releaseNotes = {
		"1.0.0":
			"Initial release of Jam, the Job Application Manager. Features include job application tracking, interview scheduling, company and contact management, and application status monitoring.",
	};

	const features = [
		{
			icon: "💼",
			title: "Job Application Records",
			description: "Create and manage comprehensive job application records",
		},
		{
			icon: "📅",
			title: "Interview Scheduling",
			description: "Track interview schedules and outcomes efficiently",
		},
		{
			icon: "🏢",
			title: "Company Management",
			description: "Store detailed company and contact information",
		},
		{
			icon: "📈",
			title: "Progress Monitoring",
			description: "Monitor application status, progress, and deadlines",
		},
	];

	const toggleAccordion = (index: any) => {
		setExpandedAccordion(expandedAccordion === index ? null : index);
	};

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
						<Col lg={8} className="text-center mb-5">
							<h2 className="display-5 fw-bold text-dark">What Jam Can Do For You</h2>
						</Col>
					</Row>
					<Row className="g-4 mb-5">
						{features.map((feature, index) => (
							<Col md={6} key={index}>
								<div className="feature-card p-4 h-100">
									<div className="d-flex align-items-start align-items-center">
										<div className="feature-icon me-3">{feature.icon}</div>
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
							<Card className="glass-card border-0 p-4">
								<Card.Body>
									<h2 className="display-6 fw-bold text-dark mb-4 text-center">Release Notes</h2>
									<div className="accordion-custom">
										{Object.entries(releaseNotes).map(([version, note], index) => (
											<div
												key={version}
												className="border border-light rounded-3 overflow-hidden bg-white shadow-sm mb-3"
											>
												<Button
													variant="link"
													onClick={() => toggleAccordion(index)}
													className={`accordion-button-custom w-100 text-start p-3 text-decoration-none ${expandedAccordion === index ? "active" : ""}`}
													aria-expanded={expandedAccordion === index}
												>
													<div className="d-flex justify-content-between align-items-center w-100">
														<span className="fs-5 fw-semibold">Version {version}</span>
														<svg
															className={`transition ${expandedAccordion === index ? "rotate-180" : ""}`}
															width="20"
															height="20"
															fill="currentColor"
															viewBox="0 0 16 16"
															style={{
																transform:
																	expandedAccordion === index
																		? "rotate(180deg)"
																		: "rotate(0deg)",
																transition: "transform 0.2s ease",
															}}
														>
															<path
																fillRule="evenodd"
																d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
															/>
														</svg>
													</div>
												</Button>
												<Collapse in={expandedAccordion === index}>
													<div className="accordion-body-custom p-3">{note}</div>
												</Collapse>
											</div>
										))}
									</div>
								</Card.Body>
							</Card>
						</Col>
					</Row>
				</Container>

				{/* Footer Decoration */}
				<div
					style={{
						height: "80px",
						background:
							"linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%)",
					}}
				></div>
			</div>
		</>
	);
};

export default AboutPage;
