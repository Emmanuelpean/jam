import React, { JSX, useContext, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import JobRatingDashboard from "./JobRatingDashboard/JobRatingDashboardPage";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { jobRatingServiceRunnerApi } from "../../services/api/Services";
import { RenderLabeledInput, renderControl, renderStatusIcons, useServiceControl } from "./ServiceUtils";
import { Popover } from "../../components/Popover/Popover";
import { useAuth } from "../../contexts/AuthContext";
import { ModalHeaderSlotContext } from "../../contexts/ModalHeaderSlotContext";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import "./Service.scss";

const JobRatingPage = (): JSX.Element => {
	const { token } = useAuth();
	const rating = useServiceRunnerStatus(jobRatingServiceRunnerApi);

	const [ratingForm, setRatingForm] = useState<{ period_hours: number }>({ period_hours: 0 });
	useEffect((): void => {
		setRatingForm({ period_hours: rating.serviceStatus?.period_hours || 0 });
	}, [rating.serviceStatus?.period_hours]);

	const onChangeField = (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent): void => {
		const target = event.target as HTMLInputElement;
		const { name, value } = target;
		setRatingForm((prev: any) => ({ ...prev, [name]: value === "" ? "" : Number(value) || 3 }));
	};

	const ratingControl = useServiceControl(
		token,
		rating.fetchStatus,
		(t: string) => jobRatingServiceRunnerApi.start(ratingForm.period_hours, t),
		(t: string) => jobRatingServiceRunnerApi.stop(t)
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
			onChangeField,
			ratingDisabled
		);

	const headerSlot: HTMLElement | null = useContext(ModalHeaderSlotContext);
	const statusControl: JSX.Element = (
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
	);

	return (
		<div className="scraped-jobs-page">
			{headerSlot ? (
				createPortal(statusControl, headerSlot)
			) : (
				<PageHeader
					title="Job Rating"
					icon={getTableIcon("Job Rating Dashboard")}
					statusContent={statusControl}
				/>
			)}

			<JobRatingDashboard
				serviceStatus={rating.serviceStatus}
				remainingTime={rating.remainingTime}
				fetchStatus={rating.fetchStatus}
				statusError={rating.statusError}
			/>
		</div>
	);
};

export default JobRatingPage;
