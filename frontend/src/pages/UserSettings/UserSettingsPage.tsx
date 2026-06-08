import React, { JSX, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
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

	const contentColRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		contentColRef.current?.scrollTo({ top: 0 });
	}, [activeTab]);

	const handleTabChange = (tabId: tabs): void => {
		navigate(`/settings/${tabId}`);
	};

	return (
		<div className="container-fluid d-flex flex-column settings-page-container">
			<PageHeader title={"User Settings"} icon={getTableIcon("User Settings")} />
			<div className="settings-layout">
				<div className="settings-sidebar-col">
					<div className="settings-sidebar">
						<nav className="settings-nav">
							{menuItems.map((item: MenuItem): JSX.Element | null =>
								!(item.conditional === false) ? (
									<button
										key={item.id}
										id={`${item.id}-tab`}
										type="button"
										className={`settings-nav-item ${activeTab === item.id ? "active" : ""}`}
										onClick={(): void => handleTabChange(item.id)}
									>
										<span className="settings-nav-icon">
											<i className={`bi bi-${item.icon}`}></i>
										</span>
										<span className="settings-nav-label">{item.label}</span>
									</button>
								) : null
							)}
						</nav>
					</div>
				</div>

				<div className="settings-content-col" ref={contentColRef}>
					<div className="settings-content">
						{activeTab === "account" && <AccountTab />}
						{activeTab === "preferences" && <PreferencesTab />}
						{activeTab === "qualifications" && <QualificationsTab />}
						{activeTab === "premium" && <PremiumTab />}
					</div>
				</div>
			</div>
		</div>
	);
};

export default UserSettingsPage;
