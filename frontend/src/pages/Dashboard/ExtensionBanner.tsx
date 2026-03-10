import React, { useState } from "react";
import "./ExtensionBanner.scss";
import { useAuth } from "../../contexts/AuthContext";

const ExtensionBanner: React.FC = () => {
	const { currentUser, updateCurrentUser } = useAuth();
	const [dismissed, setDismissed] = useState(false);

	if (!currentUser || currentUser.preferences.extension_banner_dismissed || dismissed) return null;

	const handleDismiss = () => {
		setDismissed(true);
		void updateCurrentUser({ preferences: { extension_banner_dismissed: true } });
	};

	return (
		<div className="extension-banner mb-4">
			<div className="extension-banner-icon">
				<i className="bi bi-puzzle-fill" />
			</div>
			<div className="extension-banner-content">
				<div className="extension-banner-title">
					SPREAD Chrome Extension
					<span className="extension-banner-badge">Coming Soon</span>
				</div>
				<div className="extension-banner-subtitle">
					Import jobs from LinkedIn, Indeed, NHS Jobs & VeganJobs directly into JAM — no copy-pasting needed.
				</div>
			</div>
			<button className="extension-banner-close" onClick={handleDismiss} aria-label="Dismiss">
				<i className="bi bi-x-lg" />
			</button>
		</div>
	);
};

export default ExtensionBanner;
