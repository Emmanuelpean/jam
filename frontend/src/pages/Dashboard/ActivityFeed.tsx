import React, { JSX, ReactNode } from "react";
import { Card } from "react-bootstrap";
import "./DashboardPage.css";
import {
	renderFunctions,
	RenderParams,
	RenderViewFieldWithContext,
	ViewField,
} from "../../components/rendering/view/ViewRenders";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { EnrichedInterviewData, EnrichedJobApplicationUpdateData, JobData } from "../../services/schemas/DataTables";
import { formatActivityDate } from "../../utils/TimeUtils";
import { CardHeader } from "./CardHeader";

interface ActivityFeedCardProps<T> {
	icon: string;
	title: string;
	subtitle: string;
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
}: ActivityFeedCardProps<T>) => (
	<Card className="h-100 shadow-sm border-0 d-flex flex-column">
		<CardHeader icon={icon} title={title} subtitle={subtitle} badgeValue={badgeValue} />
		<Card.Body className="p-0 flex-grow-1 d-flex flex-column" style={{ minHeight: 0 }}>
			{items.length === 0 ? (
				<div className="text-center py-5 px-4 flex-grow-1 d-flex flex-column justify-content-center">
					<div className="mb-3">
						<i className={`bi bi-${emptyIcon} text-muted`} style={{ fontSize: "3.5rem" }}></i>
					</div>
					<h6 className="text-muted fw-semibold">{emptyTitle}</h6>
					<p className="text-muted small mb-0">{emptyDescription}</p>
				</div>
			) : (
				<div
					className="activity-timeline px-4 flex-grow-1"
					style={{ overflowY: "auto", height: "100%", minHeight: 0 }}
				>
					{items.map((item, index) => renderItem(item, index, index === items.length - 1))}
				</div>
			)}
		</Card.Body>
	</Card>
);

export interface RecentActivity {
	data: JobData | EnrichedInterviewData | EnrichedJobApplicationUpdateData;
	date: string | Date;
	type: "Application" | "Interview" | "Job Application Update";
	job_id: number | null | undefined | string;
}

export const renderRecentActivityItem = (activity: RecentActivity, index: number, isLast: boolean): JSX.Element => {
	const getActivityIcon = (type: string): string => {
		const iconMap: { [key: string]: string } = {
			Application: getTableIcon("Job Applications"),
			Interview: getTableIcon("Interviews"),
			"Job Application Update": getTableIcon("Job Application Updates"),
		};
		return iconMap[type] || "bi-plus-circle-fill";
	};

	const getActivityColor = (type: string): string => {
		const colorMap: { [key: string]: string } = {
			Application: "#2563eb",
			Interview: "#10b981",
			"Job Application Update": "#f59e42",
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
		render: (params: RenderParams) => activityBadge(params),
	};

	return (
		<div key={`activity-${index}`} className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
			<div className="d-flex position-relative">
				{/* Timeline line */}
				{!isLast && <div className="position-absolute activity-line"></div>}

				{/* Activity icon */}
				<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
					<div
						className="rounded-circle d-flex align-items-center justify-content-center"
						style={{
							width: "35px",
							height: "35px",
							backgroundColor: activityColor,
						}}
					>
						<i className={`bi-${activityIcon} text-white`} style={{ fontSize: "1rem" }}></i>
					</div>
				</div>

				{/* Activity content */}
				<div className="flex-grow-1 min-width-0">
					<div className="d-flex align-items-start justify-content-between mb-1">
						<div className="fw-semibold" style={{ fontSize: "1rem" }}>
							{activity.type} {getActivityNumber(activity)}
						</div>
						<small className="text-muted flex-shrink-0 ms-2">{formatActivityDate(activity.date)}</small>
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
	isLast: boolean,
): JSX.Element => {
	const jobField: ViewField = {
		key: "activity-item-" + index,
		render: (params: RenderParams) => renderFunctions.interviewBadge(params),
	};

	return (
		<div key={`interview-${index}`} className={`activity-item ${!isLast ? "mb-4" : "mb-3"}`}>
			<div className="d-flex position-relative">
				{/* Timeline line */}
				{!isLast && <div className="position-absolute activity-line"></div>}
				{/* Interview icon */}
				<div className="flex-shrink-0 me-3 position-relative" style={{ zIndex: 1 }}>
					<div
						className="rounded-circle d-flex align-items-center justify-content-center"
						style={{
							width: "35px",
							height: "35px",
							backgroundColor: "#8b5cf6",
						}}
					>
						<i className="bi bi-people-fill text-white" style={{ fontSize: "1rem" }}></i>
					</div>
				</div>
				{/* Interview content */}
				<div className="flex-grow-1 min-width-0">
					<div className="d-flex align-items-start justify-content-between mb-1">
						<div className="fw-semibold text-dark" style={{ fontSize: "0.95rem" }}>
							{interview.type} (interview #{interview.number})
						</div>
						<small className="text-muted flex-shrink-0 ms-2">{formatActivityDate(interview.date!)}</small>
					</div>
					<RenderViewFieldWithContext field={jobField} item={interview} id={index.toString()} />
				</div>
			</div>
		</div>
	);
};
