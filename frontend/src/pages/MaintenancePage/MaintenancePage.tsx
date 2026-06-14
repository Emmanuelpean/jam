import React, { JSX } from "react";
import JamLogo from "../../assets/Logo.svg?react";
import "./MaintenancePage.scss";

export function MaintenancePage(): JSX.Element {
	return (
		<div className="maintenance-page" id="maintenance-page">
			<div className="maintenance-page-content">
				<div className="maintenance-logo">
					<JamLogo />
				</div>
				<h1 className="maintenance-title">We'll be back soon</h1>
				<p className="maintenance-message">
					JAM is currently undergoing scheduled maintenance to bring you new features and improvements.
				</p>
				<div className="maintenance-status">
					<i className="bi bi-gear-wide-connected maintenance-icon"></i>
					<span>Maintenance in progress</span>
				</div>
				<p className="maintenance-note">
					Thank you for your patience. Please check back shortly.
				</p>
			</div>
		</div>
	);
}
