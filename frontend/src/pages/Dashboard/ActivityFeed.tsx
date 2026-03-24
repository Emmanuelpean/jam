import React, { JSX, ReactNode } from "react";
import "./DashboardPage.scss";
import {
	renderFunctions,
	RenderParams,
	RenderViewFieldWithContext,
	ViewField,
} from "../../components/rendering/view/ViewRenders";
import { getTableIcon } from "../../components/rendering/view/Icons";
import {
	EnrichedInterviewData,
	EnrichedJobApplicationUpdateData,
	EnrichedJobData,
	JobData,
} from "../../services/schemas/DataTables";
import { formatActivityDate } from "../../utils/TimeUtils";
import { DashboardCard } from "./DashboardCard";

const getActivityColor = (type: string): string => {
	const colorMap: Record<string, string> = {
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
	const iconMap: Record<string, string> = {
		Application: getTableIcon("Job Applications"),
		Interview: getTableIcon("Interviews"),
		"Job Application Update": getTableIcon("Job Application Updates"),
	};
	return iconMap[type] || "bi-plus-circle-fill";
};

interface TimelineItemProps {
	colorClass: string;
	icon: string;
	isLast: boolean;
	title: ReactNode;
	date: Date;
	dateOnly?: boolean;
	children: ReactNode;
}

const TimelineItem: React.FC<TimelineItemProps> = ({
	colorClass,
	icon,
	isLast,
	title,
	date,
	dateOnly,
	children,
}: TimelineItemProps): JSX.Element => (
	<div className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
		<div className="d-flex position-relative">
			{!isLast && <div className="position-absolute activity-line" />}
			<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
				<div
					className={`rounded-circle d-flex align-items-center justify-content-center badge ${colorClass}`}
					style={{ width: "31.5px", height: "31.5px" }}
				>
					<i className={`bi-${icon} text-white`} style={{ fontSize: "1rem" }} />
				</div>
			</div>
			<div className="flex-grow-1 min-width-0">
				<div className="activity-header d-flex align-items-start justify-content-between mb-1">
					<div className="fw-semibold activity-title" style={{ fontSize: "1rem" }}>
						{title}
					</div>
					<small className="text-muted activity-date">{formatActivityDate(date, dateOnly)}</small>
				</div>
				{children}
			</div>
		</div>
	</div>
);

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
	date: Date;
	type: "Application" | "Interview" | "Job Application Update";
	job_id: number | null | undefined | string;
}

export const renderRecentActivityItem = (activity: RecentActivity, index: number, isLast: boolean): JSX.Element => {
	const number =
		activity.type === "Interview" || activity.type === "Job Application Update"
			? ` #${"number" in activity.data ? activity.data.number : ""}`
			: "";

	const badgeRenderer = getActivityBadge(activity.type);
	const activityData = activity.type === "Application" ? activity : activity.data;

	const jobField: ViewField = {
		key: "activity-item-" + index,
		render: (params: RenderParams): ReactNode => badgeRenderer(params),
	};

	return (
		<TimelineItem
			key={`activity-${index}`}
			colorClass={getActivityColor(activity.type)}
			icon={getActivityIcon(activity.type)}
			isLast={isLast}
			title={`${activity.type}${number}`}
			date={activity.date}
		>
			<RenderViewFieldWithContext field={jobField} item={activityData} id={index.toString()} />
		</TimelineItem>
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

	return (
		<TimelineItem
			key={`interview-${index}`}
			colorClass={getActivityColor("Interview")}
			icon={getActivityIcon("Interview")}
			isLast={isLast}
			title={`${interview.type} (interview #${interview.number})`}
			date={interview.date}
		>
			<RenderViewFieldWithContext field={jobField} item={interview} id={index.toString()} />
		</TimelineItem>
	);
};

export const renderPastInterviewItem = (
	interview: EnrichedInterviewData,
	index: number,
	isLast: boolean
): JSX.Element => {
	const jobField: ViewField = {
		key: "activity-item-" + index,
		render: (params: RenderParams) => renderFunctions.interviewBadge(params),
	};

	return (
		<TimelineItem
			key={`past-interview-${index}`}
			colorClass="bg-secondary"
			icon={getActivityIcon("Interview")}
			isLast={isLast}
			title={`${interview.type} (interview #${interview.number})`}
			date={interview.date}
		>
			<RenderViewFieldWithContext field={jobField} item={interview} id={index.toString()} />
		</TimelineItem>
	);
};

export const renderStatusUpdateItem = (
	update: EnrichedJobApplicationUpdateData,
	index: number,
	isLast: boolean
): JSX.Element => {
	const jobField: ViewField = {
		key: "activity-item-" + index,
		render: (params: RenderParams) => renderFunctions.jobApplicationUpdateBadge(params),
	};

	return (
		<TimelineItem
			key={`status-update-${index}`}
			colorClass={getActivityColor("Job Application Update")}
			icon={getActivityIcon("Job Application Update")}
			isLast={isLast}
			title={`Update #${update.number}`}
			date={update.date}
		>
			<RenderViewFieldWithContext field={jobField} item={update} id={index.toString()} />
		</TimelineItem>
	);
};

export const renderUpcomingDeadlineItem = (job: EnrichedJobData, index: number, isLast: boolean): JSX.Element => {
	const jobField: ViewField = {
		key: "activity-item-" + index,
		render: (params: RenderParams) => renderFunctions.jobBadge(params),
	};

	return (
		<TimelineItem
			key={`deadline-${index}`}
			colorClass="bg-warning"
			icon="alarm"
			dateOnly
			isLast={isLast}
			title={job.name || job.title}
			date={job.deadline as Date}
		>
			<RenderViewFieldWithContext field={jobField} item={{ job_id: job.id }} id={index.toString()} />
		</TimelineItem>
	);
};
