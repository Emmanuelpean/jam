import React, { JSX, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import JobRatingDashboard from "./JobRatingDashboard/JobRatingDashboardPage";
import JobScraperDashboard from "./JobScrapingDashboard/JobScraperDashboardPage";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { jobRatingServiceRunnerApi, jobScraperServiceApi } from "../../services/api/Services";
import { RenderLabeledInput, renderControl, renderStatusIcons, useServiceControl } from "./ServiceUtils";
import { Popover } from "../../components/Popover/Popover";
import { useAuth } from "../../contexts/AuthContext";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import "./Service.scss";

type ActiveTab = "scraping" | "rating";

const ServiceDashboards = (): JSX.Element => {
	const location = useLocation();
	const navigate = useNavigate();
	const { token } = useAuth();
	const activeTab: ActiveTab = location.pathname === "/services/job-rating" ? "rating" : "scraping";

	const scraping = useServiceRunnerStatus(jobScraperServiceApi);
	const rating = useServiceRunnerStatus(jobRatingServiceRunnerApi);

	// Scraper config form (initialised once from the service status).
	const [scrapingForm, setScrapingForm] = useState<{ period_hours: number; timedelta_days: number }>({
		period_hours: 0,
		timedelta_days: 0,
	});
	const scrapingFormInitialised = useRef<boolean>(false);
	useEffect(() => {
		if (scraping.serviceStatus && !scrapingFormInitialised.current) {
			setScrapingForm({
				period_hours: scraping.serviceStatus.period_hours || 0,
				timedelta_days: scraping.serviceStatus.service_kwargs?.timedelta_days || 0,
			});
			scrapingFormInitialised.current = true;
		}
	}, [scraping.serviceStatus]);

	// Rating config form.
	const [ratingForm, setRatingForm] = useState<{ period_hours: number }>({ period_hours: 0 });
	useEffect((): void => {
		setRatingForm({ period_hours: rating.serviceStatus?.period_hours || 0 });
	}, [rating.serviceStatus?.period_hours]);

	const onChangeField = (
		setForm: React.Dispatch<React.SetStateAction<any>>,
		event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent
	): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;
		setForm((prev: any) => ({ ...prev, [name]: value === "" ? "" : Number(value) || 3 }));
	};

	const scrapingControl = useServiceControl(
		token,
		scraping.fetchStatus,
		(t: string) => jobScraperServiceApi.start(scrapingForm.period_hours, scrapingForm.timedelta_days, t),
		(t: string) => jobScraperServiceApi.stop(t)
	);
	const ratingControl = useServiceControl(
		token,
		rating.fetchStatus,
		(t: string) => jobRatingServiceRunnerApi.start(ratingForm.period_hours, t),
		(t: string) => jobRatingServiceRunnerApi.stop(t)
	);

	const scrapingDisabled: boolean = scraping.serviceStatus?.service_runner_status !== "stopped";
	const scrapingFields: React.ReactNode = scraping.serviceStatus && (
		<>
			{RenderLabeledInput(
				"period_hours",
				"Scraping Period",
				"Time between scraping runs.",
				scrapingForm.period_hours,
				"Hour(s)",
				!scrapingDisabled,
				(e) => onChangeField(setScrapingForm, e),
				scrapingDisabled
			)}
			{RenderLabeledInput(
				"timedelta_days",
				"Time Delta",
				"Number of days back to scrape job postings for each run.",
				scrapingForm.timedelta_days,
				"Day(s)",
				!scrapingDisabled,
				(e) => onChangeField(setScrapingForm, e),
				scrapingDisabled
			)}
		</>
	);

	const ratingDisabled: boolean = rating.serviceStatus?.service_runner_status !== "stopped";
	const ratingFields: React.ReactNode =
		rating.serviceStatus &&
		RenderLabeledInput(
			"period_hours",
			"Scraping Period",
			"Time between rating runs.",
			ratingForm.period_hours,
			"Hour(s)",
			!ratingDisabled,
			(e) => onChangeField(setRatingForm, e),
			ratingDisabled
		);

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
					statusContent={
						<Popover
							trigger={renderStatusIcons(scraping.serviceStatus, scraping.remainingTime)}
							ariaLabel="Job scraping service controls"
						>
							{(close) =>
								renderControl(
									scraping.serviceStatus,
									scrapingFields,
									scrapingControl.loading,
									() => {
										close();
										scrapingControl.handleStart();
									},
									() => {
										close();
										scrapingControl.handleStop();
									}
								)
							}
						</Popover>
					}
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
					statusContent={
						<Popover
							trigger={renderStatusIcons(rating.serviceStatus, rating.remainingTime)}
							ariaLabel="Job rating service controls"
						>
							{(close) =>
								renderControl(
									rating.serviceStatus,
									ratingFields,
									ratingControl.loading,
									() => {
										close();
										ratingControl.handleStart();
									},
									() => {
										close();
										ratingControl.handleStop();
									}
								)
							}
						</Popover>
					}
				/>
			</div>

			{activeTab === "rating" ? (
				<JobRatingDashboard
					serviceStatus={rating.serviceStatus}
					remainingTime={rating.remainingTime}
					fetchStatus={rating.fetchStatus}
					statusError={rating.statusError}
				/>
			) : (
				<JobScraperDashboard
					serviceStatus={scraping.serviceStatus}
					remainingTime={scraping.remainingTime}
					fetchStatus={scraping.fetchStatus}
					statusError={scraping.statusError}
				/>
			)}
		</div>
	);
};

export default ServiceDashboards;
