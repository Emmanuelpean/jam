import React, { JSX, useState } from "react";
import JamLogo from "../../assets/Logo.svg?react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.scss";
import packageJson from "../../../package.json";
import { useWhatsNew } from "../../contexts/WhatsNewContext";
import { useTour } from "../../contexts/TourContext";
import { useAuth } from "../../contexts/AuthContext";
import { TourDefinition, TOURS } from "../../components/GuidedTour/tourSteps";
import AppFeaturesList, { Feature } from "./AppFeaturesList";
import { releaseNotes as releaseNotesRegistry, version, VERSIONS } from "../../releaseNotes/versions";
import { Accordion } from "../../components/Accordion/Accordion";
import { useViewport } from "../../contexts/ViewportContext";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";

const AboutPage = (): JSX.Element => {
	const { showWelcome } = useWhatsNew();
	const { toggleTourSelect, completedTourIds } = useTour();
	const { currentUser } = useAuth();
	const { isMobile } = useViewport();
	const [openVersion, setOpenVersion] = useState<string | null>(null);
	const isPremium = currentUser?.premium.is_active ?? false;
	const implementedTours: TourDefinition[] = TOURS.filter(
		(t: TourDefinition): boolean => isPremium || !["import-scraped-job", "scraping-filters"].includes(t.id)
	);
	const allToursCompleted: boolean =
		implementedTours.length > 0 &&
		implementedTours.every((t: TourDefinition): boolean => completedTourIds.has(t.id));
	const tourPanelDismissed: boolean = currentUser?.preferences.tour_panel_dismissed ?? false;

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
			description: "Automatically rate job alerts based on your preferences to prioritise applications",
		},
		{
			icon: "bi-envelope-arrow-up",
			title: "Follow-Up Email Generator",
			description: "Automatically generate personalised follow-up email drafts for your applications",
		},
	];

	return (
		<div style={{ flex: 1 }}>
			{isMobile && <PageHeader title="About JAM" icon={getTableIcon("About JAM")} />}
			<div className="about-container d-flex flex-column align-items-center justify-content-center">
				{/* Hero Section */}
				<div className="hero-overlay">
					<Container className="py-5">
						<Row className="justify-content-center text-center py-5">
							<Col lg={8}>
								<div className="auth-logo">
									<div className="logo-container logo-container-vertical">
										<JamLogo style={{ height: "158px" }} />
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
							<h2 className="display-5 fw-bold mb-4" style={{ textAlign: "center" }}>
								Streamline Your Job Search Journey
							</h2>
							<p
								className="fs-5 about-text-muted mb-4"
								style={{ lineHeight: "1.625", textAlign: "center" }}
							>
								Job searching is overwhelming. Between tracking applications, following up with
								contacts, and preparing for interviews, it's easy to lose sight of opportunities that
								could change your career. <strong style={{ color: "var(--primary-mid)" }}>JAM</strong>{" "}
								brings everything together in one place - applications, interviews, contacts, and notes
								- so you can stay organised and focused on landing your dream job.
							</p>
						</Col>
					</Row>

					{/* Features Section */}
					<Row className="justify-content-center mb-5">
						<Col lg={8} className="text-center mb-2">
							<h2 className="display-5 fw-bold">What JAM Can Do For You</h2>
						</Col>
						<div className="d-flex justify-content-center gap-2 mt-3">
							<Button variant="outline-primary" onClick={showWelcome}>
								<i className="bi bi-stars me-2" />
								Discover JAM
							</Button>
							{(allToursCompleted || tourPanelDismissed) && (
								<Button id="take-a-tour-btn" variant="outline-secondary" onClick={toggleTourSelect}>
									<i className="bi bi-map me-2" />
									Take a Tour
								</Button>
							)}
						</div>
					</Row>
					<AppFeaturesList features={features} className="mb-5" />

					{/* Release Notes Section */}
					<Row className="justify-content-center mt-5 mb-2">
						<Col lg={8} className="text-center mb-2">
							<h2 className="display-5 fw-bold">Release Notes</h2>
						</Col>
					</Row>
					<Row className="justify-content-center">
						<Col lg={10}>
							<div style={{ width: "100%", marginTop: "9px" }}>
								{[...VERSIONS].reverse().map(
									(v: version): JSX.Element => (
										<Accordion
											key={v}
											className="mb-2"
											isOpen={openVersion === v}
											onToggle={() => setOpenVersion(openVersion === v ? null : v)}
											header={<span className="fw-medium">V{v}</span>}
										>
											<div style={{ margin: "9px" }}>
												<div
													className="release-notes-content"
													dangerouslySetInnerHTML={{
														__html: releaseNotesRegistry[v] as string,
													}}
												/>
											</div>
										</Accordion>
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
							<Accordion
								className="mb-2"
								header={
									<span className="fw-medium">
										Open-source projects and services that make Jam possible
									</span>
								}
							>
								<div style={{ margin: "9px" }}>
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
												{
													name: "Beautiful Soup",
													url: "https://www.crummy.com/software/BeautifulSoup",
												},
												{ name: "Gunicorn", url: "https://gunicorn.org" },
												{ name: "PostgreSQL", url: "https://www.postgresql.org" },
											],
										},
										{
											title: "Services",
											packages: [
												{ name: "Anthropic", url: "https://www.anthropic.com/" },
												{ name: "Stripe", url: "https://stripe.com" },
												{ name: "Apify", url: "https://apify.com" },
												{ name: "BrightData", url: "https://brightdata.com" },
											],
										},
									].map((section) => (
										<div key={section.title} className="mb-4">
											<h5 className="fw-bold mb-3" style={{ color: "var(--primary-mid)" }}>
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
														style={{ fontSize: "0.875rem", padding: "0.5rem 1rem" }}
													>
														{pkg.name}
													</a>
												))}
											</div>
										</div>
									))}
								</div>
							</Accordion>
						</Col>
					</Row>
				</Container>
			</div>
		</div>
	);
};

export default AboutPage;
