import React, { useEffect, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import {
	ResponsiveGridLayout,
	useContainerWidth,
	Layout,
	LayoutItem,
	ResponsiveLayouts,
} from "react-grid-layout";
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
import ExtensionBanner from "./ExtensionBanner";
import {
	CARD_REGISTRY,
	DashboardLayoutData,
	getDefaultLayout,
	parseLayoutData,
} from "./cardRegistry";
import CardSelectorModal from "./CardSelectorModal";

const Dashboard: React.FC = () => {
	const dataContext: DataContextValue = useDataContext();
	const { token, currentUser, updateCurrentUser } = useAuth();
	const [scrapedJobCount, setScrapedJobCount] = useState<number>(0);
	const [isEditMode, setIsEditMode] = useState(false);
	const [showCardSelector, setShowCardSelector] = useState(false);
	const [isSaving, setIsSaving] = useState(false);
	const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < 768);

	const isPremium = currentUser?.premium.is_active ?? false;

	const { width, containerRef, mounted } = useContainerWidth();

	const [layoutData, setLayoutData] = useState<DashboardLayoutData>(() =>
		parseLayoutData(currentUser?.preferences.dashboard_layout ?? null, isPremium)
	);
	const savedLayoutRef = useRef<DashboardLayoutData>(layoutData);

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

	// Card renderers
	const cardRenderers: Record<string, () => React.ReactNode> = {
		"stat-total-jobs": () => (
			<StatCard
				name="Total Jobs"
				value={dataContext.jobs.length}
				icon="briefcase"
				variant="primary"
				description="Jobs in your database"
			/>
		),
		"stat-applications": () => (
			<StatCard
				name="Applications"
				value={jobApplications.length}
				icon="send"
				variant="success"
				description="Total applications sent"
			/>
		),
		"stat-pending": () => (
			<StatCard
				name="Pending"
				value={jobApplicationPending.length}
				icon="clock"
				variant="warning"
				description="Applications awaiting response"
			/>
		),
		"stat-follow-up": () => (
			<StatCard
				name="Need Follow-up"
				value={needsChase.length}
				icon="telephone"
				variant="danger"
				description="Applications requiring action"
			/>
		),
		"recent-activity": () => (
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
		),
		"follow-up-table": () => (
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
		),
		"upcoming-deadlines": () => (
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
		),
		"upcoming-interviews": () => (
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
		),
		"job-alerts": () => (
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
		),
	};

	const visibleCards = layoutData.visibleCards.filter((id) => {
		const def = CARD_REGISTRY.find((c) => c.id === id);
		if (!def) return false;
		if (def.premiumOnly && !isPremium) return false;
		return true;
	});

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

	const handleCardsChange = (newVisibleCards: string[]) => {
		setLayoutData((prev) => {
			const addedCards = newVisibleCards.filter((id) => !prev.visibleCards.includes(id));
			const newLayouts = { ...prev.layouts };

			// Add default layouts for newly added cards
			for (const cardId of addedCards) {
				const def = CARD_REGISTRY.find((c) => c.id === cardId);
				if (!def) continue;
				const maxY = (bp: "lg" | "md" | "sm") => {
					const items = newLayouts[bp];
					if (items.length === 0) return 0;
					return Math.max(...items.map((l) => l.y + l.h));
				};
				for (const bp of ["lg", "md", "sm"] as const) {
					newLayouts[bp] = [
						...newLayouts[bp],
						{ ...def.layouts[bp], y: maxY(bp) },
					];
				}
			}

			// Remove layouts for removed cards
			const visibleSet = new Set(newVisibleCards);
			for (const bp of ["lg", "md", "sm"] as const) {
				newLayouts[bp] = newLayouts[bp].filter((l) => visibleSet.has(l.i));
			}

			return {
				...prev,
				visibleCards: newVisibleCards,
				layouts: newLayouts,
			};
		});
	};

	const currentLayouts: ResponsiveLayouts = {
		lg: layoutData.layouts.lg.filter((l) => visibleCards.includes(l.i)),
		md: layoutData.layouts.md.filter((l) => visibleCards.includes(l.i)),
		sm: layoutData.layouts.sm.filter((l) => visibleCards.includes(l.i)),
	};

	const dragEnabled = isEditMode && !isSmallScreen;

	return (
		<>
			{/* Toolbar */}
			{!isSmallScreen && (
				<div className="d-flex justify-content-end mb-3 gap-2">
					{isEditMode ? (
						<>
							<Button
								variant="outline-secondary"
								size="sm"
								onClick={() => setShowCardSelector(true)}
							>
								<i className="bi bi-plus-circle me-1"></i>
								Add / Remove Cards
							</Button>
							<Button variant="outline-warning" size="sm" onClick={handleReset}>
								<i className="bi bi-arrow-counterclockwise me-1"></i>
								Reset
							</Button>
							<Button variant="outline-secondary" size="sm" onClick={handleCancel}>
								Cancel
							</Button>
							<Button variant="primary" size="sm" onClick={handleSave} disabled={isSaving}>
								{isSaving ? "Saving..." : "Save Layout"}
							</Button>
						</>
					) : (
						<Button
							variant="outline-secondary"
							size="sm"
							onClick={() => setIsEditMode(true)}
						>
							<i className="bi bi-grid me-1"></i>
							Customize
						</Button>
					)}
				</div>
			)}

			<div ref={containerRef as React.RefObject<HTMLDivElement>} className={isEditMode ? "dashboard-edit-mode" : ""}>
				{mounted && (
					<ResponsiveGridLayout
						className="dashboard-grid"
						width={width}
						layouts={currentLayouts}
						breakpoints={{ lg: 992, md: 768, sm: 0 }}
						cols={{ lg: 12, md: 12, sm: 12 }}
						rowHeight={60}
						margin={[16, 16]}
						dragConfig={{ enabled: dragEnabled, handle: ".drag-handle" }}
						resizeConfig={{ enabled: dragEnabled }}
						onLayoutChange={handleLayoutChange}
					>
						{visibleCards.map((cardId) => (
							<div key={cardId} className="dashboard-grid-item">
								{isEditMode && (
									<div className="drag-handle">
										<i className="bi bi-grip-horizontal"></i>
									</div>
								)}
								<div className="grid-item-content">
									{cardRenderers[cardId]?.()}
								</div>
							</div>
						))}
					</ResponsiveGridLayout>
				)}
			</div>

			<CardSelectorModal
				show={showCardSelector}
				onHide={() => setShowCardSelector(false)}
				visibleCards={layoutData.visibleCards}
				onCardsChange={handleCardsChange}
				isPremium={isPremium}
			/>
		</>
	);
};

export default Dashboard;
