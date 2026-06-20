import React, { JSX, useContext, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import JobScraperDashboard from "./JobScrapingDashboard/JobScraperDashboardPage";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { jobScraperServiceApi } from "../../services/api/Services";
import { RenderLabeledInput, renderControl, renderStatusIcons, useServiceControl } from "./ServiceUtils";
import { Popover } from "../../components/Popover/Popover";
import { useAuth } from "../../contexts/AuthContext";
import { ModalHeaderSlotContext } from "../../contexts/ModalHeaderSlotContext";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import "./Service.scss";

const JobScrapingPage = (): JSX.Element => {
	const { token } = useAuth();
	const scraping = useServiceRunnerStatus(jobScraperServiceApi);

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

	const onChangeField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;
		setScrapingForm((prev: any) => ({ ...prev, [name]: value === "" ? "" : Number(value) || 3 }));
	};

	const scrapingControl = useServiceControl(
		token,
		scraping.fetchStatus,
		(t: string) => jobScraperServiceApi.start(scrapingForm.period_hours, scrapingForm.timedelta_days, t),
		(t: string) => jobScraperServiceApi.stop(t)
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
				onChangeField,
				scrapingDisabled
			)}
			{RenderLabeledInput(
				"timedelta_days",
				"Time Delta",
				"Number of days back to scrape job postings for each run.",
				scrapingForm.timedelta_days,
				"Day(s)",
				!scrapingDisabled,
				onChangeField,
				scrapingDisabled
			)}
		</>
	);

	const headerSlot: HTMLElement | null = useContext(ModalHeaderSlotContext);
	const statusControl: JSX.Element = (
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
	);

	return (
		<div className="scraped-jobs-page">
			{headerSlot ? (
				createPortal(statusControl, headerSlot)
			) : (
				<PageHeader
					title="Job Scraping"
					icon={getTableIcon("Job Scraping Dashboard")}
					statusContent={statusControl}
				/>
			)}

			<JobScraperDashboard
				serviceStatus={scraping.serviceStatus}
				remainingTime={scraping.remainingTime}
				fetchStatus={scraping.fetchStatus}
				statusError={scraping.statusError}
			/>
		</div>
	);
};

export default JobScrapingPage;
