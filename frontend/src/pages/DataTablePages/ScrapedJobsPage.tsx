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
	const [alertsReload, setAlertsReload] = useState<number>(0);
	const [emailsReload, setEmailsReload] = useState<number>(0);

	return (
		<>
			<div className="d-flex gap-3">
				<PageHeader
					id="scraped-jobs-header"
					className="flex-fill"
					title="Job Alerts"
					icon={getEntityIcon("scrapedJob")}
					count={alertsCount}
					onClick={(): void => {
						setActiveTab("alerts");
						setAlertsReload((n) => n + 1);
					}}
					active={activeTab === "alerts"}
				/>
				<PageHeader
					id="job-emails-header"
					className="flex-fill"
					title="Job Emails"
					icon={getEntityIcon("jobEmail")}
					count={emailsCount}
					onClick={(): void => {
						setActiveTab("emails");
						setEmailsReload((n) => n + 1);
					}}
					active={activeTab === "emails"}
				/>
			</div>


			<div style={{ display: activeTab === "alerts" ? "contents" : "none" }}>
				<ScrapedJobsTable onTotalCountChange={setAlertsCount} reloadTrigger={alertsReload} />
			</div>
			<div style={{ display: activeTab === "emails" ? "contents" : "none" }}>
				<JobEmailTable onTotalCountChange={setEmailsCount} reloadTrigger={emailsReload} />
			</div>
		</>
	);
};
