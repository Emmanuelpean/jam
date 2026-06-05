import React, { JSX, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ScrapedJobsTable from "../../components/DataTable/ScrapedJobTable";
import JobEmailTable from "../../components/DataTable/JobEmailTable";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import PageHeader from "../PageHeader/PageHeader";
import { useTour } from "../../contexts/TourContext";
import { useViewport } from "../../contexts/ViewportContext";

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

	const switchTab = (tab: ActiveTab): void => {
		if (tab === "alerts") {
			navigate("/job-alerts/jobs", { replace: true });
			setAlertsReload((n: number): number => n + 1);
		} else {
			navigate("/job-alerts/emails", { replace: true });
		}
	};

	return (
		<>
			<div className="d-flex gap-3 page-headers-row">
				<PageHeader
					id="scraped-jobs-header"
					className="flex-fill"
					title="Job Alerts"
					icon={getEntityIcon("scrapedJob")}
					count={alertsCount}
					onClick={(): void => switchTab("alerts")}
					active={activeTab === "alerts"}
				/>
				<PageHeader
					id="job-emails-header"
					className="flex-fill"
					title="Job Emails"
					icon={getEntityIcon("jobEmail")}
					count={emailsCount}
					onClick={(): void => switchTab("emails")}
					active={activeTab === "emails"}
				/>
			</div>

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
