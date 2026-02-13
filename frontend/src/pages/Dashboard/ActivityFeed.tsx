import React, { JSX, ReactNode } from "react";
import "./DashboardPage.scss";
import {
	renderFunctions,
	RenderParams,
	RenderViewFieldWithContext,
	ViewField,
} from "../../components/rendering/view/ViewRenders";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { EnrichedInterviewData, EnrichedJobApplicationUpdateData, JobData } from "../../services/schemas/DataTables";
import { formatActivityDate } from "../../utils/TimeUtils";
import { DashboardCard } from "./DashboardCard";

const getActivityColor = (type: string): string => {
	const colorMap: { [key: string]: string } = {
		Application: "bg-primary",
		Interview: "bg-success",
		"Job Application Update": "bg-info",
	};
	return colorMap[type] || "#2563eb";
};

const getActivityBadge = (type: string): ((param: RenderParams) => ReactNode) => {
	const badgeMap: Record<string, (param: RenderParams) => ReactNode> = {
		Application: renderFunctions.jobBadge,
		Interview: renderFunctions.interviewBadge,
		"Job Application Update": renderFunctions.jobApplicationUpdateBadge,
	};
	return badgeMap[type] || renderFunctions.jobBadge;
};

const getActivityIcon = (type: string): string => {
	const iconMap: { [key: string]: string } = {
		Application: getTableIcon("Job Applications"),
		Interview: getTableIcon("Interviews"),
		"Job Application Update": getTableIcon("Job Application Updates"),
	};
	return iconMap[type] || "bi-plus-circle-fill";
};

interface ActivityFeedCardProps<T> {
	icon: string;
	title: string;
	subtitle?: string;
	badgeValue: number;
	emptyIcon: string;
	emptyTitle: string;
	emptyDescription: string;
	items: T[];
	renderItem: (item: T, index: number, isLast: boolean) => JSX.Element;
}

export const ActivityFeedCard = <T,>({
	icon,
	title,
	subtitle,
	badgeValue,
	emptyIcon,
	emptyTitle,
	emptyDescription,
	items,
	renderItem,
}: ActivityFeedCardProps<T>): JSX.Element => (
	<DashboardCard
		icon={icon}
		title={title}
		subtitle={subtitle}
		badgeValue={badgeValue}
		isEmpty={items.length === 0}
		emptyState={{
			icon: emptyIcon,
			title: emptyTitle,
			description: emptyDescription,
		}}
		bodyPadding={false}
	>
		<div className="activity-timeline px-4 flex-grow-1" style={{ overflowY: "auto", height: "100%", minHeight: 0 }}>
			{items.map((item, index) => renderItem(item, index, index === items.length - 1))}
		</div>
	</DashboardCard>
);

export interface RecentActivity {
	data: JobData | EnrichedInterviewData | EnrichedJobApplicationUpdateData;
	date: string | Date;
	type: "Application" | "Interview" | "Job Application Update";
	job_id: number | null | undefined | string;
}

export const renderRecentActivityItem = (activity: RecentActivity, index: number, isLast: boolean): JSX.Element => {
	const getActivityNumber = (activity: RecentActivity): string => {
		if (activity.type === "Interview" || activity.type === "Job Application Update") {
			return `#${"number" in activity.data ? activity.data.number : ""}`;
		} else {
			return "";
		}
	};

	const activityColor: string = getActivityColor(activity.type);
	const activityIcon: string = getActivityIcon(activity.type);
	const activityBadge = getActivityBadge(activity.type);
	const activityData = activity.type === "Application" ? activity : activity.data;

	const jobField: ViewField = {
		key: "activity-item-" + index,
		render: (params: RenderParams): ReactNode => activityBadge(params),
	};

	return (
		<div key={`activity-${index}`} className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
			<div className="d-flex position-relative">
				{/* Timeline line */}
				{!isLast && <div className="position-absolute activity-line"></div>}

				{/* Activity icon */}
				<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
					<div
						className={`rounded-circle d-flex align-items-center justify-content-center badge ${activityColor}`}
						style={{
							width: "35px",
							height: "35px",
						}}
					>
						<i className={`bi-${activityIcon} text-white`} style={{ fontSize: "1rem" }}></i>
					</div>
				</div>

				{/* Activity content */}
				<div className="flex-grow-1 min-width-0">
					<div className="activity-header d-flex align-items-start justify-content-between mb-1">
						<div className="fw-semibold activity-title" style={{ fontSize: "1rem" }}>
							{activity.type} {getActivityNumber(activity)}
						</div>
						<small className="text-muted activity-date">{formatActivityDate(activity.date)}</small>
					</div>
					<RenderViewFieldWithContext field={jobField} item={activityData} id={index.toString()} />
				</div>
			</div>
		</div>
	);
};

export const renderUpcomingInterviewItem = (
	interview: EnrichedInterviewData,
	index: number,
	isLast: boolean
): JSX.Element => {
	const jobField: ViewField = {
		key: "activity-item-" + index,
		render: (params: RenderParams) => renderFunctions.interviewBadge(params),
	};
	const activityColor: string = getActivityColor("Interview");
	const activityIcon: string = getActivityIcon("Interview");

	return (
		<div key={`interview-${index}`} className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
			<div className="d-flex position-relative">
				{/* Timeline line */}
				{!isLast && <div className="position-absolute activity-line"></div>}
				{/* Interview icon */}
				<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
					<div
						className={`rounded-circle d-flex align-items-center justify-content-center ${activityColor}`}
						style={{
							width: "35px",
							height: "35px",
						}}
					>
						<i className={`bi-${activityIcon} text-white`} style={{ fontSize: "1rem" }}></i>
					</div>
				</div>
				{/* Interview content */}
				<div className="flex-grow-1 min-width-0">
					<div className="activity-header d-flex align-items-start justify-content-between mb-1">
						<div className="fw-semibold activity-title" style={{ fontSize: "1rem" }}>
							{interview.type} (interview #{interview.number})
						</div>
						<small className="text-muted activity-date">{formatActivityDate(interview.date)}</small>
					</div>
					<RenderViewFieldWithContext field={jobField} item={interview} id={index.toString()} />
				</div>
			</div>
		</div>
	);
};
