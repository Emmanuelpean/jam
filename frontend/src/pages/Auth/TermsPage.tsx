import React, { JSX } from "react";
import { Col, Container, Row } from "react-bootstrap";
import { TermsContent } from "./TermsConditions";
import "./TermsConditions.scss";
import "../About/AboutPage.scss";

const TermsPage = (): JSX.Element => (
	<div className="gradient-bg" style={{ borderRadius: "20px", overflow: "hidden", minHeight: "100%" }}>
		<Container className="py-5">
			<Row className="justify-content-center mb-4">
				<Col lg={8} className="text-center">
					<i className="bi bi-file-earmark-text" style={{ fontSize: "3rem", color: "var(--primary-mid)" }} />
					<h1 className="display-5 fw-bold mt-3">Terms &amp; Conditions</h1>
					<p className="about-text-muted mt-2">Including the SPREAD Chrome Extension Privacy Policy</p>
				</Col>
			</Row>
			<Row className="justify-content-center">
				<Col lg={10}>
					<TermsContent />
				</Col>
			</Row>
		</Container>
	</div>
);

export default TermsPage;
