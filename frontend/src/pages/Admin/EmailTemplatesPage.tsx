import React, { useEffect, useState, JSX } from "react";
import { Col, Row, Spinner } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { emailApi } from "../../services/api/Others";
import "../UserSettings/UserSettingsPage.scss";

interface TemplateItem {
	id: string;
	label: string;
	icon: string;
}

const TEMPLATES: TemplateItem[] = [
	{ id: "email_confirmation", label: "Email Confirmation", icon: "envelope-check" },
	{ id: "password_reset", label: "Password Reset", icon: "key" },
	{ id: "email_change", label: "Email Change Verification", icon: "envelope-arrow-up" },
	{ id: "password_changed", label: "Password Changed", icon: "lock" },
	{ id: "email_changed", label: "Email Changed", icon: "envelope-at" },
	{ id: "trial_end_reminder", label: "Trial End Reminder", icon: "hourglass-split" },
	{ id: "new_version", label: "New Version Announcement", icon: "stars" },
];

export const EmailTemplatesContent: React.FC = (): JSX.Element => {
	const { token } = useAuth();
	const [selected, setSelected] = useState<string>(TEMPLATES[0]!.id);
	const [html, setHtml] = useState<string>("");
	const [loadingPreview, setLoadingPreview] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);

	useEffect((): void => {
		if (!selected || !token) return;

		const fetchPreview = async () => {
			setLoadingPreview(true);
			setHtml("");
			setError(null);
			try {
				const result: string = await emailApi.fetchTemplateHtml(selected, token);
				setHtml(result);
			} catch {
				setError(`Failed to load preview for "${TEMPLATES.find((t) => t.id === selected)?.label}".`);
			} finally {
				setLoadingPreview(false);
			}
		};

		void fetchPreview();
	}, [selected, token]);

	return (
		<div className="container-fluid d-flex flex-column" style={{ height: "calc(100vh - 140px)" }}>
			<Row className="g-0 settings-layout" style={{ flex: 1, minHeight: 0 }}>
				<Col md={3} lg={2} className="settings-sidebar-col" style={{ width: "360px" }}>
					<div className="settings-sidebar">
						<nav className="settings-nav">
							{TEMPLATES.map(
								(item: TemplateItem): JSX.Element => (
									<button
										key={item.id}
										type="button"
										className={`settings-nav-item ${selected === item.id ? "active" : ""}`}
										onClick={() => setSelected(item.id)}
									>
										<span className="settings-nav-icon">
											<i className={`bi bi-${item.icon}`}></i>
										</span>
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
						{error && <div className="alert alert-danger">{error}</div>}

						{loadingPreview ? (
							<div className="d-flex justify-content-center align-items-center" style={{ flex: 1 }}>
								<Spinner animation="border" />
							</div>
						) : (
							<iframe
								title={selected}
								srcDoc={html}
								style={{
									flex: 1,
									width: "100%",
									border: "1px solid var(--bs-border-color)",
									borderRadius: "7.2px",
									background: "#fff",
								}}
								sandbox="allow-same-origin"
							/>
						)}
					</div>
				</Col>
			</Row>
		</div>
	);
};
