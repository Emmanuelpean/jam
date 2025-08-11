import React, { useEffect, useState } from "react";
import { Badge, Button, ButtonGroup, Card, Col, Container, Form, Row, Table } from "react-bootstrap";
import { ResponsiveBar } from "@nivo/bar";
import { ResponsiveLine } from "@nivo/line";
import { serviceLogApi } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { formatTimeAgo } from "../utils/TimeUtils";
import { barChartProps, lineChartProps } from "../components/charts/Themes";
import { useLoading } from "../contexts/LoadingContext";

const TIME_RANGES = [
	{ value: "7", label: "Last 7 Days" },
	{ value: "30", label: "Last 30 Days" },
	{ value: "180", label: "Last 6 Months" },
	{ value: "365", label: "Last 12 Months" },
	{ value: "0", label: "All Time" },
];

const ServiceLogDashboard = () => {
	const { token, is_admin } = useAuth();
	const { showLoading, hideLoading } = useLoading();
	const [serviceLogData, setServiceLogData] = useState([]);
	const [chartType, setChartType] = useState("line");
	const [timeRange, setTimeRange] = useState("7");
	const [recentLogs, setRecentLogs] = useState([]);
	const [error, setError] = useState(null);

	useEffect(() => {
		if (!is_admin) {
			setError("Access denied: Admin privileges required");
			return;
		}
		fetchServiceLogData().then(() => null);
		fetchRecentLogs().then(() => null);
	}, [token, is_admin, timeRange]);

	const fetchServiceLogData = async () => {
		try {
			showLoading("Loading service log data...");
			setError(null);

			// Use delta_days parameter for time range
			const params = {
				delta_days: timeRange !== "0" ? parseInt(timeRange) : undefined,
			};

			const serviceLogsRes = await serviceLogApi.getAll(token, params);
			processServiceLogs(serviceLogsRes);
		} catch (err) {
			console.error("Error fetching service log data:", err);
			setError("Failed to load service log data");
		} finally {
			hideLoading();
		}
	};

	const fetchRecentLogs = async () => {
		try {
			showLoading("Loading recent logs...");
			const params = {
				limit: 10,
			};
			const data = await serviceLogApi.getAll(token, params);
			setRecentLogs(data);
		} catch (err) {
			console.error("Error fetching recent logs:", err);
			setError("Failed to load recent service logs");
		} finally {
			hideLoading();
		}
	};

	const processServiceLogs = (serviceLogs) => {
		const groupedData = groupLogsByDate(serviceLogs);
		setChartData(groupedData);
	};

	const groupLogsByDate = (serviceLogs) => {
		const grouped = new Map();
		const days = parseInt(timeRange) || 365;

		serviceLogs.forEach((log) => {
			const date = new Date(log.run_datetime);
			let key;

			if (days <= 30) {
				key = date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
			} else if (days <= 180) {
				const weekNum = Math.floor((new Date() - date) / (7 * 24 * 60 * 60 * 1000));
				key = `Week ${weekNum + 1}`;
			} else {
				key = date.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
			}

			if (!grouped.has(key)) {
				grouped.set(key, {
					successful: 0,
					failed: 0,
					totalDuration: 0,
					count: 0,
				});
			}

			const group = grouped.get(key);
			if (log.is_success) group.successful++;
			else group.failed++;
			group.totalDuration += log.run_duration || 0;
			group.count++;
		});

		return Array.from(grouped.entries()).map(([date, data]) => ({
			date,
			successful: data.successful,
			failed: data.failed,
			duration: data.count > 0 ? data.totalDuration / data.count : 0,
		}));
	};

	const setChartData = (groupedData) => {
		if (chartType === "line") {
			setServiceLogData([
				{
					id: "Average Duration",
					color: "#3498db",
					data: groupedData.map((d) => ({
						x: d.date,
						y: parseFloat(d.duration.toFixed(2)),
					})),
				},
			]);
		} else {
			setServiceLogData(
				groupedData.map((d) => ({
					period: d.date,
					successful: d.successful,
					failed: d.failed,
				})),
			);
		}
	};

	const getStatusBadgeColor = (isSuccess) => {
		return isSuccess ? "success" : "danger";
	};

	const getStatusIcon = (isSuccess) => {
		return isSuccess ? "bi-check-circle-fill" : "bi-x-circle-fill";
	};

	if (!is_admin) {
		return (
			<Container className="mt-4">
				<div className="alert alert-danger border-0 shadow-sm" role="alert">
					<i className="bi bi-shield-x me-2"></i>
					Access denied: Admin privileges required to view service logs
				</div>
			</Container>
		);
	}

	if (error) {
		return (
			<Container className="mt-4">
				<div className="alert alert-danger border-0 shadow-sm" role="alert">
					<i className="bi bi-exclamation-circle me-2"></i>
					{error}
				</div>
			</Container>
		);
	}

	return (
		<Container fluid className="mt-4">
			{/* Main Chart */}
			<Row className="mb-4">
				<Col lg={8}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 d-flex justify-content-between align-items-center p-4">
							<h5 className="mb-0 fw-semibold text-dark">Service Performance</h5>
							<div className="d-flex gap-2">
								<ButtonGroup>
									<Button
										variant={chartType === "line" ? "info" : "outline-info"}
										onClick={() => setChartType("line")}
										className="px-3"
									>
										<i className="bi bi-graph-up me-2"></i>
										Duration
									</Button>
									<Button
										variant={chartType === "bar" ? "info" : "outline-info"}
										onClick={() => setChartType("bar")}
										className="px-3"
									>
										<i className="bi bi-bar-chart me-2"></i>
										Success/Fail
									</Button>
								</ButtonGroup>
								<Form.Select
									value={timeRange}
									onChange={(e) => setTimeRange(e.target.value)}
									className="w-auto"
								>
									{TIME_RANGES.map(({ value, label }) => (
										<option key={value} value={value}>
											{label}
										</option>
									))}
								</Form.Select>
							</div>
						</Card.Header>
						<Card.Body className="p-4">
							{serviceLogData.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-server text-muted" style={{ fontSize: "4rem" }}></i>
									<h4 className="mt-4 text-muted fw-semibold">No Service Log Data</h4>
									<p className="text-muted fs-6">Service logs will appear here when available.</p>
								</div>
							) : (
								<div style={{ height: "400px" }}>
									{chartType === "line" ? (
										<ResponsiveLine data={serviceLogData} {...lineChartProps} />
									) : (
										<ResponsiveBar data={serviceLogData} {...barChartProps} />
									)}
								</div>
							)}
						</Card.Body>
					</Card>
				</Col>

				{/* Recent Logs */}
				<Col lg={4}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 p-4">
							<h5 className="mb-0 fw-semibold text-dark">
								<i className="bi bi-clock-history me-2 text-secondary"></i>
								Recent Service Runs
							</h5>
						</Card.Header>
						<Card.Body className="p-0" style={{ maxHeight: "500px", overflowY: "auto" }}>
							{recentLogs.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-list-ul text-muted" style={{ fontSize: "3rem" }}></i>
									<p className="mt-3 text-muted fw-semibold">No recent logs</p>
								</div>
							) : (
								<Table className="mb-0" size="sm">
									<tbody>
										{recentLogs.map((log, index) => (
											<tr key={log.id || index}>
												<td className="px-3 py-2">
													<div className="d-flex align-items-center">
														<div
															className="rounded-circle d-flex align-items-center justify-content-center me-2"
															style={{
																width: "32px",
																height: "32px",
																backgroundColor: log.is_success ? "#d4edda" : "#f8d7da",
																color: log.is_success ? "#155724" : "#721c24",
															}}
														>
															<i
																className={`bi ${getStatusIcon(log.is_success)} fs-6`}
															></i>
														</div>
														<div className="flex-grow-1">
															<div className="fw-semibold small">{log.name}</div>
															<div className="text-muted small">
																{log.run_duration
																	? `${log.run_duration.toFixed(2)}s`
																	: "N/A"}{" "}
																• {formatTimeAgo(log.run_datetime)}
															</div>
															{log.error_message && (
																<div className="text-danger small">
																	<i className="bi bi-exclamation-triangle me-1"></i>
																	{log.error_message.substring(0, 50)}...
																</div>
															)}
														</div>
														<Badge
															bg={getStatusBadgeColor(log.is_success)}
															className="ms-2"
														>
															{log.is_success ? "Success" : "Failed"}
														</Badge>
													</div>
												</td>
											</tr>
										))}
									</tbody>
								</Table>
							)}
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
};

export default ServiceLogDashboard;
