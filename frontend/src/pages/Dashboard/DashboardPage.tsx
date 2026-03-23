import React, { useEffect, useRef, useState } from "react";
import { Layout, LayoutItem, ResponsiveGridLayout, ResponsiveLayouts, useContainerWidth } from "react-grid-layout";
import { useAuth } from "../../contexts/AuthContext";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import "./DashboardPage.scss";
import JobsToChase from "../../components/DataTable/JobsToChase";
import UpcomingDeadlinesTable from "../../components/DataTable/UpcomingDeadlines";
import { StatCard } from "./StatCard";
import { DashboardCard } from "./DashboardCard";
import { ActivityFeedCard, renderRecentActivityItem, renderUpcomingInterviewItem } from "./ActivityFeed";
import ScrapedJobsTable from "../../components/DataTable/ScrapedJobTable";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import {
	DashboardLayoutDataV2,
	generateWidgetId,
	getDefaultLayout,
	getDefaultLayoutsForConfig,
	parseLayoutData,
	WidgetConfig,
} from "./widgetRegistry";
import GraphWidget from "./GraphWidget";
import FavouriteJobWidget from "./FavouriteJobWidget";
import { useDashboardData } from "./useDashboardData";
import { useAlert } from "../../contexts/AlertContext";
import WidgetPickerModal from "./WidgetPickerModal";
import ExtensionBanner from "./ExtensionBanner";
import { DashboardToolbar } from "./DashboardToolbar";

const Dashboard: React.FC = () => {
	const { currentUser, updateCurrentUser } = useAuth();
	const { showConfirm, showDelete } = useAlert();
	const { width, containerRef, mounted } = useContainerWidth({ measureBeforeMount: true });
	const [isEditMode, setIsEditMode] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [showWidgetPicker, setShowWidgetPicker] = useState(false);
	const [scrapedJobCount, setScrapedJobCount] = useState<number>(0);

	const isPremium = currentUser?.premium.is_active ?? false;

	const [layoutData, setLayoutData] = useState<DashboardLayoutDataV2>(() =>
		parseLayoutData(currentUser?.preferences.dashboard_layout ?? null, isPremium)
	);
	const savedLayoutRef = useRef<DashboardLayoutDataV2>(layoutData);
	const layoutInitializedRef = useRef(false);

	useEffect(() => {
		if (currentUser && !layoutInitializedRef.current) {
			layoutInitializedRef.current = true;
			const loaded = parseLayoutData(currentUser.preferences.dashboard_layout ?? null, isPremium);
			setLayoutData(loaded);
			savedLayoutRef.current = loaded;
		}
	}, [currentUser]);

	const { totalJobs, jobApplications, jobApplicationPending, offersReceived, activeApplications, needsChase, upcomingDeadlines, upcomingInterviews, recentActivity, interviewRate, offerRate, avgResponseTime } =
		useDashboardData();

	const handleLayoutChange = (_currentLayout: Layout, allLayouts: ResponsiveLayouts) => {
		if (!isEditMode) return;
		setLayoutData((prev) => ({
			...prev,
			layouts: {
				lg: (allLayouts.lg as LayoutItem[] | undefined) || prev.layouts.lg,
				md: (allLayouts.md as LayoutItem[] | undefined) || prev.layouts.md,
				sm: (allLayouts.sm as LayoutItem[] | undefined) || prev.layouts.sm,
			},
		}));
	};

	const handleSave = async () => {
		setIsSaving(true);
		try {
			await updateCurrentUser({ preferences: { dashboard_layout: JSON.stringify(layoutData) } });
			savedLayoutRef.current = layoutData;
			setIsEditMode(false);
		} finally {
			setIsSaving(false);
		}
	};

	const handleCancel = () => {
		setLayoutData(savedLayoutRef.current);
		setIsEditMode(false);
	};

	const handleResetLayout = () => {
		void showConfirm({
			title: "Reset layout",
			message: "This will restore the default dashboard layout. Any custom arrangement will be lost.",
			confirmText: "Reset",
			onSuccess: async () => setLayoutData(getDefaultLayout(isPremium)),
		});
	};

	const handleAddWidget = (config: WidgetConfig) => {
		const id = generateWidgetId();
		const defaultLayouts = getDefaultLayoutsForConfig(config);
		setLayoutData((prev) => ({
			...prev,
			widgets: [...prev.widgets, { id, config }],
			layouts: {
				lg: [...prev.layouts.lg, { ...defaultLayouts.lg, i: id }],
				md: [...prev.layouts.md, { ...defaultLayouts.md, i: id }],
				sm: [...prev.layouts.sm, { ...defaultLayouts.sm, i: id }],
			},
		}));
	};

	const handleRemoveWidget = (widgetId: string) => {
		void showDelete({
			title: "Remove widget",
			message: "Are you sure you want to remove this widget?",
			onSuccess: async () =>
				setLayoutData((prev) => ({
					...prev,
					widgets: prev.widgets.filter((w) => w.id !== widgetId),
					layouts: {
						lg: prev.layouts.lg.filter((l) => l.i !== widgetId),
						md: prev.layouts.md.filter((l) => l.i !== widgetId),
						sm: prev.layouts.sm.filter((l) => l.i !== widgetId),
					},
				})),
		});
	};

	const handleUpdateWidgetConfig = (widgetId: string, newConfig: WidgetConfig) => {
		setLayoutData((prev) => ({
			...prev,
			widgets: prev.widgets.map((w) => (w.id === widgetId ? { ...w, config: newConfig } : w)),
		}));
	};

	const renderMetricWidget = (metric: string): React.ReactNode => {
		switch (metric) {
			case "total_jobs":
				return <StatCard name="Total Jobs" value={totalJobs} icon="briefcase" variant="primary" description="Jobs in your database" />;
			case "applications":
				return <StatCard name="Applications" value={jobApplications.length} icon="send" variant="success" description="Total applications sent" />;
			case "pending":
				return <StatCard name="Pending" value={jobApplicationPending.length} icon="clock" variant="warning" description="Applications awaiting response" />;
			case "follow_up":
				return <StatCard name="Need Follow-up" value={needsChase.length} icon="telephone" variant="danger" description="Applications requiring action" />;
			case "offers_received":
				return <StatCard name="Offers Received" value={offersReceived.length} icon="trophy" variant="success" description="Applications that resulted in an offer" />;
			case "active_applications":
				return <StatCard name="Active Applications" value={activeApplications.length} icon="send-check" variant="info" description="Not yet rejected or withdrawn" />;
			case "interview_rate":
				return <StatCard name="Interview Rate" value={`${interviewRate}%`} icon="person-check" variant="primary" description="Applications that led to an interview" />;
			case "offer_rate":
				return <StatCard name="Offer Rate" value={`${offerRate}%`} icon="patch-check" variant="success" description="Applications that resulted in an offer" />;
			case "avg_response_time":
				return <StatCard name="Avg. Response Time" value={`${avgResponseTime}d`} icon="hourglass-split" variant="secondary" description="Average days from application to first update" />;
			default:
				return null;
		}
	};

	const renderTableWidget = (source: string): React.ReactNode => {
		switch (source) {
			case "follow_up":
				return (
					<DashboardCard
						icon="telephone"
						title="Applications Requiring Follow-up"
						badgeValue={needsChase.length}
						isEmpty={needsChase.length === 0}
						emptyState={{ icon: "telephone-x", title: "No follow-ups needed", description: "All your applications are up to date" }}
					>
						<JobsToChase data={needsChase} />
					</DashboardCard>
				);
			case "upcoming_deadlines":
				return (
					<DashboardCard
						icon="clock"
						title="Upcoming Deadlines"
						badgeValue={upcomingDeadlines.length}
						isEmpty={upcomingDeadlines.length === 0}
						emptyState={{ icon: "calendar-check", title: "No upcoming deadlines", description: "You have no application deadlines approaching" }}
					>
						<UpcomingDeadlinesTable data={upcomingDeadlines} />
					</DashboardCard>
				);
			case "job_alerts":
				return (
					<DashboardCard
						icon={getEntityIcon("scrapedJob")}
						title="Job Alerts"
						subtitle="Jobs that you received from job boards"
						badgeValue={scrapedJobCount}
						path="/scraped-jobs"
						isEmpty={scrapedJobCount === 0}
						emptyState={{ icon: "bell-slash", title: "No job alerts", description: "Job alerts from your scrapers will appear here" }}
					>
						<div style={{ paddingTop: "9px", paddingBottom: "18px", display: "flex", flex: 1, minHeight: 0 }}>
							<ScrapedJobsTable onTotalCountChange={setScrapedJobCount} />
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
			case "card":
				return <FavouriteJobWidget />;
			case "graph":
				return (
					<GraphWidget
						config={config}
						onConfigChange={(updated) => handleUpdateWidgetConfig(widgetId, updated)}
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

	const widgetIds = new Set(layoutData.widgets.map((w) => w.id));
	const currentLayouts: ResponsiveLayouts = {
		lg: layoutData.layouts.lg.filter((l) => widgetIds.has(l.i)),
		md: layoutData.layouts.md.filter((l) => widgetIds.has(l.i)),
		sm: layoutData.layouts.sm.filter((l) => widgetIds.has(l.i)),
	};

	return (
		<div className="dashboard-wrapper">
			<div className="dashboard-main" ref={containerRef as React.RefObject<HTMLDivElement>}>
				<ExtensionBanner />
				<div className={isEditMode ? "dashboard-edit-mode" : ""}>
					{mounted && (
						<ResponsiveGridLayout
							className="dashboard-grid"
							width={width}
							layouts={currentLayouts}
							breakpoints={{ lg: 992, md: 768, sm: 0 }}
							cols={{ lg: 12, md: 12, sm: 12 }}
							rowHeight={30}
							dragConfig={{ enabled: isEditMode, handle: ".drag-handle" }}
							resizeConfig={{ enabled: isEditMode, handles: ["sw", "nw", "se", "ne"] }}
							onLayoutChange={handleLayoutChange}
						>
							{layoutData.widgets.map((widget) => (
								<div key={widget.id} className="dashboard-grid-item">
									{isEditMode && (
										<>
											<div className="drag-handle">
												<i className="bi bi-grip-horizontal"></i>
											</div>
											<button
												className="widget-remove-btn"
												onClick={() => handleRemoveWidget(widget.id)}
												title="Remove widget"
											>
												<i className="bi bi-x"></i>
											</button>
										</>
									)}
									<div className="grid-item-content">{renderWidget(widget.config, widget.id)}</div>
								</div>
							))}
						</ResponsiveGridLayout>
					)}
				</div>
			</div>
			<DashboardToolbar
				isEditMode={isEditMode}
				isSaving={isSaving}
				onEdit={() => setIsEditMode(true)}
				onCancel={handleCancel}
				onSave={handleSave}
				onAddWidget={() => setShowWidgetPicker(true)}
				onReset={handleResetLayout}
			/>
			<WidgetPickerModal
				show={showWidgetPicker}
				onHide={() => setShowWidgetPicker(false)}
				onAddWidget={handleAddWidget}
				isPremium={isPremium}
			/>
		</div>
	);
};

export default Dashboard;
