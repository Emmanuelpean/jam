import React, { useEffect, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import { ResponsiveGridLayout, useContainerWidth, Layout, LayoutItem, ResponsiveLayouts } from "react-grid-layout";
import { useAuth } from "../../contexts/AuthContext";
import "./DashboardPage.scss";
import {
	EnrichedInterviewData,
	EnrichedJobApplicationUpdateData,
	EnrichedJobData,
} from "../../services/schemas/DataTables";
import JobsToChase from "../../components/DataTable/JobsToChase";
import UpcomingDeadlinesTable from "../../components/DataTable/UpcomingDeadlines";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { StatCard } from "./StatCard";
import { DashboardCard } from "./DashboardCard";
import {
	ActivityFeedCard,
	RecentActivity,
	renderRecentActivityItem,
	renderUpcomingInterviewItem,
} from "./ActivityFeed";
import ScrapedJobsTable from "../../components/DataTable/ScrapedJobTable";
import { scrapedJobApi } from "../../services/api/Services";
import { sortByKey } from "../../utils/Utils";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import {
	DashboardLayoutDataV2,
	WidgetConfig,
	WidgetInstance,
	generateWidgetId,
	getDefaultLayout,
	getDefaultLayoutsForConfig,
	parseLayoutData,
} from "./widgetRegistry";
import WidgetPickerModal from "./WidgetPickerModal";
import GraphWidget from "./GraphWidget";
import AlertModal, { AlertState } from "../../components/AlertModal/AlertModal";

const Dashboard: React.FC = () => {
	const dataContext: DataContextValue = useDataContext();
	const { token, currentUser, updateCurrentUser } = useAuth();
	const [scrapedJobCount, setScrapedJobCount] = useState<number>(0);
	const [isEditMode, setIsEditMode] = useState(false);
	const [showWidgetPicker, setShowWidgetPicker] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < 768);
	const [alertState, setAlertState] = useState<AlertState>({ show: false });

	const isPremium = currentUser?.premium.is_active ?? false;

	const { width, containerRef, mounted } = useContainerWidth();

	const [layoutData, setLayoutData] = useState<DashboardLayoutDataV2>(() =>
		parseLayoutData(currentUser?.preferences.dashboard_layout ?? null, isPremium)
	);
	const savedLayoutRef = useRef<DashboardLayoutDataV2>(layoutData);

	// Track small screen
	useEffect(() => {
		const handleResize = () => setIsSmallScreen(window.innerWidth < 768);
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

	// Fetch scraped job count
	useEffect(() => {
		if (token && isPremium) {
			scrapedJobApi.getCount(token).then((count) => {
				setScrapedJobCount(count.data.count);
			});
		}
	}, [token, isPremium]);

	if (!currentUser) {
		return null;
	}

	const now = new Date();

	const jobApplications: EnrichedJobData[] = dataContext.jobs.filter(
		(job: EnrichedJobData): Date | string | null | undefined => job.application_date || job.application_status
	);

	const jobApplicationPending: EnrichedJobData[] = jobApplications.filter(
		(job: EnrichedJobData): boolean | string | null | undefined =>
			job.application_status && !["rejected", "withdrawn"].includes(job.application_status)
	);

	const needsChase: EnrichedJobData[] = jobApplicationPending.filter(
		(job: EnrichedJobData) =>
			job.days_since_last_update &&
			job.days_since_last_update > currentUser.preferences.chase_threshold &&
			(!job.followup_snooze_datetime || job.followup_snooze_datetime <= now) &&
			job.application_status &&
			!["rejected", "offer", "withdrawn"].includes(job.application_status)
	);

	const thresholdDate = new Date(now.getTime() + currentUser.preferences.deadline_threshold * 24 * 60 * 60 * 1000);

	const upcomingDeadlines: EnrichedJobData[] = dataContext.jobs.filter(
		(job: EnrichedJobData) =>
			!job.application_date &&
			!job.application_status &&
			job.deadline &&
			new Date(job.deadline) > now &&
			new Date(job.deadline) <= thresholdDate
	);

	const upcomingInterviews: EnrichedInterviewData[] = sortByKey(
		dataContext.interviews.filter(
			(interview: EnrichedInterviewData): boolean | null | undefined => new Date(interview.date!) >= now
		),
		"date"
	);

	const allUpdates: RecentActivity[] = [];

	// Add job applications as "Application" updates
	jobApplications.forEach((job: EnrichedJobData): void => {
		if (job.application_date) {
			allUpdates.push({
				data: job,
				date: job.application_date,
				type: "Application",
				job_id: job.id,
			});
		}
	});

	// Add interviews as "Interview" updates
	dataContext.interviews.forEach((interview: EnrichedInterviewData): void => {
		if (new Date(interview.date) < now) {
			allUpdates.push({
				data: interview,
				date: interview.date,
				type: "Interview",
				job_id: interview.job_id,
			});
		}
	});

	// Add job application updates
	dataContext.jobApplicationUpdates.forEach((update: EnrichedJobApplicationUpdateData): void => {
		if (new Date(update.date) < now) {
			allUpdates.push({
				data: update,
				date: update.date,
				type: "Job Application Update",
				job_id: update.job_id,
			});
		}
	});

	allUpdates.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
	const recentActivity = allUpdates.slice(0, currentUser.preferences.update_limit);

	const handleUpdateWidgetConfig = (widgetId: string, newConfig: WidgetConfig) => {
		setLayoutData((prev) => ({
			...prev,
			widgets: prev.widgets.map((w) => (w.id === widgetId ? { ...w, config: newConfig } : w)),
		}));
	};

	// Widget renderers by type
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
						onConfigChange={(updated) => handleUpdateWidgetConfig(widgetId, updated)}
						isEditMode={isEditMode}
					/>
				);
		}
	};

	const renderMetricWidget = (metric: string): React.ReactNode => {
		switch (metric) {
			case "total_jobs":
				return (
					<StatCard
						name="Total Jobs"
						value={dataContext.jobs.length}
						icon="briefcase"
						variant="primary"
						description="Jobs in your database"
					/>
				);
			case "applications":
				return (
					<StatCard
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
						name="Need Follow-up"
						value={needsChase.length}
						icon="telephone"
						variant="danger"
						description="Applications requiring action"
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
						<div style={{ paddingTop: "10px", paddingBottom: "20px" }}>
							<ScrapedJobsTable />
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
			await updateCurrentUser({
				preferences: {
					dashboard_layout: JSON.stringify(layoutData),
				},
			});
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

	const handleReset = () => {
		const defaultLayout = getDefaultLayout(isPremium);
		setLayoutData(defaultLayout);
	};

	const handleAddWidget = (config: WidgetConfig) => {
		setLayoutData((prev) => {
			const id = generateWidgetId();
			const newWidget: WidgetInstance = { id, config };
			const defaults = getDefaultLayoutsForConfig(config);
			const newLayouts = { ...prev.layouts };

			for (const bp of ["lg", "md", "sm"] as const) {
				const items = newLayouts[bp];
				const maxY = items.length === 0 ? 0 : Math.max(...items.map((l) => l.y + l.h));
				newLayouts[bp] = [...items, { ...defaults[bp], i: id, y: maxY }];
			}

			return {
				...prev,
				widgets: [...prev.widgets, newWidget],
				layouts: newLayouts,
			};
		});
	};

	const confirmRemoveWidget = (widgetId: string) => {
		setAlertState({
			show: true,
			type: "danger",
			title: "Remove Widget",
			message: "Are you sure you want to remove this widget?",
			confirmText: "Remove",
			cancelText: "Cancel",
			onSuccess: () => {
				setLayoutData((prev) => ({
					...prev,
					widgets: prev.widgets.filter((w) => w.id !== widgetId),
					layouts: {
						lg: prev.layouts.lg.filter((l) => l.i !== widgetId),
						md: prev.layouts.md.filter((l) => l.i !== widgetId),
						sm: prev.layouts.sm.filter((l) => l.i !== widgetId),
					},
				}));
			},
		});
	};

	const widgetIds = new Set(layoutData.widgets.map((w) => w.id));
	const currentLayouts: ResponsiveLayouts = {
		lg: layoutData.layouts.lg.filter((l) => widgetIds.has(l.i)),
		md: layoutData.layouts.md.filter((l) => widgetIds.has(l.i)),
		sm: layoutData.layouts.sm.filter((l) => widgetIds.has(l.i)),
	};

	const hasChanges = JSON.stringify(layoutData) !== JSON.stringify(savedLayoutRef.current);
	const dragEnabled = isEditMode && !isSmallScreen;

	return (
		<div className="dashboard-wrapper">
			<div className="dashboard-main" ref={containerRef as React.RefObject<HTMLDivElement>}>
				<div className={isEditMode ? "dashboard-edit-mode" : ""}>
					{mounted && (
						<ResponsiveGridLayout
							className="dashboard-grid"
							width={width}
							layouts={currentLayouts}
							breakpoints={{ lg: 992, md: 768, sm: 0 }}
							cols={{ lg: 12, md: 12, sm: 12 }}
							rowHeight={30}
							margin={[16, 16]}
							dragConfig={{ enabled: dragEnabled, handle: ".drag-handle" }}
							resizeConfig={{ enabled: dragEnabled }}
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
												onClick={() => confirmRemoveWidget(widget.id)}
												title="Remove widget"
											>
												<i className="bi bi-trash3"></i>
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

			{!isSmallScreen && (
				<div className={`dashboard-right-sidebar ${isEditMode ? "expanded" : ""}`}>
					{isEditMode ? (
						<div className="sidebar-edit-controls">
							<Button
								variant="outline-secondary"
								size="sm"
								className="w-100"
								onClick={() => setShowWidgetPicker(true)}
							>
								<i className="bi bi-plus-circle me-1"></i>
								Add Widget
							</Button>
							<Button variant="outline-warning" size="sm" className="w-100" onClick={handleReset}>
								<i className="bi bi-arrow-counterclockwise me-1"></i>
								Reset
							</Button>
							<Button
								variant="secondary"
								size="sm"
								className="w-100"
								onClick={handleCancel}
							>
								<i className="bi bi-x-lg me-1"></i>
								Cancel
							</Button>
							<Button
								variant="primary"
								size="sm"
								className="w-100"
								onClick={handleSave}
								disabled={isSaving || !hasChanges}
							>
								<i className={`bi bi-${isSaving ? "hourglass-split" : "check-lg"} me-1`}></i>
								{isSaving ? "Saving..." : "Save"}
							</Button>
						</div>
					) : (
						<button
							className="sidebar-customize-btn"
							onClick={() => setIsEditMode(true)}
							title="Customize dashboard"
						>
							<i className="bi bi-grid"></i>
						</button>
					)}
				</div>
			)}

			<WidgetPickerModal
				show={showWidgetPicker}
				onHide={() => setShowWidgetPicker(false)}
				onAddWidget={handleAddWidget}
				isPremium={isPremium}
			/>

			<AlertModal alertState={alertState} hideAlert={() => setAlertState({ show: false })} />
		</div>
	);
};

export default Dashboard;
