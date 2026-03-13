import React, { JSX, useState } from "react";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import JobRatingDashboard from "./JobRatingDashboard/JobRatingDashboardPage";
import JobScraperDashboard from "./JobScrapingDashboard/JobScraperDashboardPage";

type ActiveTab = "scraping" | "rating";

const ServiceDashboards = (): JSX.Element => {
	const [activeTab, setActiveTab] = useState<ActiveTab>("scraping");

	return (
		<div className="scraped-jobs-page">
			<div className="d-flex gap-3">
				<PageHeader
					title="Job Scraping"
					icon={getTableIcon("Job Scraping Dashboard")}
					onClick={(): void => {
						setActiveTab("scraping");
					}}
					active={activeTab === "scraping"}
				/>
				<PageHeader
					title="Job Rating"
					icon={getTableIcon("Job Rating Dashboard")}
					onClick={(): void => {
						setActiveTab("rating");
					}}
					active={activeTab === "rating"}
				/>
			</div>

			{activeTab === "rating" && <JobRatingDashboard />}
			{activeTab === "scraping" && <JobScraperDashboard />}
		</div>
	);
};

export default ServiceDashboards;
