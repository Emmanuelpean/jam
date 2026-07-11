import React, { JSX, useCallback, useEffect, useMemo, useState } from "react";
import { Col, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { Button } from "react-bootstrap";
import {
	providerMonitoringApi,
	providerMonitoringRunnerApi,
} from "../../services/api/ProviderMonitoring";
import { LineChart, SeriesData } from "../../components/Chart/LineChart";
import { useServiceRunnerStatus } from "../../hooks/useServiceRunnerStatus";
import { useServiceLogs } from "../../hooks/useServiceLogs";
import { useServiceErrors } from "../../hooks/useServiceErrors";
import { providerMonitoringServiceLogApi } from "../../services/api/Services";
import LogViewer, { useLogViewerToggle } from "../Services/LogViewer/LogViewer";
import { LastLogBar } from "../Services/LogViewer/LastLogBar";
import { ErrorSummaryCard } from "../Services/ErrorSummaryCard";
import { TimeFilterPopover } from "../../components/TimeSelection/TimeFilterPopover";
import { ServiceFilterSlot } from "../Services/ServiceFilterSlot";
import { DateRange } from "../../utils/TimeUtils";
import { failureColor, formatErrorMessage, successColor } from "../Services/ServiceUtils";
import "../Services/Service.scss";
import {
	AnthropicDailyUsageData,
	ApifyBalanceData,
	ApifyDailyUsageData,
	BrightdataBalanceData,
	BrightdataDailyUsageData,
	ServiceLog,
	StripeDailyIncomeData,
} from "../../services/schemas/Services";

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
	const { serviceStatus, statusError } = useServiceRunnerStatus(providerMonitoringRunnerApi);
	const {
		expanded: logsExpanded,
		setExpanded: setLogsExpanded,
		open: openLogViewer,
	} = useLogViewerToggle("usage-log-viewer");
	const [dateRange, setDateRange] = useState<DateRange | null>(null);
	const [showAcknowledged, setShowAcknowledged] = useState<boolean>(false);

	const isRunning: boolean = serviceStatus?.is_running || false;
	const { previousServiceLogs, loading: logsLoading } = useServiceLogs<ServiceLog>(
		providerMonitoringServiceLogApi,
		isRunning,
		dateRange
	);
	const {
		errors,
		setAcknowledged,
		loading: errorsLoading,
	} = useServiceErrors(previousServiceLogs, "provider_monitoring_service_log_id", showAcknowledged, true);

	const [anthropic, setAnthropic] = useState<AnthropicDailyUsageData[]>([]);
	const [apify, setApify] = useState<ApifyDailyUsageData[]>([]);
	const [apifyBalance, setApifyBalance] = useState<ApifyBalanceData | null>(null);
	const [brightdata, setBrightdata] = useState<BrightdataDailyUsageData[]>([]);
	const [brightdataBalance, setBrightdataBalance] = useState<BrightdataBalanceData | null>(null);
	const [stripe, setStripe] = useState<StripeDailyIncomeData[]>([]);

	const [historyLoading, setHistoryLoading] = useState<boolean>(false);
	const [historyError, setHistoryError] = useState<string | null>(null);

	const fetchHistory = useCallback(async (): Promise<void> => {
		if (!token || !dateRange) return;
		setHistoryLoading(true);
		setHistoryError(null);
		try {
			const range = { start_date: toIsoDate(dateRange.start), end_date: toIsoDate(dateRange.end) };
			const [a, ap, apBal, bd, bdBal, st] = await Promise.all([
				providerMonitoringApi.getAnthropicHistory(range, token),
				providerMonitoringApi.getApifyHistory(range, token),
				providerMonitoringApi.getApifyBalance(token),
				providerMonitoringApi.getBrightdataHistory(range, token),
				providerMonitoringApi.getBrightdataBalance(token),
				providerMonitoringApi.getStripeHistory(range, token),
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
				data: anthropic.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.usage_usd })),
			},
		],
		[anthropic]
	);

	const apifySeries: SeriesData[] = useMemo(
		() => [
			{
				id: "Usage",
				data: apify.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.usage_usd })),
			},
		],
		[apify]
	);

	// Bright Data: one line per dataset (the row schema is one row per (date, dataset)).
	const brightdataSeries: SeriesData[] = useMemo(() => {
		const datasets = Array.from(new Set(brightdata.map((r) => r.dataset))).sort();
		return datasets.map((ds) => ({
			id: ds,
			data: brightdata
				.filter((r) => r.dataset === ds)
				.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.usage_usd })),
		}));
	}, [brightdata]);

	const stripeSeries: SeriesData[] = useMemo(
		() => [
			{
				id: "Gross",
				data: stripe.map((r) => ({ x: new Date(r.date + "T00:00:00Z"), y: r.gross_gbp })),
			},
			{
				id: "Net",
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

			<ServiceFilterSlot>
				<TimeFilterPopover
					id="history-filters"
					onDateRangeChange={setDateRange}
					defaultMode="period"
					defaultAmount={1}
					defaultUnit="months"
					defaultIntervalSeconds={3600}
					availableUnits={["weeks", "months", "years"]}
				/>
			</ServiceFilterSlot>

			<LastLogBar serviceStatus={serviceStatus} onClick={openLogViewer} className="mb-3" />

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

			<LogViewer
				id="usage-log-viewer"
				api={providerMonitoringRunnerApi}
				isServiceRunning={isRunning}
				expanded={logsExpanded}
				onExpandedChange={setLogsExpanded}
			/>

			<ErrorSummaryCard
				current={{ errors, setAcknowledged }}
				showAcknowledged={showAcknowledged}
				onToggleAcknowledged={setShowAcknowledged}
				isRunning={isRunning}
				loading={logsLoading || errorsLoading}
			/>
		</div>
	);
};

export default UsagePage;
