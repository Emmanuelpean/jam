import React, { JSX } from "react";
import { Col, Container, Row } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.scss";
import AppFeaturesList, { Feature } from "./AppFeaturesList";

const extensionFeatures: Feature[] = [
	{
		icon: "bi-cursor-fill",
		title: "One-Click Import",
		description: "Save any supported job listing to JAM in a single click - no manual data entry required",
	},
	{
		icon: "bi-magic",
		title: "Auto-Fills Job Details",
		description: "Title, company, salary, location, and description are scraped and pre-filled automatically",
	},
	{
		icon: "bi-search",
		title: "Smart Detection",
		description: "Automatically detects when you're on a supported job listing page and activates instantly",
	},
	{
		icon: "bi-grid",
		title: "Multi-Platform Support",
		description: "Works across LinkedIn, Indeed, NHS Jobs, and VeganJobs - with more platforms planned",
	},
];

const ExtensionPage = (): JSX.Element => {
	return (
		<div
			className="d-flex flex-column align-items-center justify-content-center"
			style={{
				borderRadius: "18px",
				overflow: "hidden",
				minHeight: "100%",
				backgroundColor: "var(--bs-body-bg)",
				border: "1px solid var(--bs-card-border-color)",
				boxShadow: "0 4px 24px rgb(0 0 0 / 10%)",
			}}
		>
			<Container className="py-5">
				<div className="text-center mb-4">
					<div className="extension-about-icon">
						<i className="bi bi-puzzle-fill" />
					</div>
					<h2 className="display-5 fw-bold mt-3">SPREAD Chrome Extension</h2>
					<p
						className="about-text-muted mt-2"
						style={{ fontSize: "1.3rem", letterSpacing: "0.06em", textTransform: "uppercase" }}
					>
						Smart Plugin for Recruitment Extraction &amp; Aggregation of Data
					</p>
					<a
						href="https://chromewebstore.google.com/detail/spread/dnkmbfflallehleblligcokipgijnbhe"
						target="_blank"
						rel="noopener noreferrer"
						className="extension-about-badge m-1"
						style={{ textDecoration: "none" }}
					>
						<i className="bi bi-download me-2" />
						Install from Chrome Web Store
					</a>
				</div>

				<Row className="justify-content-center mb-4">
					<Col lg={10}>
						<p className="fs-5 about-text-muted mb-0" style={{ lineHeight: "1.625", textAlign: "center" }}>
							SPREAD is a Chrome extension that connects your browser directly to JAM. Browse job listings
							on aggregator websites such as LinkedIn and Indeed, click one button, and the full job
							details are instantly imported - no copy-pasting, no manual entry.
						</p>
					</Col>
				</Row>

				<AppFeaturesList features={extensionFeatures} className="mb-4" />

				<div className="text-center">
					<p className="about-text-muted mb-3">Supported platforms</p>
					<div className="d-flex justify-content-center gap-2 flex-wrap">
						{[
							{ label: "LinkedIn", color: "#0a66c2" },
							{ label: "Indeed", color: "#0a66c2" },
							{ label: "NHS Jobs", color: "#0a66c2" },
							{ label: "VeganJobs", color: "#0a66c2" },
						].map((p) => (
							<span key={p.label} className="extension-platform-badge" style={{ background: p.color }}>
								{p.label}
							</span>
						))}
					</div>
				</div>
			</Container>
		</div>
	);
};

export default ExtensionPage;
