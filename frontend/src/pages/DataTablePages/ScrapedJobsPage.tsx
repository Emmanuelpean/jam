import React, { JSX, useState } from "react";
import ScrapedJobsTable from "../../components/DataTable/ScrapedJobTable";
import JobEmailTable from "../../components/DataTable/JobEmailTable";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import PageHeader from "../PageHeader/PageHeader";

type ActiveTab = "alerts" | "emails";

export const ScrapedJobsPage = (): JSX.Element => {
	const [activeTab, setActiveTab] = useState<ActiveTab>("alerts");
	const [alertsCount, setAlertsCount] = useState<number>(0);
	const [emailsCount, setEmailsCount] = useState<number>(0);

	return (
		<div className="scraped-jobs-page">
			<div className="d-flex gap-3">
				<PageHeader
					className="flex-fill"
					title="Job Alerts"
					icon={getEntityIcon("scrapedJob")}
					count={alertsCount}
					onClick={(): void => setActiveTab("alerts")}
					active={activeTab === "alerts"}
				/>
				<PageHeader
					className="flex-fill"
					title="Job Emails"
					icon={getEntityIcon("jobEmail")}
					count={emailsCount}
					onClick={(): void => setActiveTab("emails")}
					active={activeTab === "emails"}
				/>
			</div>

			<div style={{ display: activeTab === "alerts" ? "block" : "none" }}>
				<ScrapedJobsTable onTotalCountChange={setAlertsCount} />
			</div>
			<div style={{ display: activeTab === "emails" ? "block" : "none" }}>
				<JobEmailTable onTotalCountChange={setEmailsCount} />
			</div>
		</div>
	);
};
