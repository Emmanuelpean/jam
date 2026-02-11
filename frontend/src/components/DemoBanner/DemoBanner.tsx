import React, { JSX } from "react";
import { useAuth } from "../../contexts/AuthContext";
import "./DemoBanner.scss";

export function DemoBanner(): JSX.Element | null {
	const { currentUser } = useAuth();

	if (!currentUser?.is_demo) return null;

	return (
		<div className="demo-banner" role="status" id="demo-banner">
			<i className="bi bi-incognito" />
			<span>
				You are using a <strong>demo account</strong>. All data will be permanently deleted when you log out.
			</span>
		</div>
	);
}
