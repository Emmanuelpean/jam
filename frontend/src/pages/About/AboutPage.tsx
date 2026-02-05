import React, { JSX, useState } from "react";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import packageJson from "../../../package.json";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.scss";
import v100 from "../../releaseNotes/V1_0_0";
import v110 from "../../releaseNotes/V1_1_0";
import v120 from "../../releaseNotes/V1_2_0";
import { useWhatsNew } from "../../contexts/WhatsNewContext";

interface Feature {
	icon: string;
	title: string;
	description: string;
}

interface ReleaseNoteAccordionProps {
	version: string;
	content: any;
	isOpen: boolean;
	onToggle: () => void;
}

const ReleaseNoteAccordion = ({ version, content, isOpen, onToggle }: ReleaseNoteAccordionProps): JSX.Element => {
	const contentRef = React.useRef<HTMLDivElement>(null);

	return (
		<div className="simple-accordion mb-2" style={{ paddingLeft: "10px", paddingRight: "10px" }}>
			<div
				className="simple-accordion-header d-flex align-items-center justify-content-between py-2 border-bottom"
				onClick={onToggle}
				style={{ cursor: "pointer" }}
			>
				<div className="d-flex align-items-center">
					<span className="fw-medium">V{version}</span>
				</div>
				<i className={`bi ${isOpen ? "bi-chevron-up" : "bi-chevron-down"} text-muted`}></i>
			</div>
			<div
				ref={contentRef}
				style={{
					maxHeight: isOpen ? `${contentRef.current?.scrollHeight}px` : "0",
					overflow: "hidden",
					transition: "max-height 0.3s ease-in-out",
				}}
			>
				<div className="simple-accordion-content" style={{ margin: "10px" }}>
					<div className="release-notes-content" dangerouslySetInnerHTML={{ __html: content }} />
				</div>
			</div>
		</div>
	);
};
const AboutPage = (): JSX.Element => {
	const [openVersion, setOpenVersion] = useState<string | null>(null);
	const [acknowledgementsOpen, setAcknowledgementsOpen] = useState<boolean>(false);
	const { showWhatsNew } = useWhatsNew();
	const releaseNotes: Record<string, any> = {
		"1.2": v120,
		"1.1": v110,
		"1.0": v100,
	};
	const versions: string[] = Object.keys(releaseNotes);

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
			icon: "bi-inbox",
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
									<h2 className="display-5 fw-bold mb-4">Streamline Your Job Search Journey</h2>
									<p className="fs-5 about-text-muted mb-4" style={{ lineHeight: "1.625" }}>
										Job searching is overwhelming. Between tracking applications, following up with
										contacts, and preparing for interviews, it's easy to lose sight of opportunities
										that could change your career.{" "}
										<strong style={{ color: "var(--primary-mid)" }}>Jam</strong> brings everything
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

					{/* Release Notes Section */}
					<Row className="justify-content-center mb-2">
						<Col lg={8} className="text-center mb-2">
							<h2 className="display-5 fw-bold">Release Notes</h2>
							<button
								onClick={showWhatsNew}
								className="glass-badge mt-3"
								style={{
									cursor: "pointer",
									border: "none",
									transition: "transform 0.2s ease",
								}}
								onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
								onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
							>
								<i className="bi bi-stars me-2" style={{ color: "var(--primary-mid)" }} />
								View What's New in {packageJson.version}
							</button>
						</Col>
					</Row>
					<Row className="justify-content-center">
						<Col lg={10}>
							<div style={{ width: "100%", marginTop: "10px" }}>
								{versions.map(
									(version: string): JSX.Element => (
										<ReleaseNoteAccordion
											key={version}
											version={version}
											content={releaseNotes[version]}
											isOpen={openVersion === version}
											onToggle={() => setOpenVersion(openVersion === version ? null : version)}
										/>
									)
								)}
							</div>
						</Col>
					</Row>

					{/* Acknowledgements Section */}
					<Row className="justify-content-center mt-5 mb-2">
						<Col lg={8} className="text-center mb-2">
							<h2 className="display-5 fw-bold">Acknowledgements</h2>
						</Col>
					</Row>
					<Row className="justify-content-center">
						<Col lg={10}>
							<div
								className="simple-accordion mb-2"
								style={{ paddingLeft: "10px", paddingRight: "10px" }}
							>
								<div
									className="simple-accordion-header d-flex align-items-center justify-content-between py-2 border-bottom"
									onClick={() => setAcknowledgementsOpen(!acknowledgementsOpen)}
									style={{ cursor: "pointer" }}
								>
									<div className="d-flex align-items-center">
										<span className="fw-medium">
											Open-source projects and services that make Jam possible
										</span>
									</div>
									<i
										className={`bi ${acknowledgementsOpen ? "bi-chevron-up" : "bi-chevron-down"} text-muted`}
									></i>
								</div>
								<div
									style={{
										maxHeight: acknowledgementsOpen ? "1000px" : "0",
										overflow: "hidden",
										transition: "max-height 0.3s ease-in-out",
									}}
								>
									<div className="simple-accordion-content" style={{ margin: "10px" }}>
										{[
											{
												title: "Frontend",
												packages: [
													{ name: "React", url: "https://react.dev" },
													{ name: "Bootstrap", url: "https://getbootstrap.com" },
													{ name: "Bootstrap Icons", url: "https://icons.getbootstrap.com" },
													{ name: "React Bootstrap", url: "https://react-bootstrap.github.io" },
													{ name: "Recharts", url: "https://recharts.org" },
													{ name: "Leaflet", url: "https://leafletjs.com" },
													{ name: "React Router", url: "https://reactrouter.com" },
													{ name: "React Select", url: "https://react-select.com" },
													{ name: "Lodash", url: "https://lodash.com" },
												],
											},
											{
												title: "Backend",
												packages: [
													{ name: "FastAPI", url: "https://fastapi.tiangolo.com" },
													{ name: "SQLAlchemy", url: "https://www.sqlalchemy.org" },
													{ name: "Pydantic", url: "https://docs.pydantic.dev" },
													{ name: "Beautiful Soup", url: "https://www.crummy.com/software/BeautifulSoup" },
													{ name: "Gunicorn", url: "https://gunicorn.org" },
													{ name: "PostgreSQL", url: "https://www.postgresql.org" },
												],
											},
											{
												title: "Services",
												packages: [
													{ name: "OpenAI", url: "https://openai.com" },
													{ name: "Stripe", url: "https://stripe.com" },
													{ name: "Apify", url: "https://apify.com" },
													{ name: "Scrapfly", url: "https://scrapfly.io" },
												],
											},
										].map((section) => (
											<div key={section.title} className="mb-4">
												<h5
													className="fw-bold mb-3"
													style={{ color: "var(--primary-mid)" }}
												>
													{section.title}
												</h5>
												<div className="d-flex flex-wrap gap-2">
													{section.packages.map((pkg) => (
														<a
															key={pkg.name}
															href={pkg.url}
															target="_blank"
															rel="noopener noreferrer"
															className="glass-badge text-decoration-none"
															style={{
																fontSize: "0.875rem",
																padding: "0.5rem 1rem",
															}}
														>
															{pkg.name}
														</a>
													))}
												</div>
											</div>
										))}
									</div>
								</div>
							</div>
						</Col>
					</Row>
				</Container>
			</div>
		</>
	);
};

export default AboutPage;
