import React, { JSX, ReactNode, useCallback, useEffect, useState } from "react";
import { Col, Modal, Row } from "react-bootstrap";
import PageHeader from "../PageHeader/PageHeader";
import { ModalHeaderSlotContext } from "../../contexts/ModalHeaderSlotContext";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";
import { useDataContext } from "../../contexts/DataContext";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { jobRatingServiceRunnerApi, jobScraperServiceApi, ServiceStatus } from "../../services/api/Services";
import {
	externalServiceMonitoringApi,
	externalServiceMonitoringRunnerApi,
} from "../../services/api/ExternalServiceMonitoring";
import { failureColor, serviceRunnerStatusLabels, successColor } from "../Services/ServiceUtils";
import { formatDuration } from "../../utils/TimeUtils";
import { UserData } from "../../services/schemas/Core";
import JamModal from "../../components/JamModal/JamModal";
import { UsersPage } from "./UsersPage";
import { AppSettingsPage } from "./AppSettingsPage";
import EmailTemplatesPage from "./EmailTemplatesPage";
import JobScrapingPage from "../Services/JobScrapingPage";
import JobRatingPage from "../Services/JobRatingPage";
import UsagePage from "./UsagePage";
import "../Services/Service.scss";
import "./AdminPage.scss";

// Each admin card opens its page inside a large modal rather than navigating away.
type AdminPageKey = "users" | "settings" | "email" | "scraping" | "rating" | "usage";

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
		title: "External Service Monitoring",
		icon: getTableIcon("ESM"),
		render: () => <UsagePage />,
	},
};

// Spend services bill in USD, Stripe income is in GBP. Fixed rate used to express the
// net balance in a single currency (GBP), matching UsagePage.
const USD_TO_GBP = 0.79;

const toIsoDate = (d: Date): string => d.toISOString().slice(0, 10);

const formatMoney = (value: number, prefix: string): string => `${prefix}${value.toFixed(2)}`;

interface DailyRow {
	usage_usd?: number;
	net_gbp?: number;
}

const sumBy = <T extends DailyRow>(rows: T[], picker: (r: T) => number): number =>
	rows.reduce((acc: number, r: T): number => acc + picker(r), 0);

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
	const runnerActive: boolean = !!status && ["started", "starting"].includes(status.service_runner_status);
	const isStopping: boolean = status?.service_runner_status === "stopping";
	const serviceRunning: boolean = !!status?.service_running;
	const showCountdown: boolean = status?.service_runner_status === "started" && !serviceRunning;
	return (
		<StatList
			rows={[
				{
					label: "Service runner",
					value: (
						<span className="admin-card-status-value">
							<i
								className={`bi bi-cpu-fill service-status-icon service-status-icon--runner ${runnerActive ? "is-on" : "is-off"} ${isStopping ? "is-stopping" : ""}`}
							/>
							{status ? serviceRunnerStatusLabels[status.service_runner_status] : "…"}
						</span>
					),
				},
				{
					label: "Service",
					value: (
						<span className="admin-card-status-value">
							<i
								className={`bi bi-activity service-status-icon ${serviceRunning ? "is-on is-running" : "is-off"}`}
							/>
							{serviceRunning ? "Running" : "Idle"}
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

const isActiveUser = (user: UserData): boolean => {
	if (!user.last_login) return false;
	const monthAgo: number = Date.now() - 30 * 24 * 60 * 60 * 1000;
	return new Date(user.last_login).getTime() >= monthAgo;
};

const AdminPage = (): JSX.Element => {
	const { token } = useAuth();
	const { users, settings, emailTemplates } = useDataContext();
	const [openPage, setOpenPage] = useState<AdminPageKey | null>(null);
	// `showModal` drives the open/close transition; the modal stays mounted while it
	// animates out, and `openPage` (the content) is only cleared once it has (onExited).
	const [showModal, setShowModal] = useState<boolean>(false);
	// The modal header's status area; the open page portals its status control here.
	const [statusEl, setStatusEl] = useState<HTMLElement | null>(null);

	const openModal = (key: AdminPageKey): void => {
		setOpenPage(key);
		setShowModal(true);
	};

	const scraping = useServiceRunnerStatus(jobScraperServiceApi);
	const rating = useServiceRunnerStatus(jobRatingServiceRunnerApi);
	const monitoring = useServiceRunnerStatus(externalServiceMonitoringRunnerApi);

	const [netBalance, setNetBalance] = useState<number | null>(null);
	const [balanceError, setBalanceError] = useState<boolean>(false);

	// Net balance over the trailing 30 days, mirroring UsagePage's computation.
	const fetchNetBalance = useCallback(async (): Promise<void> => {
		if (!token) return;
		setBalanceError(false);
		try {
			const end = new Date();
			const start = new Date(end.getTime() - 30 * 24 * 60 * 60 * 1000);
			const range = { start_date: toIsoDate(start), end_date: toIsoDate(end) };
			const [anthropic, apify, brightdata, stripe] = await Promise.all([
				externalServiceMonitoringApi.getAnthropicHistory(range, token),
				externalServiceMonitoringApi.getApifyHistory(range, token),
				externalServiceMonitoringApi.getBrightdataHistory(range, token),
				externalServiceMonitoringApi.getStripeHistory(range, token),
			]);
			const spendUsd =
				sumBy(anthropic, (r) => r.usage_usd ?? 0) +
				sumBy(apify, (r) => r.usage_usd ?? 0) +
				sumBy(brightdata, (r) => r.usage_usd ?? 0);
			const stripeNetGbp = sumBy(stripe, (r) => r.net_gbp ?? 0);
			setNetBalance(stripeNetGbp - spendUsd * USD_TO_GBP);
		} catch {
			setBalanceError(true);
		}
	}, [token]);

	useEffect((): void => {
		void fetchNetBalance();
	}, [fetchNetBalance]);

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

				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-job-scraping"
						title="Job Scraping"
						icon={getTableIcon("Job Scraping Dashboard")}
						onClick={(): void => openModal("scraping")}
					>
						<ServiceStatusBody status={scraping.serviceStatus} remainingTime={scraping.remainingTime} />
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
					</AdminCard>
				</Col>

				<Col xs={12} md={6} xl={4}>
					<AdminCard
						id="admin-card-usage"
						title="External Service Monitoring"
						icon={getTableIcon("ESM")}
						onClick={(): void => openModal("usage")}
					>
						<ServiceStatusBody status={monitoring.serviceStatus} remainingTime={monitoring.remainingTime} />
						<div className="d-flex justify-content-between admin-card-stat mt-2">
							<span className="text-muted">Net balance (30d)</span>
							<span
								className="fw-bold"
								style={
									netBalance === null
										? undefined
										: { color: netBalance >= 0 ? successColor : failureColor }
								}
							>
								{balanceError ? "—" : netBalance === null ? "…" : formatMoney(netBalance, "£")}
							</span>
						</div>
					</AdminCard>
				</Col>
			</Row>

			<JamModal
				show={showModal}
				onHide={() => setShowModal(false)}
				onExited={() => {
					setOpenPage(null);
					setStatusEl(null);
				}}
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
							<div className="admin-page-modal-title">
								<div className="header-icon-wrapper me-2">
									<i className={`bi bi-${ADMIN_PAGES[openPage].icon}`} />
								</div>
								<h4 className="mb-0 fw-bold">{ADMIN_PAGES[openPage].title}</h4>
							</div>
							<div ref={setStatusEl} className="admin-page-modal-status" />
						</JamModal.Header>
						<Modal.Body className="admin-page-modal-body">
							<ModalHeaderSlotContext.Provider value={statusEl}>
								{statusEl && ADMIN_PAGES[openPage].render()}
							</ModalHeaderSlotContext.Provider>
						</Modal.Body>
					</>
				)}
			</JamModal>
		</div>
	);
};

export default AdminPage;
