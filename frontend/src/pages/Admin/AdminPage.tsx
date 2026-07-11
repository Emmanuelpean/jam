import React, { JSX, ReactNode, useEffect, useMemo, useState } from "react";
import { Col, Modal, Row } from "react-bootstrap";
import PageHeader from "../PageHeader/PageHeader";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";
import { useDataContext } from "../../contexts/DataContext";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { useSchedulerStatus } from "../../hooks/useSchedulerStatus";
import {
	BaseServiceApi,
	jobRatingServiceLogApi,
	jobRatingServiceRunnerApi,
	jobScraperServiceApi,
	jobScraperServiceLogApi,
	SchedulerStatus,
	ServiceStatus,
	ServiceUpdatePayload,
} from "../../services/api/Services";
import { providerMonitoringApi, providerMonitoringRunnerApi } from "../../services/api/ProviderMonitoring";
import { failureColor, serviceEnabledLabel, successColor } from "../Services/ServiceUtils";
import { ServiceConfigField, ServiceStatusControl } from "../Services/ServiceStatusControl";
import { ServiceFilterSlotContext } from "../Services/ServiceFilterSlot";
import { formatDuration } from "../../utils/TimeUtils";
import { UserData } from "../../services/schemas/Core";
import { Sparkline, SparklinePoint } from "../../components/Chart/Sparkline";
import JamModal from "../../components/JamModal/JamModal";
import { UsersPage } from "./UsersPage";
import { AppSettingsPage } from "./AppSettingsPage";
import EmailTemplatesPage from "./EmailTemplatesPage";
import JobScrapingPage from "../Services/JobScrapingPage";
import JobRatingPage from "../Services/JobRatingPage";
import SchedulerPage from "../Services/SchedulerPage";
import UsagePage from "./UsagePage";
import "../Services/Service.scss";
import "./AdminPage.scss";

type AdminPageKey = "users" | "settings" | "email" | "scraping" | "rating" | "usage" | "scheduler";

const ADMIN_PAGES: Record<AdminPageKey, { title: string; icon: string; render: () => JSX.Element }> = {
	users: { title: "Users", icon: getTableIcon("Users"), render: () => <UsersPage /> },
	settings: { title: "Settings", icon: getTableIcon("Settings"), render: () => <AppSettingsPage /> },
	email: { title: "Email Templates", icon: getTableIcon("Email Templates"), render: () => <EmailTemplatesPage /> },
	scraping: {
		title: "Job Scraping",
		icon: getTableIcon("Job Scraping Dashboard"),
		render: () => <JobScrapingPage />,
	},
	rating: { title: "Job Rating", icon: getTableIcon("Job Rating Dashboard"), render: () => <JobRatingPage /> },
	usage: {
		title: "Provider Monitoring",
		icon: getTableIcon("ESM"),
		render: () => <UsagePage />,
	},
	scheduler: { title: "Service Scheduler", icon: "clock-history", render: () => <SchedulerPage /> },
};

interface ServiceControlConfig {
	ariaLabel: string;
	configFields: ServiceConfigField[];
	api: BaseServiceApi;
	buildUpdate?: (values: Record<string, number>) => ServiceUpdatePayload;
}

const SERVICE_CONTROLS: Partial<Record<AdminPageKey, ServiceControlConfig>> = {
	scraping: {
		ariaLabel: "Job scraping service controls",
		api: jobScraperServiceApi,
		configFields: [
			{
				name: "period_hours",
				label: "Scraping Period",
				help: "Time between scraping runs.",
				unit: "Hour(s)",
				getValue: (s) => s.run_period_hours || 0,
			},
			{
				name: "min_timedelta_days",
				label: "Min Time Delta",
				help: "Minimum number of days back to scrape emails for each run.",
				unit: "Day(s)",
				getValue: (s) => s.parameters?.min_timedelta_days || 0,
			},
			{
				name: "max_timedelta_days",
				label: "Max Time Delta",
				help: "Maximum number of days back to scrape emails (used to catch up after downtime).",
				unit: "Day(s)",
				getValue: (s) => s.parameters?.max_timedelta_days || 0,
			},
		],
		buildUpdate: (v) => ({
			run_period_hours: v.period_hours,
			parameters: { min_timedelta_days: v.min_timedelta_days, max_timedelta_days: v.max_timedelta_days },
		}),
	},
	rating: {
		ariaLabel: "Job rating service controls",
		api: jobRatingServiceRunnerApi,
		configFields: [
			{
				name: "period_hours",
				label: "Rating Period",
				help: "Time between rating runs.",
				unit: "Hour(s)",
				getValue: (s) => s.run_period_hours || 0,
			},
		],
		buildUpdate: (v) => ({ run_period_hours: v.period_hours }),
	},
	usage: {
		ariaLabel: "Monitoring service controls",
		api: providerMonitoringRunnerApi,
		configFields: [],
	},
};

// Spend services bill in USD, Stripe income is in GBP. Fixed rate used to express the
// net balance in a single currency (GBP), matching UsagePage.
const USD_TO_GBP = 0.79;

const toIsoDate = (d: Date): string => d.toISOString().slice(0, 10);

const formatMoney = (value: number, prefix: string): string => `${prefix}${value.toFixed(2)}`;

// Window covered by the per-service card graphs.
const RANGE_DAYS = 30;

// The trailing N calendar days (UTC) as YYYY-MM-DD, oldest first — the buckets the
// card graphs aggregate into.
const lastNDays = (n: number): string[] => {
	const days: string[] = [];
	const today = new Date();
	for (let i = n - 1; i >= 0; i--) {
		const d = new Date(today);
		d.setUTCDate(today.getUTCDate() - i);
		days.push(d.toISOString().slice(0, 10));
	}
	return days;
};

// Sum a per-run metric into one point per day over the window.
const dailySeriesFromLogs = <T extends { run_datetime: Date }>(
	logs: T[],
	getValue: (log: T) => number
): SparklinePoint[] => {
	const totals = new Map<string, number>(lastNDays(RANGE_DAYS).map((d) => [d, 0]));
	logs.forEach((log: T): void => {
		const day: string = new Date(log.run_datetime).toISOString().slice(0, 10);
		if (totals.has(day)) totals.set(day, totals.get(day)! + getValue(log));
	});
	return Array.from(totals, ([day, y]): SparklinePoint => ({ x: new Date(`${day}T00:00:00Z`), y }));
};

// Net balance per day = Stripe net (GBP) minus spend (USD → GBP), over the window.
const dailyBalanceSeries = (
	spend: { date: string; usage_usd: number }[],
	stripe: { date: string; net_gbp: number }[]
): SparklinePoint[] => {
	const days: string[] = lastNDays(RANGE_DAYS);
	const spendByDay = new Map<string, number>(days.map((d) => [d, 0]));
	spend.forEach((r): void => {
		if (spendByDay.has(r.date)) spendByDay.set(r.date, spendByDay.get(r.date)! + r.usage_usd);
	});
	const netByDay = new Map<string, number>(days.map((d) => [d, 0]));
	stripe.forEach((r): void => {
		if (netByDay.has(r.date)) netByDay.set(r.date, r.net_gbp);
	});
	return days.map(
		(d: string): SparklinePoint => ({
			x: new Date(`${d}T00:00:00Z`),
			y: (netByDay.get(d) ?? 0) - (spendByDay.get(d) ?? 0) * USD_TO_GBP,
		})
	);
};

interface AdminCardProps {
	id?: string;
	title: string;
	icon: string;
	onClick: () => void;
	children: ReactNode;
	headerExtra?: ReactNode;
}

const AdminCard = ({ id, title, icon, onClick, children, headerExtra }: AdminCardProps): JSX.Element => {
	return (
		<div
			id={id}
			className="status-card admin-card h-100"
			role="button"
			tabIndex={0}
			onClick={onClick}
			onKeyDown={(e: React.KeyboardEvent): void => {
				if (e.key === "Enter" || e.key === " ") {
					e.preventDefault();
					onClick();
				}
			}}
		>
			<div className="history-chart-header d-flex justify-content-between align-items-center">
				<h2 className="card-title">
					<i className={`bi bi-${icon} me-2`} />
					{title}
				</h2>
				{headerExtra ?? <i className="bi bi-chevron-right admin-card-arrow" />}
			</div>
			<div className="admin-card-body">{children}</div>
		</div>
	);
};

interface StatRow {
	label: string;
	value: ReactNode;
}

const StatList = ({
	primary,
	caption,
	rows = [],
}: {
	primary?: ReactNode;
	caption?: string;
	rows?: StatRow[];
}): JSX.Element => (
	<>
		{primary !== undefined && <div className="admin-card-primary">{primary}</div>}
		{caption && <div className="admin-card-caption">{caption}</div>}
		{rows.map(
			(r: StatRow): JSX.Element => (
				<div key={String(r.label)} className="d-flex justify-content-between admin-card-stat">
					<span className="text-muted">{r.label}</span>
					<span className="fw-bold">{r.value}</span>
				</div>
			)
		)}
	</>
);

// The service runner + service status, each with its status icon beside the text.
// The countdown to the next run (while the runner is idle between runs) sits next
// to the service status.
const ServiceStatusBody = ({
	status,
	remainingTime,
}: {
	status: ServiceStatus | null;
	remainingTime: number | null;
}): JSX.Element => {
	const enabled: boolean = !!status?.is_enabled;
	const running: boolean = !!status?.is_running;
	const showCountdown: boolean = enabled && !running && remainingTime !== null;
	return (
		<StatList
			rows={[
				{
					label: "Service",
					value: (
						<span className="admin-card-status-value">
							<i
								className={`bi bi-cpu-fill service-status-icon service-status-icon--runner ${enabled ? "is-on" : "is-off"}`}
							/>
							{serviceEnabledLabel(status)}
						</span>
					),
				},
				{
					label: "Run",
					value: (
						<span className="admin-card-status-value">
							<i
								className={`bi bi-activity service-status-icon ${running ? "is-on is-running" : "is-off"}`}
							/>
							{running ? "In progress" : "Idle"}
							{showCountdown && (
								<span className="service-next-run">
									<i className="bi bi-hourglass-split me-1" />
									{formatDuration(remainingTime)}
								</span>
							)}
						</span>
					),
				},
			]}
		/>
	);
};

const SchedulerStatusBody = ({ status }: { status: SchedulerStatus | null }): JSX.Element => {
	const running: boolean = !!status?.running;
	return (
		<StatList
			rows={[
				{
					label: "Scheduler",
					value: (
						<span className="admin-card-status-value">
							<i
								className={`bi bi-activity service-status-icon ${running ? "is-on is-running" : "is-off"}`}
							/>
							{status ? (running ? "Running" : "Stopped") : "…"}
						</span>
					),
				},
				{ label: "Poll interval", value: status ? `${status.poll_interval_seconds}s` : "…" },
			]}
		/>
	);
};

const isActiveUser = (user: UserData): boolean => {
	if (!user.last_login) return false;
	const monthAgo: number = Date.now() - 30 * 24 * 60 * 60 * 1000;
	return new Date(user.last_login).getTime() >= monthAgo;
};

const AdminPage = (): JSX.Element => {
	const { token } = useAuth();
	const { users, settings, emailTemplates } = useDataContext();
	const [openPage, setOpenPage] = useState<AdminPageKey | null>(null);
	const [showModal, setShowModal] = useState<boolean>(false);
	const [filterSlot, setFilterSlot] = useState<HTMLDivElement | null>(null);

	const openModal = (key: AdminPageKey): void => {
		setOpenPage(key);
		setShowModal(true);
	};

	const scraping = useServiceRunnerStatus(jobScraperServiceApi);
	const rating = useServiceRunnerStatus(jobRatingServiceRunnerApi);
	const monitoring = useServiceRunnerStatus(providerMonitoringRunnerApi);
	const scheduler = useSchedulerStatus();

	const pageStatus: Partial<Record<AdminPageKey, ReturnType<typeof useServiceRunnerStatus>>> = {
		scraping,
		rating,
		usage: monitoring,
	};

	const [scrapedSeries, setScrapedSeries] = useState<SparklinePoint[]>([]);
	const [ratedSeries, setRatedSeries] = useState<SparklinePoint[]>([]);
	const [balanceSeries, setBalanceSeries] = useState<SparklinePoint[]>([]);
	const [sparklinesLoading, setSparklinesLoading] = useState<boolean>(true);

	useEffect((): (() => void) | void => {
		if (!token) return;
		let cancelled = false;
		const load = async (): Promise<void> => {
			setSparklinesLoading(true);
			try {
				const end = new Date();
				const start = new Date(end.getTime() - (RANGE_DAYS - 1) * 24 * 60 * 60 * 1000);
				const isoRange = { start_date: toIsoDate(start), end_date: toIsoDate(end) };
				const dtRange = { start_date: start.toISOString(), end_date: end.toISOString() };
				const [scrapeLogs, ratingLogs, anthropic, apify, brightdata, stripe] = await Promise.all([
					jobScraperServiceLogApi.getAll(token, dtRange),
					jobRatingServiceLogApi.getAll(token, dtRange),
					providerMonitoringApi.getAnthropicHistory(isoRange, token),
					providerMonitoringApi.getApifyHistory(isoRange, token),
					providerMonitoringApi.getBrightdataHistory(isoRange, token),
					providerMonitoringApi.getStripeHistory(isoRange, token),
				]);
				if (cancelled) return;
				setScrapedSeries(dailySeriesFromLogs(scrapeLogs.data, (l) => l.job_scrape_succeeded_n));
				setRatedSeries(dailySeriesFromLogs(ratingLogs.data, (l) => l.job_succeeded_ids.length));
				setBalanceSeries(dailyBalanceSeries([...anthropic, ...apify, ...brightdata], stripe));
			} catch {
				// Leave the series empty on error; the sparklines show "No data".
			} finally {
				if (!cancelled) setSparklinesLoading(false);
			}
		};
		void load();
		return (): void => {
			cancelled = true;
		};
	}, [token]);

	const scrapedTotal: number = useMemo(() => scrapedSeries.reduce((acc, p) => acc + p.y, 0), [scrapedSeries]);
	const ratedTotal: number = useMemo(() => ratedSeries.reduce((acc, p) => acc + p.y, 0), [ratedSeries]);
	const netBalance: number = useMemo(() => balanceSeries.reduce((acc, p) => acc + p.y, 0), [balanceSeries]);

	const totalUsers: number = users.length;
	const activeUsers: number = users.filter(isActiveUser).length;
	const premiumUsers: number = users.filter((u: UserData): boolean => u.premium.is_active).length;
	const activeSettings: number = settings.filter((s): boolean => s.is_active).length;

	return (
		<div className="scraped-jobs-page">
			<PageHeader title="Admin" icon={getTableIcon("Admin")} />

			<Row className="g-3">
				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-users"
						title="Users"
						icon={getTableIcon("Users")}
						onClick={(): void => openModal("users")}
					>
						<StatList
							primary={totalUsers}
							caption="Total users"
							rows={[
								{ label: "Active (last 30 days)", value: activeUsers },
								{ label: "Premium", value: premiumUsers },
							]}
						/>
					</AdminCard>
				</Col>

				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-settings"
						title="Settings"
						icon={getTableIcon("Settings")}
						onClick={(): void => openModal("settings")}
					>
						<StatList primary={activeSettings} caption="Active settings" />
					</AdminCard>
				</Col>

				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-email-templates"
						title="Email Templates"
						icon={getTableIcon("Email Templates")}
						onClick={(): void => openModal("email")}
					>
						<StatList primary={emailTemplates.length} caption="Email templates" />
					</AdminCard>
				</Col>

				<Col xs={12}>
					<AdminCard
						id="admin-card-scheduler"
						title="Service Scheduler"
						icon="clock-history"
						onClick={(): void => openModal("scheduler")}
					>
						<SchedulerStatusBody status={scheduler.schedulerStatus} />
						{scheduler.schedulerStatus?.last_log && (
							<div className="admin-card-caption text-truncate">{scheduler.schedulerStatus.last_log}</div>
						)}
					</AdminCard>
				</Col>

				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-job-scraping"
						title="Job Scraping"
						icon={getTableIcon("Job Scraping Dashboard")}
						onClick={(): void => openModal("scraping")}
					>
						<ServiceStatusBody status={scraping.serviceStatus} remainingTime={scraping.remainingTime} />
						<div className="admin-card-sparkline">
							<div className="d-flex justify-content-between admin-card-stat">
								<span className="text-muted">Jobs scraped ({RANGE_DAYS}d)</span>
								<span className="fw-bold">{sparklinesLoading ? "…" : scrapedTotal}</span>
							</div>
							<Sparkline data={scrapedSeries} loading={sparklinesLoading} />
						</div>
					</AdminCard>
				</Col>

				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-job-rating"
						title="Job Rating"
						icon={getTableIcon("Job Rating Dashboard")}
						onClick={(): void => openModal("rating")}
					>
						<ServiceStatusBody status={rating.serviceStatus} remainingTime={rating.remainingTime} />
						<div className="admin-card-sparkline">
							<div className="d-flex justify-content-between admin-card-stat">
								<span className="text-muted">Jobs rated ({RANGE_DAYS}d)</span>
								<span className="fw-bold">{sparklinesLoading ? "…" : ratedTotal}</span>
							</div>
							<Sparkline data={ratedSeries} loading={sparklinesLoading} />
						</div>
					</AdminCard>
				</Col>

				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-usage"
						title="Provider Monitoring"
						icon={getTableIcon("ESM")}
						onClick={(): void => openModal("usage")}
					>
						<ServiceStatusBody status={monitoring.serviceStatus} remainingTime={monitoring.remainingTime} />
						<div className="admin-card-sparkline">
							<div className="d-flex justify-content-between admin-card-stat">
								<span className="text-muted">Net balance ({RANGE_DAYS}d)</span>
								<span
									className="fw-bold"
									style={
										sparklinesLoading
											? undefined
											: { color: netBalance >= 0 ? successColor : failureColor }
									}
								>
									{sparklinesLoading ? "…" : formatMoney(netBalance, "£")}
								</span>
							</div>
							<Sparkline
								data={balanceSeries}
								loading={sparklinesLoading}
								valueFormatter={(y) => formatMoney(y, "£")}
								allowNegative
							/>
						</div>
					</AdminCard>
				</Col>
			</Row>

			<JamModal
				show={showModal}
				onHide={() => setShowModal(false)}
				onExited={() => setOpenPage(null)}
				centered
				scrollable
				dialogClassName="admin-page-modal-dialog"
				className="admin-page-modal"
				id="admin-page-modal"
				aria-label={openPage ? ADMIN_PAGES[openPage].title : undefined}
			>
				{openPage && (
					<>
						<JamModal.Header onClose={() => setShowModal(false)} className="admin-page-modal-header">
							<Modal.Title>
								<span style={{ display: "flex", alignItems: "center" }}>
									<i
										className={`bi bi-${ADMIN_PAGES[openPage].icon} me-2`}
										style={{ fontSize: "1.05em" }}
									/>

									<span>{ADMIN_PAGES[openPage].title}</span>
								</span>
							</Modal.Title>
							<div className="admin-page-modal-filter" ref={setFilterSlot} />
							{pageStatus[openPage] && SERVICE_CONTROLS[openPage] && (
								<div className="admin-page-modal-status">
									<ServiceStatusControl
										status={pageStatus[openPage]!.serviceStatus}
										remainingTime={pageStatus[openPage]!.remainingTime}
										fetchStatus={pageStatus[openPage]!.fetchStatus}
										{...SERVICE_CONTROLS[openPage]!}
									/>
								</div>
							)}
						</JamModal.Header>
						<Modal.Body className="admin-page-modal-body">
							<ServiceFilterSlotContext.Provider value={filterSlot}>
								{ADMIN_PAGES[openPage].render()}
							</ServiceFilterSlotContext.Provider>
						</Modal.Body>
					</>
				)}
			</JamModal>
		</div>
	);
};

export default AdminPage;
