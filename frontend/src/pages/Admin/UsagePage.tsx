import React, { JSX, useCallback, useEffect, useMemo, useState } from "react";
import { Col, Row } from "react-bootstrap";
import PageHeader from "../PageHeader/PageHeader";
import { useAuth } from "../../contexts/AuthContext";
import { Button } from "react-bootstrap";
import {
	externalServiceMonitoringApi,
	externalServiceMonitoringRunnerApi,
} from "../../services/api/ExternalServiceMonitoring";
import { LineChart, SeriesData } from "../../components/Chart/LineChart";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { Popover } from "../../components/Popover/Popover";
import TimeSelection from "../../components/TimeSelection/TimeSelection";
import { DateRange } from "../../utils/TimeUtils";
import {
	failureColor,
	formatErrorMessage,
	renderControl,
	renderStatusIcons,
	successColor,
	useServiceControl,
} from "../Services/ServiceUtils";
import "../Services/Service.scss";
import {
	AnthropicDailyUsageData,
	ApifyBalanceData,
	ApifyDailyUsageData,
	BrightdataBalanceData,
	BrightdataDailyUsageData,
	StripeDailyIncomeData,
} from "../../services/schemas/Services";
import { getTableIcon } from "../../components/rendering/view/Icons";

const SERVICE_ICONS: Record<string, string> = {
	anthropic: "stars",
	apify: "robot",
	brightdata: "globe2",
	stripe: "credit-card",
};

const DASHBOARD_URLS: Record<string, string> = {
	anthropic: "https://console.anthropic.com/settings/usage",
	apify: "https://console.apify.com/billing",
	brightdata: "https://brightdata.com/cp/billing",
	stripe: "https://dashboard.stripe.com/payments",
};

// Distinct colours so multi-series (Bright Data datasets, Stripe gross/net) are distinguishable.
const SERIES_PALETTE: string[] = ["var(--bs-primary)", "#f59e0b", "#22c55e", "#ef4444", "#8b5cf6", "#06b6d4"];

// Spend services bill in USD, Stripe income is in GBP. Fixed rate used to express the
// net balance in a single currency (GBP). Update if the rate drifts significantly.
const USD_TO_GBP = 0.79;

const toIsoDate = (d: Date | string): string => {
	if (typeof d === "string") return d.slice(0, 10);
	return d.toISOString().slice(0, 10);
};

const formatDateTick = (value: Date): string => value.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });

const formatMoney = (value: number, prefix: string): string => `${prefix}${value.toFixed(2)}`;

interface DailyRow {
	date: string;
}

const sumByDay = <T extends DailyRow>(rows: T[], picker: (r: T) => number): number =>
	rows.reduce((acc: number, r: T): number => acc + picker(r), 0);

interface ServiceCardProps {
	service: string;
	label: string;
	icon: string;
	loading: boolean;
	error: string | null;
	totalLine: { label: string; value: string }[];
	chartData: SeriesData[];
	yAxisLabel: string;
	currencyPrefix: string;
	dashboardUrl?: string;
}

const ServiceCard = ({
	service,
	label,
	icon,
	loading,
	error,
	totalLine,
	chartData,
	yAxisLabel,
	currencyPrefix,
	dashboardUrl,
}: ServiceCardProps): JSX.Element => {
	return (
		<div className="status-card h-100">
			<div className="history-chart-header d-flex justify-content-between align-items-center">
				<h2 className="card-title">
					<i className={`bi bi-${icon} me-2`} />
					{label}
				</h2>
				{dashboardUrl && (
					<Button
						href={dashboardUrl}
						target="_blank"
						rel="noreferrer"
						variant={"outline-secondary"}
						className="btn-sm"
						style={{ fontSize: "0.95rem" }}
					>
						<i className="bi bi-box-arrow-up-right me-1" />
						Dashboard
					</Button>
				)}
			</div>
			{error ? (
				<div className="alert alert-danger py-2 px-3 mb-3">{error}</div>
			) : (
				<>
					<div className="mb-3">
						{totalLine.map(({ label: lbl, value }) => (
							<div key={`${service}-${lbl}`} className="d-flex justify-content-between mb-1">
								<span className="text-muted">{lbl}</span>
								<span className="fw-bold">{value}</span>
							</div>
						))}
					</div>
					<LineChart
						data={chartData}
						xAxisLabel="Day"
						yAxisLabel={yAxisLabel}
						xAxisFormatter={formatDateTick}
						yAxisFormatter={(v: number | null): number | null =>
							v === null ? null : Number(v.toFixed(currencyPrefix === "£" ? 2 : 4))
						}
						isLoading={loading}
						height={260}
					/>
				</>
			)}
		</div>
	);
};

interface SummaryCardProps {
	icon: string;
	label: string;
	value: string;
	caption?: string | string[];
	valueColor?: string;
}

const SummaryCard = ({ icon, label, value, caption, valueColor }: SummaryCardProps): JSX.Element => {
	const captions: string[] = caption === undefined ? [] : Array.isArray(caption) ? caption : [caption];
	return (
		<div className="status-card usage-summary-card h-100">
			<div className="usage-summary-top">
				<i className={`bi bi-${icon} usage-summary-icon`} />
				<span className="usage-summary-label">{label}</span>
			</div>
			<div className="usage-summary-value" style={valueColor ? { color: valueColor } : undefined}>
				{value}
			</div>
			{captions.map((c) => (
				<div key={c} className="usage-summary-caption">
					{c}
				</div>
			))}
		</div>
	);
};

const UsagePage = (): JSX.Element => {
	const { token } = useAuth();
	const { serviceStatus, remainingTime, fetchStatus, statusError } = useServiceRunnerStatus(
		externalServiceMonitoringRunnerApi
	);
	const control = useServiceControl(
		token,
		fetchStatus,
		(t: string) => externalServiceMonitoringRunnerApi.start(t),
		(t: string) => externalServiceMonitoringRunnerApi.stop(t)
	);

	const [dateRange, setDateRange] = useState<DateRange>({ start: new Date(), end: new Date() });

	const [anthropic, setAnthropic] = useState<AnthropicDailyUsageData[]>([]);
	const [apify, setApify] = useState<ApifyDailyUsageData[]>([]);
	const [apifyBalance, setApifyBalance] = useState<ApifyBalanceData | null>(null);
	const [brightdata, setBrightdata] = useState<BrightdataDailyUsageData[]>([]);
	const [brightdataBalance, setBrightdataBalance] = useState<BrightdataBalanceData | null>(null);
	const [stripe, setStripe] = useState<StripeDailyIncomeData[]>([]);

	const [historyLoading, setHistoryLoading] = useState<boolean>(false);
	const [historyError, setHistoryError] = useState<string | null>(null);

	const fetchHistory = useCallback(async (): Promise<void> => {
		if (!token) return;
		setHistoryLoading(true);
		setHistoryError(null);
		try {
			const range = { start_date: toIsoDate(dateRange.start), end_date: toIsoDate(dateRange.end) };
			const [a, ap, apBal, bd, bdBal, st] = await Promise.all([
				externalServiceMonitoringApi.getAnthropicHistory(range, token),
				externalServiceMonitoringApi.getApifyHistory(range, token),
				externalServiceMonitoringApi.getApifyBalance(token),
				externalServiceMonitoringApi.getBrightdataHistory(range, token),
				externalServiceMonitoringApi.getBrightdataBalance(token),
				externalServiceMonitoringApi.getStripeHistory(range, token),
			]);
			setAnthropic(a);
			setApify(ap);
			setApifyBalance(apBal);
			setBrightdata(bd);
			setBrightdataBalance(bdBal);
			setStripe(st);
		} catch (e: any) {
			setHistoryError(e?.message || "Failed to load usage history");
		} finally {
			setHistoryLoading(false);
		}
	}, [token, dateRange]);

	useEffect((): void => {
		void fetchHistory();
	}, [fetchHistory]);

	// ---- Build per-service card props ----
	const anthropicSeries: SeriesData[] = useMemo(
		() => [
			{
				id: "Spend",
				color: SERIES_PALETTE[0],
				data: anthropic.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.usage_usd })),
			},
		],
		[anthropic]
	);

	const apifySeries: SeriesData[] = useMemo(
		() => [
			{
				id: "Usage",
				color: SERIES_PALETTE[0],
				data: apify.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.usage_usd })),
			},
		],
		[apify]
	);

	// Bright Data: one line per dataset (the row schema is one row per (date, dataset)).
	const brightdataSeries: SeriesData[] = useMemo(() => {
		const datasets = Array.from(new Set(brightdata.map((r) => r.dataset))).sort();
		return datasets.map((ds, i) => ({
			id: ds,
			color: SERIES_PALETTE[i % SERIES_PALETTE.length],
			data: brightdata
				.filter((r) => r.dataset === ds)
				.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.usage_usd })),
		}));
	}, [brightdata]);

	const stripeSeries: SeriesData[] = useMemo(
		() => [
			{
				id: "Gross",
				color: SERIES_PALETTE[0],
				data: stripe.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.gross_gbp })),
			},
			{
				id: "Net",
				color: SERIES_PALETTE[2],
				data: stripe.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.net_gbp })),
			},
		],
		[stripe]
	);

	// Period totals for the summary cards (period follows the filter above).
	const summary = useMemo(() => {
		const anthropicUsd = sumByDay(anthropic, (r) => r.usage_usd);
		const apifyUsd = sumByDay(apify, (r) => r.usage_usd);
		const brightdataUsd = sumByDay(brightdata, (r) => r.usage_usd);
		const stripeNetGbp = sumByDay(stripe, (r) => r.net_gbp);
		const totalSpendGbp = (anthropicUsd + apifyUsd + brightdataUsd) * USD_TO_GBP;
		return { anthropicUsd, apifyUsd, brightdataUsd, stripeNetGbp, netGbp: stripeNetGbp - totalSpendGbp };
	}, [anthropic, apify, brightdata, stripe]);

	const collectedErrors = [
		{ key: "status", label: "Service status", value: statusError },
		{ key: "history", label: "Usage history", value: historyError },
	].filter((e) => e.value);

	return (
		<div className="scraped-jobs-page">
			<PageHeader
				title="External Service Monitoring"
				icon={getTableIcon("ESM")}
				statusContent={
					<Popover
						trigger={renderStatusIcons(serviceStatus, remainingTime)}
						ariaLabel="Monitoring service controls"
					>
						{(close) =>
							renderControl(
								serviceStatus,
								null,
								control.loading,
								() => {
									close();
									control.handleStart();
								},
								() => {
									close();
									control.handleStop();
								}
							)
						}
					</Popover>
				}
			/>

			{collectedErrors.length > 0 && (
				<div className="alert alert-danger mb-4 shadow-sm rounded-3" role="alert">
					<div className="d-flex align-items-start">
						<i className="bi bi-exclamation-triangle-fill me-3 fs-5" />
						<div className="flex-grow-1">
							<h5 className="alert-heading mb-2">Errors</h5>
							<ul className="mb-0">
								{collectedErrors.map((e) => (
									<li key={e.key}>
										<strong>{e.label}:</strong> {formatErrorMessage(e.value)}
									</li>
								))}
							</ul>
						</div>
					</div>
				</div>
			)}

			<div id="history-filters" className="status-card filter-card mt-4">
				<div className="d-flex align-items-center gap-3 flex-wrap">
					<span className="filter-card-label">
						<i className="bi bi-funnel me-2" />
						Filters
					</span>
					<TimeSelection
						onDateRangeChange={setDateRange}
						defaultMode="period"
						defaultAmount={1}
						defaultUnit="months"
						defaultIntervalSeconds={3600}
					/>
				</div>
			</div>

			<Row className="g-3 mt-1">
				<Col xs={12} sm={6} lg={4} xl={true}>
					<SummaryCard
						icon={SERVICE_ICONS.anthropic || "cpu"}
						label="Anthropic spend"
						value={formatMoney(summary.anthropicUsd, "$")}
					/>
				</Col>
				<Col xs={12} sm={6} lg={4} xl={true}>
					<SummaryCard
						icon={SERVICE_ICONS.apify || "cpu"}
						label="Apify spend"
						value={formatMoney(summary.apifyUsd, "$")}
						caption={
							apifyBalance?.limit_usd != null
								? `Cycle limit: ${formatMoney(apifyBalance.limit_usd, "$")}`
								: undefined
						}
					/>
				</Col>
				<Col xs={12} sm={6} lg={4} xl={true}>
					<SummaryCard
						icon={SERVICE_ICONS.brightdata || "cpu"}
						label="Bright Data spend"
						value={formatMoney(summary.brightdataUsd, "$")}
						caption={
							[
								...(brightdataBalance?.balance_usd != null
									? [`Balance: ${formatMoney(brightdataBalance.balance_usd, "$")}`]
									: []),
								...(brightdataBalance?.pending_costs_usd != null
									? [`Pending: ${formatMoney(brightdataBalance.pending_costs_usd, "$")}`]
									: []),
							].join(" · ") || undefined
						}
					/>
				</Col>
				<Col xs={12} sm={6} lg={4} xl={true}>
					<SummaryCard
						icon={SERVICE_ICONS.stripe || "cpu"}
						label="Stripe income"
						value={formatMoney(summary.stripeNetGbp, "£")}
					/>
				</Col>
				<Col xs={12} sm={6} lg={4} xl={true}>
					<SummaryCard
						icon="cash-stack"
						label="Net balance"
						value={formatMoney(summary.netGbp, "£")}
						valueColor={summary.netGbp >= 0 ? successColor : failureColor}
					/>
				</Col>
			</Row>

			<Row className="g-3 mt-1">
				<Col md={6}>
					<ServiceCard
						service="anthropic"
						label="Anthropic (Claude)"
						icon={SERVICE_ICONS.anthropic || "cpu"}
						dashboardUrl={DASHBOARD_URLS.anthropic}
						loading={historyLoading}
						error={null}
						totalLine={[]}
						chartData={anthropicSeries}
						yAxisLabel="Spend ($)"
						currencyPrefix="$"
					/>
				</Col>
				<Col md={6}>
					<ServiceCard
						service="apify"
						label="Apify"
						icon={SERVICE_ICONS.apify || "cpu"}
						dashboardUrl={DASHBOARD_URLS.apify}
						loading={historyLoading}
						error={null}
						totalLine={[]}
						chartData={apifySeries}
						yAxisLabel="Usage ($)"
						currencyPrefix="$"
					/>
				</Col>
				<Col md={6}>
					<ServiceCard
						service="brightdata"
						label="Bright Data"
						icon={SERVICE_ICONS.brightdata || "cpu"}
						dashboardUrl={DASHBOARD_URLS.brightdata}
						loading={historyLoading}
						error={null}
						totalLine={[]}
						chartData={brightdataSeries}
						yAxisLabel="Spend ($)"
						currencyPrefix="$"
					/>
				</Col>
				<Col md={6}>
					<ServiceCard
						service="stripe"
						label="Stripe Income"
						icon={SERVICE_ICONS.stripe || "cpu"}
						dashboardUrl={DASHBOARD_URLS.stripe}
						loading={historyLoading}
						error={null}
						totalLine={[]}
						chartData={stripeSeries}
						yAxisLabel="Income (£)"
						currencyPrefix="£"
					/>
				</Col>
			</Row>
		</div>
	);
};

export default UsagePage;
