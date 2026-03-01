import React, { JSX } from "react";
import { Card, Col, Container, Row } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.scss";
import ExtensionBanner from "../Dashboard/ExtensionBanner";

interface Feature {
	icon: string;
	title: string;
	description: string;
}

const extensionFeatures: Feature[] = [
	{
		icon: "bi-cursor-fill",
		title: "One-Click Import",
		description: "Save any supported job listing to JAM in a single click — no manual data entry required",
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
		description: "Works across LinkedIn, Indeed, NHS Jobs, and VeganJobs — with more platforms planned",
	},
];

const ExtensionPage = (): JSX.Element => {
	return (
		<div className="gradient-bg" style={{ borderRadius: "20px", overflow: "hidden", minHeight: "100%" }}>
			<Container className="py-5">
				<ExtensionBanner />

				<div className="text-center mb-4">
					<div className="extension-about-icon">
						<i className="bi bi-puzzle-fill" />
					</div>
					<h2 className="display-5 fw-bold mt-3">SPREAD Chrome Extension</h2>
					<span className="extension-about-badge m-1">Coming Soon</span>
					<p
						className="about-text-muted mt-2"
						style={{ fontSize: "1.3rem", letterSpacing: "0.06em", textTransform: "uppercase" }}
					>
						Smart Plugin for Recruitment Extraction &amp; Aggregation of Data
					</p>
				</div>

				<Row className="justify-content-center mb-4">
					<Col lg={10}>
						<Card className="glass-card border-0 p-4">
							<Card.Body className="text-center">
								<p className="fs-5 about-text-muted mb-0" style={{ lineHeight: "1.625" }}>
									SPREAD is a Chrome extension that connects your browser directly to JAM. Browse job
									listings on LinkedIn, Indeed, NHS Jobs or VeganJobs, click one button, and the full
									job details are instantly imported — no copy-pasting, no manual entry.
								</p>
							</Card.Body>
						</Card>
					</Col>
				</Row>

				<div className="features-grid mb-4">
					{extensionFeatures.map(
						(feature: Feature, index: number): JSX.Element => (
							<div className="feature-card p-4" key={index}>
								<div className="d-flex align-items-start align-items-center">
									<div className="feature-icon me-3">
										<i className={`bi ${feature.icon}`} style={{ fontSize: "2rem" }} />
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

				<div className="text-center">
					<p className="about-text-muted mb-3" style={{ fontSize: "0.85rem" }}>
						Supported platforms
					</p>
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
