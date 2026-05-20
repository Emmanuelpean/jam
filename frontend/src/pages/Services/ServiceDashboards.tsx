import React, { JSX } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import JobRatingDashboard from "./JobRatingDashboard/JobRatingDashboardPage";
import JobScraperDashboard from "./JobScrapingDashboard/JobScraperDashboardPage";

type ActiveTab = "scraping" | "rating";

const ServiceDashboards = (): JSX.Element => {
	const location = useLocation();
	const navigate = useNavigate();
	const activeTab: ActiveTab = location.pathname === "/services/job-rating" ? "rating" : "scraping";

	return (
		<div className="scraped-jobs-page">
			<div className="d-flex gap-3 page-headers-row">
				<PageHeader
					className="flex-fill"
					id="tab-scraping"
					title="Job Scraping"
					icon={getTableIcon("Job Scraping Dashboard")}
					onClick={(): void => {
						navigate("/services/job-scraping");
					}}
					active={activeTab === "scraping"}
				/>
				<PageHeader
					className="flex-fill"
					id="tab-rating"
					title="Job Rating"
					icon={getTableIcon("Job Rating Dashboard")}
					onClick={(): void => {
						navigate("/services/job-rating");
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
