import React from "react";
import { ReactComponent as JamLogo } from "../assets/Logo.svg";
import packageJson from "../../package.json";
import Accordion from "react-bootstrap/Accordion";
import "bootstrap/dist/css/bootstrap.min.css";

const AboutPage: React.FC = () => {
	const releaseNotes = {
		"1.0.0":
			"Initial release of Jam, the Job Application Manager. Features include job application tracking, interview scheduling, company and contact management, and application status monitoring.",
	};

	return (
		<div
			style={{
				display: "flex",
				flexDirection: "column",
				justifyContent: "center",
				alignItems: "center",
			}}
		>
			<div style={{ marginBottom: 24, paddingTop: "20vh" }}>
				<JamLogo style={{ height: "135px" }} />
				<div className="logo-text-below text-gradient-primary" style={{ fontSize: "35px" }}>
					Job Application Manager
				</div>
			</div>
			<h4>
				Version{" "}
				<a href="https://github.com/Emmanuelpean/jam" target="_blank" rel="noopener noreferrer">
					{packageJson.version}
				</a>
			</h4>

			<div>
				App created and maintained by{" "}
				<a href="https://emmanuelpean.me/" target="_blank" rel="noopener noreferrer">
					Emmanuel V. Péan
				</a>
				.
			</div>
			<p style={{ maxWidth: 1200, fontSize: "18px", marginTop: "16px" }}>
				<b>Jam</b> is a user-friendly web app designed to help you manage your jobs, applications, interviews,
				and everything in-between. Job search can be a time-consuming and tedious process, requiring you to keep
				track of many jobs and applications at the same time. <b>Jam</b> aims to make this process easier so
				that you can get the job of your dreams. <b>Jam</b> can:
				<ul style={{ maxWidth: 1200 }}>
					<li>Create and manage job application records</li>
					<li>Track interview schedules and outcomes</li>
					<li>Store company and contact information</li>
					<li>Monitor application status, progress, and deadlines</li>
				</ul>
			</p>
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
		</div>
	);
};

export default AboutPage;
