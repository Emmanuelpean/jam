import React, { JSX } from "react";
import { Col, Container, Row } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AboutPage.scss";
import AppFeaturesList, { Feature } from "./AppFeaturesList";
import { useViewport } from "../../contexts/ViewportContext";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";

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
	const { isMobile } = useViewport();
	return (
		<div style={{ flex: 1 }}>
			{isMobile && <PageHeader title="Browser Extension" icon={getTableIcon("Browser Extension")} />}
			<div className="about-container d-flex flex-column align-items-center justify-content-center">
				<div className="hero-overlay">
					<Container className="py-5">
						<Row className="justify-content-center text-center py-5">
							<Col lg={8}>
								<div className="extension-about-icon">
									<i className="bi bi-puzzle-fill" />
								</div>
								<div
									className="logo-text-below text-gradient-primary"
									style={{ fontSize: "45px", fontWeight: "bold" }}
								>
									SPREAD
								</div>
								<div
									className="d-flex flex-column flex-sm-row align-items-center justify-content-center gap-3 mt-3"
									style={{ fontSize: "15.3px" }}
								>
									<div className="glass-badge">
										<span className="about-text-muted">Version</span>
										<span className="link-gradient ms-2">1.0.0</span>
									</div>
									<a
										href="https://chromewebstore.google.com/detail/spread/dnkmbfflallehleblligcokipgijnbhe"
										target="_blank"
										rel="noopener noreferrer"
										className="glass-badge link-gradient"
										style={{ textDecoration: "none", fontSize: "15.3px" }}
									>
										<i className="bi bi-download me-2" />
										Install from Chrome Web Store
									</a>
								</div>
							</Col>
						</Row>
					</Container>
				</div>

				<Container className="py-5">
					<Row className="justify-content-center mb-5">
						<Col lg={12} className="text-center mb-2">
							<h2 className="display-5 fw-bold">
								Smart Plugin for Recruitment Extraction &amp; Aggregation of Data
							</h2>
						</Col>
						<Col lg={10}>
							<p
								className="fs-5 about-text-muted mb-0"
								style={{ lineHeight: "1.625", textAlign: "center" }}
							>
								SPREAD is a Chrome extension that connects your browser directly to JAM. Browse job
								listings on aggregator websites such as LinkedIn and Indeed, click one button, and the
								full job details are instantly imported - no copy-pasting, no manual entry.
							</p>
						</Col>
					</Row>

					<Row className="justify-content-center mb-5">
						<Col lg={8} className="text-center mb-2">
							<h2 className="display-5 fw-bold">What SPREAD Can Do For You</h2>
						</Col>
					</Row>
					<AppFeaturesList features={extensionFeatures} className="mb-5" />

					<Row className="justify-content-center">
						<Col lg={8} className="text-center">
							<p className="about-text-muted mb-3">Supported platforms</p>
							<div className="d-flex justify-content-center gap-2 flex-wrap">
								{[
									{ label: "LinkedIn", color: "#0a66c2" },
									{ label: "Indeed", color: "#0a66c2" },
									{ label: "NHS Jobs", color: "#0a66c2" },
									{ label: "VeganJobs", color: "#0a66c2" },
								].map((p) => (
									<span
										key={p.label}
										className="extension-platform-badge"
										style={{ background: p.color }}
									>
										{p.label}
									</span>
								))}
							</div>
						</Col>
					</Row>
				</Container>
			</div>
		</div>
	);
};

export default ExtensionPage;
