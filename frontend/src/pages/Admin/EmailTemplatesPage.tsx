import React, { useState, JSX } from "react";
import { Col, Row } from "react-bootstrap";
import { useDataContext } from "../../contexts/DataContext";
import { EmailTemplate } from "../../services/api/Others";
import "../UserSettings/UserSettingsPage.scss";

const EmailTemplatesContent: React.FC = (): JSX.Element => {
	const { emailTemplates } = useDataContext();
	const [selectedId, setSelectedId] = useState<string | null>(null);

	const selected: EmailTemplate | null =
		emailTemplates.find((t: EmailTemplate): boolean => t.id === selectedId) ?? emailTemplates[0] ?? null;

	return (
		<div className="container-fluid d-flex flex-column" style={{ height: "calc(100vh - 140px)" }}>
			<Row className="g-0 settings-layout" style={{ flex: 1, minHeight: 0 }}>
				<Col md={3} lg={2} className="settings-sidebar-col" style={{ width: "360px" }}>
					<div className="settings-sidebar">
						<nav className="settings-nav">
							{emailTemplates.map(
								(item: EmailTemplate): JSX.Element => (
									<button
										key={item.id}
										type="button"
										className={`settings-nav-item ${selected?.id === item.id ? "active" : ""}`}
										onClick={() => setSelectedId(item.id)}
									>
										<span className="settings-nav-label">{item.label}</span>
									</button>
								)
							)}
						</nav>
					</div>
				</Col>

				<Col
					className="settings-content-col"
					style={{ display: "flex", flexDirection: "column", minHeight: 0 }}
				>
					<div
						className="settings-content"
						style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}
					>
						{selected ? (
							<iframe
								title={selected.id}
								srcDoc={selected.html}
								style={{
									flex: 1,
									width: "100%",
									border: "1px solid var(--bs-border-color)",
									borderRadius: "7.2px",
									background: "#fff",
								}}
								sandbox="allow-same-origin"
							/>
						) : (
							<div
								className="d-flex justify-content-center align-items-center text-muted"
								style={{ flex: 1 }}
							>
								No email templates available.
							</div>
						)}
					</div>
				</Col>
			</Row>
		</div>
	);
};

export default EmailTemplatesContent;
