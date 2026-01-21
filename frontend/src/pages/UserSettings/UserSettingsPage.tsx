import React, { JSX, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Col, Row } from "react-bootstrap";
import { AccountTab } from "./AccountTab";
import { PreferencesTab } from "./PreferencesTab";
import { QualificationsTab } from "./QualificationsTab";
import { PremiumTab } from "./PremiumTab";
import "./UserSettingsPage.scss";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";
import PageHeader from "../PageHeader/PageHeader";

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

	// Set active tab based on URL parameter
	const activeTab: tabs = tab || "account";

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
			<PageHeader title={"User Settings"} icon={getTableIcon("User Settings")} />
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
							) : null
						)}
					</div>
				</Col>

				<Col className="p-4 overflow-auto">
					{activeTab === "account" && <AccountTab />}
					{activeTab === "preferences" && <PreferencesTab />}
					{activeTab === "qualifications" && <QualificationsTab />}
					{activeTab === "premium" && <PremiumTab />}
				</Col>
			</Row>
		</div>
	);
};

export default UserSettingsPage;
