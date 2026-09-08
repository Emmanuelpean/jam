import React, { JSX, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ScrapedJobsTable from "../../components/DataTable/ScrapedJobTable";
import JobEmailTable from "../../components/DataTable/JobEmailTable";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import PageHeaderGroup, { PageHeaderTab } from "../PageHeader/PageHeaderGroup";
import { useTour } from "../../contexts/TourContext";

type ActiveTab = "alerts" | "emails";

export const ScrapedJobsPage = (): JSX.Element => {
	const navigate = useNavigate();
	const location = useLocation();
	const activeTab: ActiveTab = location.pathname === "/job-alerts/emails" ? "emails" : "alerts";
	const { isTourActive } = useTour();
	const tourQueryParams = isTourActive ? { tour_only: "true" } : undefined;
	const [alertsCount, setAlertsCount] = useState<number>(0);
	const [emailsCount, setEmailsCount] = useState<number>(0);
	const [alertsReload, setAlertsReload] = useState<number>(0);
	const previousTabRef = useRef<ActiveTab>(activeTab);

	useEffect(() => {
		if (activeTab === "alerts" && previousTabRef.current !== "alerts") {
			setAlertsReload((n: number): number => n + 1);
		}
		previousTabRef.current = activeTab;
	}, [activeTab]);

	const tabs: PageHeaderTab[] = [
		{
			id: "alerts",
			headerId: "scraped-jobs-header",
			title: "Job Alerts",
			icon: getEntityIcon("scrapedJob"),
			count: alertsCount,
		},
		{
			id: "emails",
			headerId: "job-emails-header",
			title: "Job Emails",
			icon: getEntityIcon("jobEmail"),
			count: emailsCount,
		},
	];

	const tabPaths: Record<ActiveTab, string> = { alerts: "/job-alerts/jobs", emails: "/job-alerts/emails" };

	return (
		<>
			<PageHeaderGroup
				tabs={tabs}
				activeId={activeTab}
				onSelect={(tab: PageHeaderTab): void => void navigate(tabPaths[tab.id as ActiveTab], { replace: true })}
			/>

			<div style={{ display: activeTab === "alerts" ? "contents" : "none" }}>
				<ScrapedJobsTable
					onTotalCountChange={setAlertsCount}
					reloadTrigger={alertsReload}
					queryParamsOverride={tourQueryParams}
				/>
			</div>
			<div style={{ display: activeTab === "emails" ? "contents" : "none" }}>
				<JobEmailTable onTotalCountChange={setEmailsCount} queryParams={tourQueryParams} />
			</div>
		</>
	);
};
