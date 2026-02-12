import React, { JSX } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { AppBanner } from "./AppBanner";

export function DemoBanner(): JSX.Element | null {
	const { currentUser } = useAuth();

	if (!currentUser?.is_demo) return null;

	return (
		<AppBanner icon="bi-incognito" colorClass="bg-warning" id="demo-banner">
			You are using a <strong>demo account</strong>. All data will be permanently deleted when you log out.
		</AppBanner>
	);
}
