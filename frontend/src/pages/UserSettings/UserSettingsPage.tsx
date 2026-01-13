import React, { JSX, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Card, Col, Row } from "react-bootstrap";
import { AccountTab } from "./AccountTab";
import { PreferencesTab } from "./PreferencesTab";
import { QualificationsTab } from "./QualificationsTab";
import { PremiumTab } from "./PremiumTab";
import "./UserSettingsPage.css";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";

type tabs = "account" | "preferences" | "qualifications" | "premium";

interface MenuItem {
	id: tabs;
	label: string;
	icon: string;
	conditional?: boolean;
}

const UserSettingsPage: React.FC = (): JSX.Element => {
	const { currentUser } = useAuth();
	const navigate = useNavigate();
	const { tab } = useParams<{ tab: tabs }>();
	const [showCheckout, setShowCheckout] = React.useState(false);

	// Set active tab based on URL parameter
	const activeTab = tab || "account";

	// Redirect to default tab if no tab specified
	useEffect(() => {
		if (!tab) {
			navigate("/settings/account", { replace: true });
		}
	}, [tab, navigate]);

	const menuItems: MenuItem[] = [
		{ id: "account", label: "Account", icon: "person" },
		{ id: "preferences", label: "Preferences", icon: "sliders" },
		{
			id: "qualifications",
			label: "Qualifications",
			icon: "mortarboard-fill",
			conditional: currentUser?.premium.is_active,
		},
		{ id: "premium", label: "Premium", icon: "gem" },
	];

	const handleTabChange = (tabId: tabs): void => {
		navigate(`/settings/${tabId}`);
	};

	return (
		<div className="container-fluid d-flex flex-column">
			<Card.Header className="settings-header border-0 p-0 bg-white">
				<div className="d-flex align-items-center p-4">
					<div className="header-icon-wrapper me-3">
						<i className={`bi bi-${getTableIcon("User Settings")}`}></i>
					</div>
					<div>
						<h4 className="mb-0 fw-bold text-dark">User Settings</h4>
						<small className="text-muted">Manage your account</small>
					</div>
				</div>
			</Card.Header>
			<Row className="flex-grow-1 g-0">
				<Col md={2} className="settings-sidebar border-end">
					<div className="list-group list-group-flush">
						{menuItems.map((item: MenuItem): JSX.Element | null =>
							!(item.conditional === false) ? (
								<button
									key={item.id}
									id={`${item.id}-tab`}
									type="button"
									className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center ${
										activeTab === item.id ? "active" : ""
									}`}
									onClick={(): void => handleTabChange(item.id)}
								>
									<span>
										<i className={`bi bi-${item.icon} me-2`}></i>
										{item.label}
									</span>
								</button>
							) : null,
						)}
					</div>
				</Col>

				<Col className="p-4 overflow-auto" style={{ background: "white" }}>
					{activeTab === "account" && <AccountTab />}
					{activeTab === "preferences" && <PreferencesTab />}
					{activeTab === "qualifications" && <QualificationsTab />}
					{activeTab === "premium" && (
						<PremiumTab showCheckout={showCheckout} setShowCheckout={setShowCheckout} />
					)}
				</Col>
			</Row>
		</div>
	);
};

export default UserSettingsPage;
