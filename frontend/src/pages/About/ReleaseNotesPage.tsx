import React, { JSX, useState } from "react";
import { Col, Container, Row } from "react-bootstrap";
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.scss";
import { LAST_VERSION, releaseNotes as releaseNotesRegistry, version, VERSIONS } from "../../releaseNotes/versions";
import { useWhatsNew } from "../../contexts/WhatsNewContext";
import { Accordion } from "../../components/Accordion/Accordion";

const ReleaseNotesPage = (): JSX.Element => {
	const [openVersion, setOpenVersion] = useState<string | null>(LAST_VERSION);
	const { showWhatsNew } = useWhatsNew();

	return (
		<div className="gradient-bg" style={{ borderRadius: "18px", overflow: "hidden" }}>
			<Container className="py-5">
				<Row className="justify-content-center mb-4">
					<Col lg={8} className="text-center">
						<h2 className="display-5 fw-bold">Release Notes</h2>
						<Button variant="outline-primary" className="mt-3" onClick={showWhatsNew}>
							<i className="bi bi-stars me-2" />
							View What's New in {LAST_VERSION}
						</Button>
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
	);
};

export default ReleaseNotesPage;
