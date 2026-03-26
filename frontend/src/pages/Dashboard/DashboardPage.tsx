import React, { useEffect, useRef, useState, JSX } from "react";
import { ResponsiveGridLayout, Layout, LayoutItem, ResponsiveLayouts, useContainerWidth } from "react-grid-layout";
import { useAuth } from "../../contexts/AuthContext";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import "./DashboardPage.scss";
import JobsToChase from "../../components/DataTable/JobsToChase";
import UpcomingDeadlinesTable from "../../components/DataTable/UpcomingDeadlines";
import { StatCard } from "./StatCard";
import { DashboardCard } from "./DashboardCard";
import {
	ActivityFeedCard,
	renderRecentActivityItem,
	renderUpcomingInterviewItem,
	renderPastInterviewItem,
	renderStatusUpdateItem,
	renderUpcomingDeadlineItem,
} from "./ActivityFeed";
import ScrapedJobsTable from "../../components/DataTable/ScrapedJobTable";
import FavouriteJobsTable from "../../components/DataTable/FavouriteJobsTable";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import {
	DashboardLayoutDataV3,
	generateWidgetId,
	getDefaultLayout,
	getDefaultLayoutForConfig,
	GraphConfig,
	parseLayoutData,
	WidgetConfig,
	WidgetInstance,
} from "./widgetRegistry";
import GraphWidget from "./GraphWidget";
import { useDashboardData } from "./useDashboardData";
import { useAlert } from "../../contexts/AlertContext";
import WidgetPickerModal from "./WidgetPickerModal";
import ExtensionBanner from "./ExtensionBanner";
import { DashboardToolbar } from "./DashboardToolbar";
import { MOBILE_BREAKPOINT, TABLET_BREAKPOINT } from "../../utils/Breakpoints";

function findFirstFit(existing: LayoutItem[], w: number, h: number, cols: number): { x: number; y: number } {
	const maxY = existing.reduce((max, item) => Math.max(max, item.y + item.h), 0);
	for (let y = 0; y <= maxY; y++) {
		for (let x = 0; x <= cols - w; x++) {
			const overlaps = existing.some(
				(item) => x < item.x + item.w && x + w > item.x && y < item.y + item.h && y + h > item.y
			);
			if (!overlaps) return { x, y };
		}
	}
	return { x: 0, y: maxY };
}

const Dashboard: React.FC = () => {
	const { currentUser, updateCurrentUser } = useAuth();
	const { showConfirm, showDelete } = useAlert();
	const { width, containerRef, mounted } = useContainerWidth({ measureBeforeMount: true });
	const [isEditMode, setIsEditMode] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [showWidgetPicker, setShowWidgetPicker] = useState(false);
	const [scrapedJobCount, setScrapedJobCount] = useState<number>(0);
	const [favouriteAlertCount, setFavouriteAlertCount] = useState<number>(0);

	const isPremium = currentUser?.premium.is_active ?? false;

	const [layoutData, setLayoutData] = useState<DashboardLayoutDataV3>(() =>
		parseLayoutData(currentUser?.preferences.dashboard_layout ?? null, isPremium)
	);
	const savedLayoutRef = useRef<DashboardLayoutDataV3>(layoutData);
	const layoutInitializedRef = useRef(false);

	useEffect(() => {
		if (currentUser && !layoutInitializedRef.current) {
			layoutInitializedRef.current = true;
			const loaded = parseLayoutData(currentUser.preferences.dashboard_layout ?? null, isPremium);
			setLayoutData(loaded);
			savedLayoutRef.current = loaded;
		}
	}, [currentUser]);

	const {
		totalJobs,
		jobApplications,
		jobApplicationPending,
		activeApplications,
		needsChase,
		upcomingDeadlines,
		upcomingInterviews,
		pastInterviews,
		statusUpdates,
		upcomingDeadlinesTimeline,
		recentActivity,
		interviewRate,
		avgResponseTime,
		favouriteJobs,
	} = useDashboardData();

	const handleLayoutChange = (newLayout: Layout, allLayouts: ResponsiveLayouts): void => {
		if (!isEditMode) return;
		setLayoutData(
			(prev: DashboardLayoutDataV3): DashboardLayoutDataV3 => ({
				...prev,
				layout: (allLayouts.lg ?? newLayout) as LayoutItem[],
			})
		);
	};

	const handleSave = async (): Promise<void> => {
		setIsSaving(true);
		try {
			await updateCurrentUser({ preferences: { dashboard_layout: JSON.stringify(layoutData) } });
			savedLayoutRef.current = layoutData;
			setIsEditMode(false);
		} finally {
			setIsSaving(false);
		}
	};

	const handleCancel = (): void => {
		setLayoutData(savedLayoutRef.current);
		setIsEditMode(false);
	};

	const handleResetLayout = (): void => {
		void showConfirm({
			title: "Reset layout",
			message: "This will restore the default dashboard layout. Any custom arrangement will be lost.",
			confirmText: "Reset",
			onSuccess: async () => setLayoutData(getDefaultLayout(isPremium)),
		});
	};

	const handleAddWidget = (config: WidgetConfig): void => {
		const id: string = generateWidgetId();
		const def = getDefaultLayoutForConfig(config);
		setLayoutData((prev: DashboardLayoutDataV3): DashboardLayoutDataV3 => {
			const { x, y } = findFirstFit(prev.layout, def.w, def.h, 12);
			return {
				...prev,
				widgets: [...prev.widgets, { id, config }],
				layout: [...prev.layout, { ...def, i: id, x, y }],
			};
		});
	};

	const handleRemoveWidget = (widgetId: string): void => {
		void showDelete({
			title: "Remove widget",
			message: "Are you sure you want to remove this widget?",
			onSuccess: async (): Promise<void> =>
				setLayoutData(
					(prev: DashboardLayoutDataV3): DashboardLayoutDataV3 => ({
						...prev,
						widgets: prev.widgets.filter((w: WidgetInstance): boolean => w.id !== widgetId),
						layout: prev.layout.filter((l: LayoutItem): boolean => l.i !== widgetId),
					})
				),
		});
	};

	const handleUpdateWidgetConfig = (widgetId: string, newConfig: WidgetConfig): void => {
		setLayoutData(
			(prev: DashboardLayoutDataV3): DashboardLayoutDataV3 => ({
				...prev,
				widgets: prev.widgets.map(
					(w: WidgetInstance): WidgetInstance => (w.id === widgetId ? { ...w, config: newConfig } : w)
				),
			})
		);
	};

	const renderMetricWidget = (metric: string): React.ReactNode => {
		switch (metric) {
			case "total_jobs":
				return (
					<StatCard
						id="stat-card-total_jobs"
						name="Total Jobs"
						value={totalJobs}
						icon="briefcase"
						variant="primary"
						description="Jobs in your database"
					/>
				);
			case "applications":
				return (
					<StatCard
						id="stat-card-applications"
						name="Applications"
						value={jobApplications.length}
						icon="send"
						variant="success"
						description="Total applications sent"
					/>
				);
			case "pending":
				return (
					<StatCard
						id="stat-card-pending"
						name="Pending"
						value={jobApplicationPending.length}
						icon="clock"
						variant="warning"
						description="Applications awaiting response"
					/>
				);
			case "follow_up":
				return (
					<StatCard
						id="stat-card-follow_up"
						name="Need Follow-up"
						value={needsChase.length}
						icon="telephone"
						variant="danger"
						description="Applications requiring action"
					/>
				);
			case "active_applications":
				return (
					<StatCard
						id="stat-card-active_applications"
						name="Active Applications"
						value={activeApplications.length}
						icon="send-check"
						variant="info"
						description="Not yet rejected or withdrawn"
					/>
				);
			case "interview_rate":
				return (
					<StatCard
						id="stat-card-interview_rate"
						name="Interview Rate"
						value={`${interviewRate}%`}
						icon="person-check"
						variant="primary"
						description="Applications that led to an interview"
					/>
				);
			case "avg_response_time":
				return (
					<StatCard
						id="stat-card-avg_response_time"
						name="Avg. Response Time"
						value={`${avgResponseTime}d`}
						icon="hourglass-split"
						variant="secondary"
						description="Average days from application to first update"
					/>
				);
			default:
				return null;
		}
	};

	const renderTableWidget = (source: string): React.ReactNode => {
		switch (source) {
			case "follow_up":
				return (
					<DashboardCard
						id="table-card-follow_up"
						icon="telephone"
						title="Applications Requiring Follow-up"
						badgeValue={needsChase.length}
						isEmpty={needsChase.length === 0}
						emptyState={{
							icon: "telephone-x",
							title: "No follow-ups needed",
							description: "All your applications are up to date",
						}}
					>
						<JobsToChase data={needsChase} />
					</DashboardCard>
				);
			case "upcoming_deadlines":
				return (
					<DashboardCard
						id="table-card-upcoming_deadlines"
						icon="clock"
						title="Upcoming Deadlines"
						badgeValue={upcomingDeadlines.length}
						isEmpty={upcomingDeadlines.length === 0}
						emptyState={{
							icon: "calendar-check",
							title: "No upcoming deadlines",
							description: "You have no application deadlines approaching",
						}}
					>
						<UpcomingDeadlinesTable data={upcomingDeadlines} />
					</DashboardCard>
				);
			case "job_alerts":
				return (
					<DashboardCard
						id="table-card-job_alerts"
						icon={getEntityIcon("scrapedJob")}
						title="Job Alerts"
						subtitle="Jobs that you received from job boards"
						badgeValue={scrapedJobCount}
						path="/scraped-jobs"
						isEmpty={scrapedJobCount === 0}
						emptyState={{
							icon: "bell-slash",
							title: "No job alerts",
							description: "Job alerts from your scrapers will appear here",
						}}
					>
						<ScrapedJobsTable dashboardMode={true} onTotalCountChange={setScrapedJobCount} />
					</DashboardCard>
				);

			case "favourite_jobs":
				return (
					<DashboardCard
						id="table-card-favourite_jobs"
						icon="star"
						title="Favourite Jobs"
						badgeValue={favouriteJobs.length}
						isEmpty={favouriteJobs.length === 0}
						emptyState={{
							icon: "star",
							title: "No favourite jobs",
							description: "Mark jobs as favourite to pin them here",
						}}
					>
						<FavouriteJobsTable data={favouriteJobs} />
					</DashboardCard>
				);
			case "favourites":
				return (
					<DashboardCard
						id="table-card-favourites"
						icon="star-fill"
						title="Favourite Job Alerts"
						badgeValue={favouriteAlertCount}
						isEmpty={favouriteAlertCount === 0}
						emptyState={{
							icon: "star",
							title: "No favourite job alerts",
							description: "Create favourite filters to pin matching job alerts here",
						}}
					>
						<div
							style={{ paddingTop: "9px", paddingBottom: "18px", display: "flex", flex: 1, minHeight: 0 }}
						>
							<ScrapedJobsTable
								dashboardMode={true}
								favouritesOnly={true}
								onTotalCountChange={setFavouriteAlertCount}
							/>
						</div>
					</DashboardCard>
				);
			default:
				return null;
		}
	};

	const renderTimelineWidget = (feed: string): React.ReactNode => {
		switch (feed) {
			case "recent_activity":
				return (
					<ActivityFeedCard
						id="activity-card-recent_activity"
						icon="clock-history"
						title="Recent Activity"
						badgeValue={recentActivity.length}
						emptyIcon="inbox"
						emptyTitle="No recent activity"
						emptyDescription="Your recent activity will appear here"
						items={recentActivity}
						renderItem={renderRecentActivityItem}
					/>
				);
			case "upcoming_interviews":
				return (
					<ActivityFeedCard
						id="activity-card-upcoming_interviews"
						icon="calendar-event"
						title="Upcoming Interviews"
						badgeValue={upcomingInterviews.length}
						emptyIcon="calendar-x"
						emptyTitle="No upcoming interviews"
						emptyDescription="Your scheduled interviews will appear here"
						items={upcomingInterviews}
						renderItem={renderUpcomingInterviewItem}
					/>
				);
			case "past_interviews":
				return (
					<ActivityFeedCard
						id="activity-card-past_interviews"
						icon="calendar-check"
						title="Past Interviews"
						badgeValue={pastInterviews.length}
						emptyIcon="calendar-x"
						emptyTitle="No past interviews"
						emptyDescription="Your completed interviews will appear here"
						items={pastInterviews}
						renderItem={renderPastInterviewItem}
					/>
				);
			case "status_updates":
				return (
					<ActivityFeedCard
						id="activity-card-status_updates"
						icon="envelope-open"
						title="Status Updates"
						badgeValue={statusUpdates.length}
						emptyIcon="inbox"
						emptyTitle="No status updates"
						emptyDescription="Replies and notes on your applications will appear here"
						items={statusUpdates}
						renderItem={renderStatusUpdateItem}
					/>
				);
			case "upcoming_deadlines_timeline":
				return (
					<ActivityFeedCard
						id="activity-card-upcoming_deadlines_timeline"
						icon="alarm"
						title="Upcoming Deadlines"
						badgeValue={upcomingDeadlinesTimeline.length}
						emptyIcon="calendar-check"
						emptyTitle="No upcoming deadlines"
						emptyDescription="Approaching application deadlines will appear here"
						items={upcomingDeadlinesTimeline}
						renderItem={renderUpcomingDeadlineItem}
					/>
				);
			default:
				return null;
		}
	};

	const renderWidget = (config: WidgetConfig, widgetId: string): React.ReactNode => {
		switch (config.type) {
			case "metric":
				return renderMetricWidget(config.metric);
			case "table":
				return renderTableWidget(config.source);
			case "timeline":
				return renderTimelineWidget(config.feed);
			case "graph":
				return (
					<GraphWidget
						config={config}
						onConfigChange={(updated: GraphConfig): void => handleUpdateWidgetConfig(widgetId, updated)}
						isEditMode={isEditMode}
					/>
				);
		}
	};

	if (!currentUser) {
		return (
			<div className="dashboard-wrapper">
				<div className="dashboard-main" ref={containerRef as React.RefObject<HTMLDivElement>} />
			</div>
		);
	}

	const widgetIds = new Set(layoutData.widgets.map((w: WidgetInstance): string => w.id));
	const currentLayout: LayoutItem[] = layoutData.layout.filter((l: LayoutItem): boolean => widgetIds.has(l.i));

	return (
		<div className="dashboard-wrapper" data-loaded="true">
			<div className="dashboard-main" ref={containerRef as React.RefObject<HTMLDivElement>}>
				<ExtensionBanner />
				<div className={isEditMode ? "dashboard-edit-mode" : ""}>
					{mounted && (
						<ResponsiveGridLayout
							className="dashboard-grid"
							width={width}
							layouts={{ lg: currentLayout }}
							breakpoints={{ lg: TABLET_BREAKPOINT, sm: MOBILE_BREAKPOINT, xs: 0 }}
							cols={{ lg: 12, sm: 7, xs: 2 }}
							rowHeight={30}
							dragConfig={{ enabled: isEditMode, handle: ".drag-handle" }}
							resizeConfig={{ enabled: isEditMode, handles: ["sw", "nw", "se", "ne"] }}
							onLayoutChange={handleLayoutChange}
						>
							{layoutData.widgets.map(
								(widget: WidgetInstance): JSX.Element => (
									<div key={widget.id} className="dashboard-grid-item">
										{isEditMode && (
											<>
												<div className="drag-handle">
													<i className="bi bi-grip-horizontal"></i>
												</div>
												<button
													id={`widget-remove-btn-${widget.id}`}
													className="widget-remove-btn"
													onClick={(): void => handleRemoveWidget(widget.id)}
													title="Remove widget"
												>
													<i className="bi bi-x"></i>
												</button>
											</>
										)}
										<div className="grid-item-content">
											{renderWidget(widget.config, widget.id)}
										</div>
									</div>
								)
							)}
						</ResponsiveGridLayout>
					)}
				</div>
			</div>
			<DashboardToolbar
				isEditMode={isEditMode}
				isSaving={isSaving}
				onEdit={(): void => setIsEditMode(true)}
				onCancel={handleCancel}
				onSave={handleSave}
				onAddWidget={(): void => setShowWidgetPicker(true)}
				onReset={handleResetLayout}
			/>
			<WidgetPickerModal
				show={showWidgetPicker}
				onHide={(): void => setShowWidgetPicker(false)}
				onAddWidget={handleAddWidget}
				isPremium={isPremium}
				currentWidgets={layoutData.widgets}
			/>
		</div>
	);
};

export default Dashboard;
