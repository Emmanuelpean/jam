import React, { useEffect, useLayoutEffect, useRef, useState, JSX } from "react";
import { Button } from "react-bootstrap";
import { Tooltip, TITLE_TOOLTIP_DELAY } from "../../components/Tooltip/Tooltip";
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
import FailedScrapedJobsTable from "../../components/DataTable/FailedScrapedJobsTable";
import RecentUpdatesTable from "../../components/DataTable/RecentUpdatesTable";
import { getEntityIcon } from "../../components/rendering/view/Icons";
import {
	buildWidgetSettings,
	DashboardLayoutDataV3,
	generateWidgetId,
	getDefaultLayout,
	getDefaultLayoutForConfig,
	getWidgetSettingValue,
	GraphConfig,
	MapConfig,
	MetricConfig,
	MetricVariant,
	parseLayoutData,
	TableConfig,
	TimelineConfig,
	WidgetConfig,
	widgetHasSettings,
	WidgetInstance,
	WidgetSetting,
} from "./widgetRegistry";
import GraphWidget from "./GraphWidget";
import MapWidget from "./MapWidget";
import { ConfigurableDashboardCard, ConfigurableStatCard } from "./WidgetConfig";
import { useDashboardData } from "./useDashboardData";
import { useAlert } from "../../contexts/AlertContext";
import WidgetPickerModal from "./WidgetPickerModal";
import ExtensionBanner from "./ExtensionBanner";
import { DashboardToolbar } from "./DashboardToolbar";
import { MOBILE_BREAKPOINT, TABLET_BREAKPOINT } from "../../contexts/ViewportContext";

function findFirstFit(existing: LayoutItem[], w: number, h: number, cols: number): { x: number; y: number } {
	const maxY: number = existing.reduce((max: number, item: LayoutItem): number => Math.max(max, item.y + item.h), 0);
	for (let y = 0; y <= maxY; y++) {
		for (let x = 0; x <= cols - w; x++) {
			const overlaps: boolean = existing.some(
				(item: LayoutItem): boolean =>
					x < item.x + item.w && x + w > item.x && y < item.y + item.h && y + h > item.y
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
	const [debouncedWidth, setDebouncedWidth] = useState(width);
	const initialSyncDone = useRef(false);
	useEffect(() => {
		// First real measurement replaces the 1280 default — apply immediately, no debounce
		if (mounted && !initialSyncDone.current) {
			initialSyncDone.current = true;
			setDebouncedWidth(width);
			return;
		}
		if (!mounted) return;
		const timer = setTimeout(() => setDebouncedWidth(width), 50);
		return () => clearTimeout(timer);
	}, [width, mounted]);
	const [isEditMode, setIsEditMode] = useState(false);
	const [openConfigId, setOpenConfigId] = useState<string | null>(null);
	const [minEditHeight, setMinEditHeight] = useState(0);
	const gridWrapperRef = useRef<HTMLDivElement>(null);
	const badgeRectsRef = useRef<Map<string, DOMRect>>(new Map());

	useEffect(() => {
		if (!isEditMode) setOpenConfigId(null);
	}, [isEditMode]);

	// FLIP-animate the header count badges as they shift position when edit mode toggles.
	// "First" positions are captured at the moment the toggle is triggered (see captureBadgeRects),
	// while the DOM is still in its current, settled state — relying on positions recorded during an
	// earlier commit would be stale on the first toggle, before the grid layout has measured itself.
	useLayoutEffect(() => {
		const wrapper = gridWrapperRef.current;
		if (!wrapper) return;
		wrapper.querySelectorAll<HTMLElement>(".table-count-badge").forEach((badge: HTMLElement): void => {
			const first = badgeRectsRef.current.get(badge.id);
			if (!first) return;
			const last = badge.getBoundingClientRect();
			const dx = first.left - last.left;
			if (Math.abs(dx) > 1) {
				badge.style.transition = "none";
				badge.style.transform = `translateX(${dx}px)`;
				void badge.offsetWidth; // force reflow so the starting offset is applied
				badge.style.transition = "transform 0.25s ease";
				badge.style.transform = "";
			}
		});
		badgeRectsRef.current.clear();
	}, [isEditMode]);

	// Snapshot the current badge positions just before edit mode is toggled, so the FLIP effect above
	// has an accurate "first" frame to animate from.
	const captureBadgeRects = (): void => {
		const wrapper = gridWrapperRef.current;
		if (!wrapper) return;
		badgeRectsRef.current.clear();
		wrapper.querySelectorAll<HTMLElement>(".table-count-badge").forEach((badge: HTMLElement): void => {
			badgeRectsRef.current.set(badge.id, badge.getBoundingClientRect());
		});
	};

	useEffect(() => {
		if (!isEditMode) {
			setMinEditHeight(0);
			return;
		}
		const el = gridWrapperRef.current;
		if (!el) return;
		const ro = new ResizeObserver(() => {
			setMinEditHeight((prev) => Math.max(prev, el.scrollHeight));
		});
		ro.observe(el);
		return () => ro.disconnect();
	}, [isEditMode]);

	const [isSaving, setIsSaving] = useState(false);
	const [showWidgetPicker, setShowWidgetPicker] = useState(false);
	const [scrapedJobCount, setScrapedJobCount] = useState<number>(0);
	const [favouriteAlertCount, setFavouriteAlertCount] = useState<number>(0);
	const [errorJobCount, setErrorJobCount] = useState<number>(0);

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
		upcomingInterviews,
		pastInterviews,
		interviewRate,
		avgResponseTime,
		favouriteJobs,
		recentUpdates,
		getNeedsChase,
		getUpcomingDeadlines,
		getUpcomingDeadlinesTimeline,
		getRecentActivity,
		getStatusUpdates,
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
			captureBadgeRects();
			setIsEditMode(false);
		} finally {
			setIsSaving(false);
		}
	};

	const handleCancel = (): void => {
		setLayoutData(savedLayoutRef.current);
		captureBadgeRects();
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

	const renderMetricWidget = (
		config: MetricConfig,
		isEditMode: boolean,
		settings: WidgetSetting[],
		open: boolean
	): React.ReactNode => {
		const metric: MetricVariant = config.metric;
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
					<ConfigurableStatCard
						id="stat-card-follow_up"
						name="Need Follow-up"
						value={getNeedsChase(getWidgetSettingValue(config, "chaseThreshold")).length}
						icon="telephone"
						variant="danger"
						description="Applications requiring action"
						isEditMode={isEditMode}
						open={open}
						settings={settings}
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

	const renderTableWidget = (
		config: TableConfig,
		isEditMode: boolean,
		settings: WidgetSetting[],
		open: boolean
	): React.ReactNode => {
		const source = config.source;
		switch (source) {
			case "follow_up": {
				const needsChase = getNeedsChase(getWidgetSettingValue(config, "chaseThreshold"));
				return (
					<ConfigurableDashboardCard
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
						isEditMode={isEditMode}
						open={open}
						settings={settings}
					>
						<JobsToChase data={needsChase} />
					</ConfigurableDashboardCard>
				);
			}
			case "upcoming_deadlines": {
				const upcomingDeadlines = getUpcomingDeadlines(getWidgetSettingValue(config, "deadlineThreshold"));
				return (
					<ConfigurableDashboardCard
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
						isEditMode={isEditMode}
						open={open}
						settings={settings}
					>
						<UpcomingDeadlinesTable data={upcomingDeadlines} />
					</ConfigurableDashboardCard>
				);
			}
			case "job_alerts":
				return (
					<DashboardCard
						id="table-card-job_alerts"
						icon={getEntityIcon("scrapedJob")}
						title="Job Alerts"
						subtitle="Jobs that you received from job boards"
						badgeValue={scrapedJobCount}
						path="/job-alerts/jobs"
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
						<ScrapedJobsTable
							dashboardMode={true}
							favouritesOnly={true}
							onTotalCountChange={setFavouriteAlertCount}
						/>
					</DashboardCard>
				);
			case "error_jobs":
				return (
					<DashboardCard
						id="table-card-error_jobs"
						icon="exclamation-triangle"
						title="Failed Jobs"
						subtitle="Jobs that failed to be scraped or rated"
						badgeValue={errorJobCount}
						isEmpty={errorJobCount === 0}
						emptyState={{
							icon: "check-circle",
							title: "No failed jobs",
							description: "All your jobs have been scraped and rated successfully",
						}}
					>
						<FailedScrapedJobsTable dashboardMode={true} onTotalCountChange={setErrorJobCount} />
					</DashboardCard>
				);
			case "recent_updates":
				return (
					<DashboardCard
						id="table-card-recent_updates"
						icon="clock-history"
						title="Recent Updates"
						subtitle="Jobs with the most recent activity"
						badgeValue={recentUpdates.length}
						isEmpty={recentUpdates.length === 0}
						emptyState={{
							icon: "inbox",
							title: "No recent activity",
							description: "Jobs with interviews or application updates will appear here",
						}}
					>
						<RecentUpdatesTable data={recentUpdates} />
					</DashboardCard>
				);
			default:
				return null;
		}
	};

	const renderTimelineWidget = (
		config: TimelineConfig,
		isEditMode: boolean,
		settings: WidgetSetting[],
		open: boolean
	): React.ReactNode => {
		const feed = config.feed;
		switch (feed) {
			case "recent_activity": {
				const recentActivity = getRecentActivity(getWidgetSettingValue(config, "updateLimit"));
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
						isEditMode={isEditMode}
						open={open}
						settings={settings}
					/>
				);
			}
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
			case "status_updates": {
				const statusUpdates = getStatusUpdates(getWidgetSettingValue(config, "updateLimit"));
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
						isEditMode={isEditMode}
						open={open}
						settings={settings}
					/>
				);
			}
			case "upcoming_deadlines_timeline": {
				const upcomingDeadlinesTimeline = getUpcomingDeadlinesTimeline(
					getWidgetSettingValue(config, "deadlineThreshold")
				);
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
						isEditMode={isEditMode}
						open={open}
						settings={settings}
					/>
				);
			}
			default:
				return null;
		}
	};

	const renderWidget = (config: WidgetConfig, widgetId: string): React.ReactNode => {
		const settings: WidgetSetting[] = buildWidgetSettings(config, (updated: WidgetConfig): void =>
			handleUpdateWidgetConfig(widgetId, updated)
		);
		const open: boolean = openConfigId === widgetId;
		switch (config.type) {
			case "metric":
				return renderMetricWidget(config, isEditMode, settings, open);
			case "table":
				return renderTableWidget(config, isEditMode, settings, open);
			case "timeline":
				return renderTimelineWidget(config, isEditMode, settings, open);
			case "graph":
				return (
					<GraphWidget
						config={config}
						onConfigChange={(updated: GraphConfig): void => handleUpdateWidgetConfig(widgetId, updated)}
						isEditMode={isEditMode}
					/>
				);
			case "map":
				return (
					<MapWidget
						config={config as MapConfig}
						onConfigChange={(updated: MapConfig): void => handleUpdateWidgetConfig(widgetId, updated)}
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

	const makeFullWidthLayout = (layout: LayoutItem[], cols: number): LayoutItem[] => {
		const sorted = [...layout].sort((a, b) => (a.y !== b.y ? a.y - b.y : a.x - b.x));
		let y = 0;
		return sorted.map((item) => {
			const newItem = { ...item, x: 0, w: cols, y };
			y += item.h;
			return newItem;
		});
	};

	const makePackedLayout = (layout: LayoutItem[], cols: number): LayoutItem[] => {
		const sorted = [...layout].sort((a, b) => (a.y !== b.y ? a.y - b.y : a.x - b.x));

		// Step 1: greedy row packing
		const rows: LayoutItem[][] = [];
		let curRow: LayoutItem[] = [];
		let curX = 0;
		let curY = 0;
		let rowH = 0;
		for (const item of sorted) {
			const w = Math.min(Math.max(item.minW ?? 1, item.w), cols);
			if (curX + w > cols) {
				rows.push(curRow);
				curRow = [];
				curY += rowH;
				curX = 0;
				rowH = 0;
			}
			curRow.push({ ...item, x: curX, y: curY, w });
			curX += w;
			rowH = Math.max(rowH, item.h);
		}
		if (curRow.length) rows.push(curRow);

		// Step 2: expand each row to fill cols exactly
		return rows.flatMap((row) => {
			const used = row.reduce((s, it) => s + it.w, 0);
			const remaining = cols - used;
			const extra = Math.floor(remaining / row.length);
			const leftover = remaining - extra * row.length;
			let x = 0;
			return row.map((item, i) => {
				const w = item.w + extra + (i === row.length - 1 ? leftover : 0);
				const out = { ...item, x, w };
				x += w;
				return out;
			});
		});
	};

	return (
		<div className="dashboard-wrapper" data-loaded="true">
			<div
				id="dashboard-main"
				className="dashboard-main"
				data-tour="dashboard-stats"
				ref={containerRef as React.RefObject<HTMLDivElement>}
			>
				<ExtensionBanner />
				<div
					ref={gridWrapperRef}
					className={isEditMode ? "dashboard-edit-mode" : ""}
					style={isEditMode && minEditHeight > 0 ? { minHeight: minEditHeight } : undefined}
				>
					{mounted && (
						<ResponsiveGridLayout
							className="dashboard-grid"
							width={debouncedWidth}
							layouts={{
								lg: currentLayout,
								sm: makePackedLayout(currentLayout, 6),
								xs: makeFullWidthLayout(currentLayout, 2),
							}}
							breakpoints={{ lg: TABLET_BREAKPOINT, sm: MOBILE_BREAKPOINT, xs: 0 }}
							cols={{ lg: 12, sm: 6, xs: 2 }}
							rowHeight={30}
							containerPadding={[0, 0]}
							dragConfig={{ enabled: isEditMode, handle: ".drag-handle" }}
							resizeConfig={{ enabled: isEditMode, handles: ["sw", "nw", "se", "ne"] }}
							onLayoutChange={handleLayoutChange}
						>
							{layoutData.widgets.map(
								(widget: WidgetInstance): JSX.Element => (
									<div key={widget.id} className="dashboard-grid-item">
										{isEditMode && (
											<div className="drag-handle">
												<i className="bi bi-grip-horizontal"></i>
											</div>
										)}
										{widgetHasSettings(widget.config) && (
											<Tooltip content="Configure widget" delay={TITLE_TOOLTIP_DELAY}>
												<Button
													id={`widget-config-btn-${widget.id}`}
													className="widget-config-btn"
													variant="outline-primary"
													active={openConfigId === widget.id}
													onClick={(): void =>
														setOpenConfigId((prev: string | null): string | null =>
															prev === widget.id ? null : widget.id
														)
													}
												>
													<i className="bi bi-gear"></i>
												</Button>
											</Tooltip>
										)}
										<Tooltip content="Remove widget" delay={TITLE_TOOLTIP_DELAY}>
											<Button
												id={`widget-remove-btn-${widget.id}`}
												className="widget-remove-btn"
												variant="outline-danger"
												onClick={(): void => handleRemoveWidget(widget.id)}
											>
												<i className="bi bi-x"></i>
											</Button>
										</Tooltip>
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
				onEdit={(): void => {
					captureBadgeRects();
					setIsEditMode(true);
				}}
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
