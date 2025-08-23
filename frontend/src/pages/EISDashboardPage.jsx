import React, { useEffect, useState } from "react";
import { Badge, Button, Card, Col, Container, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import { ResponsiveLine } from "@nivo/line";
import { scrapedJobApi, serviceLogApi } from "../services/Api.ts";
import { useAuth } from "../contexts/AuthContext.tsx";
import { formatTimeAgo } from "../utils/TimeUtils.ts";
import { lineChartProps } from "../components/charts/Themes";
import { useLoading } from "../contexts/LoadingContext.tsx";

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
	const [durationData, setDurationData] = useState([]);
	const [scrapingData, setScrapingData] = useState([]);
	const [timeRange, setTimeRange] = useState("7");
	const [recentLogs, setRecentLogs] = useState([]);
	const [error, setError] = useState(null);

	// Modal state
	const [showModal, setShowModal] = useState(false);
	const [selectedLog, setSelectedLog] = useState(null);
	const [scrapedJobs, setScrapedJobs] = useState([]);
	const [modalLoading, setModalLoading] = useState(false);

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
			showLoading("Loading EIS dashboard...");
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
			showLoading("Loading EIS dashboard...");
			const params = {
				limit: 10,
			};
			const data = await serviceLogApi.getAll(token, params);
			console.log(data);
			setRecentLogs(data);
		} catch (err) {
			console.error("Error fetching recent logs:", err);
			setError("Failed to load recent service logs");
		} finally {
			hideLoading();
		}
	};

	const fetchScrapedJobsForLog = async (serviceLog) => {
		try {
			setModalLoading(true);
			setSelectedLog(serviceLog);
			setShowModal(true);

			// Fetch scraped jobs for the time period around this service log
			const logDate = new Date(serviceLog.run_datetime);
			const startDate = new Date(logDate.getTime() - 60 * 60 * 1000); // 1 hour before
			const endDate = new Date(logDate.getTime() + 60 * 60 * 1000); // 1 hour after

			// Get scraped jobs (this might need to be adjusted based on your API structure)
			const scrapedJobsData = await scrapedJobApi.getAll(token, {
				created_after: startDate.toISOString(),
				created_before: endDate.toISOString(),
				limit: 100,
			});

			setScrapedJobs(scrapedJobsData || []);
		} catch (err) {
			console.error("Error fetching scraped jobs:", err);
			setScrapedJobs([]);
		} finally {
			setModalLoading(false);
		}
	};

	const handleCloseModal = () => {
		setShowModal(false);
		setSelectedLog(null);
		setScrapedJobs([]);
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
					jobsScraped: 0,
					jobsFound: 0,
				});
			}

			const group = grouped.get(key);
			if (log.is_success) group.successful++;
			else group.failed++;
			group.totalDuration += log.run_duration || 0;
			group.count++;

			// Add job scraping metrics
			group.jobsScraped += log.job_success_n || 0;
			group.jobsFound += (log.job_success_n || 0) + (log.job_fail_n || 0);
		});

		return Array.from(grouped.entries()).map(([date, data]) => ({
			date,
			successful: data.successful,
			failed: data.failed,
			duration: data.count > 0 ? data.totalDuration / data.count : 0,
			jobsScraped: data.jobsScraped,
			jobsFound: data.jobsFound,
			successRate: data.jobsFound > 0 ? (data.jobsScraped / data.jobsFound) * 100 : 0,
		}));
	};

	const setChartData = (groupedData) => {
		// Set duration data for line chart
		setDurationData([
			{
				id: "Average Duration",
				color: "#3498db",
				data: groupedData.map((d) => ({
					x: d.date,
					y: parseFloat(d.duration.toFixed(2)),
				})),
			},
		]);

		// Set scraping data for line/bar chart
		setScrapingData([
			{
				id: "Jobs Found",
				color: "#f39c12",
				data: groupedData.map((d) => ({
					x: d.date,
					y: d.jobsFound,
				})),
			},
			{
				id: "Jobs Scraped",
				color: "#27ae60",
				data: groupedData.map((d) => ({
					x: d.date,
					y: d.jobsScraped,
				})),
			},
			{
				id: "Success Rate (%)",
				color: "#9b59b6",
				data: groupedData.map((d) => ({
					x: d.date,
					y: parseFloat(d.successRate.toFixed(1)),
				})),
			},
		]);
	};

	const getStatusBadgeColor = (isSuccess) => {
		return isSuccess ? "success" : "danger";
	};

	const getStatusIcon = (isSuccess) => {
		return isSuccess ? "bi-check-circle-fill" : "bi-x-circle-fill";
	};

	const getScrapingStatusColor = (isScraped, isFailed) => {
		if (isScraped) return "success";
		if (isFailed) return "danger";
		return "warning";
	};

	const getScrapingStatusText = (isScraped, isFailed) => {
		if (isScraped) return "Scraped";
		if (isFailed) return "Failed";
		return "Pending";
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
			{/* Time Range Selector */}
			<Row className="mb-4">
				<Col>
					<div className="d-flex justify-content-end">
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
				</Col>
			</Row>

			{/* Charts Row */}
			<Row className="mb-4">
				{/* Run Duration Chart */}
				<Col lg={6}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 d-flex justify-content-between align-items-center p-4">
							<h5 className="mb-0 fw-semibold text-dark">
								<i className="bi bi-clock me-2 text-primary"></i>
								Run Duration
							</h5>
						</Card.Header>
						<Card.Body className="p-4">
							{durationData.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-graph-up text-muted" style={{ fontSize: "4rem" }}></i>
									<h4 className="mt-4 text-muted fw-semibold">No Duration Data</h4>
									<p className="text-muted fs-6">
										Service run durations will appear here when available.
									</p>
								</div>
							) : (
								<div style={{ height: "300px" }}>
									<ResponsiveLine
										data={durationData}
										{...lineChartProps}
										axisLeft={{
											...lineChartProps.axisLeft,
											legend: "Duration (seconds)",
											legendPosition: "middle",
											legendOffset: -40,
										}}
									/>
								</div>
							)}
						</Card.Body>
					</Card>
				</Col>

				{/* Job Scraping Metrics Chart */}
				<Col lg={6}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 d-flex justify-content-between align-items-center p-4">
							<h5 className="mb-0 fw-semibold text-dark">
								<i className="bi bi-collection me-2 text-success"></i>
								Job Scraping Metrics
							</h5>
						</Card.Header>
						<Card.Body className="p-4">
							{scrapingData.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-collection text-muted" style={{ fontSize: "4rem" }}></i>
									<h4 className="mt-4 text-muted fw-semibold">No Scraping Data</h4>
									<p className="text-muted fs-6">
										Job scraping metrics will appear here when available.
									</p>
								</div>
							) : (
								<div style={{ height: "300px" }}>
									<ResponsiveLine
										data={scrapingData}
										{...lineChartProps}
										axisLeft={{
											...lineChartProps.axisLeft,
											legend: "Count / Percentage",
											legendPosition: "middle",
											legendOffset: -50,
										}}
										legends={[
											{
												anchor: "bottom-right",
												direction: "column",
												justify: false,
												translateX: 100,
												translateY: 0,
												itemsSpacing: 0,
												itemDirection: "left-to-right",
												itemWidth: 80,
												itemHeight: 20,
												itemOpacity: 0.75,
												symbolSize: 12,
												symbolShape: "circle",
												symbolBorderColor: "rgba(0, 0, 0, .5)",
											},
										]}
									/>
								</div>
							)}
						</Card.Body>
					</Card>
				</Col>
			</Row>

			{/* Recent Logs */}
			<Row>
				<Col>
					<Card className="border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 p-4">
							<h5 className="mb-0 fw-semibold text-dark">
								<i className="bi bi-clock-history me-2 text-secondary"></i>
								Recent Service Runs
								<small className="text-muted ms-2">(Click rows to view scraped jobs)</small>
							</h5>
						</Card.Header>
						<Card.Body className="p-0" style={{ maxHeight: "400px", overflowY: "auto" }}>
							{recentLogs.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-list-ul text-muted" style={{ fontSize: "3rem" }}></i>
									<p className="mt-3 text-muted fw-semibold">No recent logs</p>
								</div>
							) : (
								<Table className="mb-0" size="sm" hover>
									<thead className="table-light">
										<tr>
											<th className="px-3 py-2">Service</th>
											<th className="px-3 py-2">Duration</th>
											<th className="px-3 py-2">Jobs Found</th>
											<th className="px-3 py-2">Jobs Scraped</th>
											<th className="px-3 py-2">Success Rate</th>
											<th className="px-3 py-2">Status</th>
											<th className="px-3 py-2">Time</th>
										</tr>
									</thead>
									<tbody>
										{recentLogs.map((log, index) => {
											const jobsFound = (log.job_success_n || 0) + (log.job_fail_n || 0);
											const jobsScraped = log.job_success_n || 0;
											const successRate =
												jobsFound > 0 ? ((jobsScraped / jobsFound) * 100).toFixed(1) : "0.0";

											return (
												<tr
													key={log.id || index}
													className="table-row-clickable"
													style={{ cursor: "pointer" }}
													onClick={() => fetchScrapedJobsForLog(log)}
													title="Click to view scraped jobs"
												>
													<td className="px-3 py-2">
														<div className="d-flex align-items-center">
															<div
																className="rounded-circle d-flex align-items-center justify-content-center me-2"
																style={{
																	width: "32px",
																	height: "32px",
																	backgroundColor: log.is_success
																		? "#d4edda"
																		: "#f8d7da",
																	color: log.is_success ? "#155724" : "#721c24",
																}}
															>
																<i
																	className={`bi ${getStatusIcon(log.is_success)} fs-6`}
																></i>
															</div>
															<div>
																<div className="fw-semibold small">{log.name}</div>
																{log.error_message && (
																	<div className="text-danger small">
																		<i className="bi bi-exclamation-triangle me-1"></i>
																		{log.error_message.substring(0, 30)}...
																	</div>
																)}
															</div>
														</div>
													</td>
													<td className="px-3 py-2">
														<span className="badge bg-info">
															{log.run_duration
																? `${log.run_duration.toFixed(2)}s`
																: "N/A"}
														</span>
													</td>
													<td className="px-3 py-2">
														<span className="badge bg-warning text-dark">{jobsFound}</span>
													</td>
													<td className="px-3 py-2">
														<span className="badge bg-success">{jobsScraped}</span>
													</td>
													<td className="px-3 py-2">
														<span
															className={`badge ${successRate >= 80 ? "bg-success" : successRate >= 50 ? "bg-warning text-dark" : "bg-danger"}`}
														>
															{successRate}%
														</span>
													</td>
													<td className="px-3 py-2">
														<Badge bg={getStatusBadgeColor(log.is_success)}>
															{log.is_success ? "Success" : "Failed"}
														</Badge>
													</td>
													<td className="px-3 py-2">
														<small className="text-muted">
															{formatTimeAgo(log.run_datetime)}
														</small>
													</td>
												</tr>
											);
										})}
									</tbody>
								</Table>
							)}
						</Card.Body>
					</Card>
				</Col>
			</Row>

			{/* Scraped Jobs Modal */}
			<Modal show={showModal} onHide={handleCloseModal} size="xl" centered>
				<Modal.Header closeButton>
					<Modal.Title>
						<i className="bi bi-collection me-2"></i>
						Scraped Jobs - {selectedLog?.name}
					</Modal.Title>
				</Modal.Header>
				<Modal.Body>
					{modalLoading ? (
						<div className="text-center py-5">
							<Spinner animation="border" role="status" />
							<p className="mt-3">Loading scraped jobs...</p>
						</div>
					) : (
						<div>
							<div className="mb-3 d-flex justify-content-between align-items-center">
								<p className="text-muted mb-0">
									{selectedLog && (
										<>
											Run Date:{" "}
											<strong>{new Date(selectedLog.run_datetime).toLocaleString()}</strong>
											{selectedLog.run_duration && (
												<>
													{" "}
													• Duration: <strong>{selectedLog.run_duration.toFixed(2)}s</strong>
												</>
											)}
										</>
									)}
								</p>
								<Badge bg="primary">{scrapedJobs.length} jobs found</Badge>
							</div>

							{scrapedJobs.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-inbox text-muted" style={{ fontSize: "3rem" }}></i>
									<h5 className="mt-3 text-muted">No scraped jobs found</h5>
									<p className="text-muted">No jobs were found for this service run.</p>
								</div>
							) : (
								<div style={{ maxHeight: "60vh", overflowY: "auto" }}>
									<Table striped hover size="sm">
										<thead className="table-dark sticky-top">
											<tr>
												<th>Job Title</th>
												<th>Company</th>
												<th>Location</th>
												<th>Status</th>
												<th>URL</th>
												<th>Created</th>
											</tr>
										</thead>
										<tbody>
											{scrapedJobs.map((job, index) => (
												<tr key={job.id || index}>
													<td>
														<div className="fw-semibold">{job.title || "Untitled"}</div>
														{job.scrape_error && (
															<small className="text-danger">
																<i className="bi bi-exclamation-triangle me-1"></i>
																{job.scrape_error.substring(0, 50)}...
															</small>
														)}
													</td>
													<td>{job.company || "N/A"}</td>
													<td>{job.location || "N/A"}</td>
													<td>
														<Badge
															bg={getScrapingStatusColor(job.is_scraped, job.is_failed)}
														>
															{getScrapingStatusText(job.is_scraped, job.is_failed)}
														</Badge>
													</td>
													<td>
														{job.url ? (
															<a
																href={job.url}
																target="_blank"
																rel="noopener noreferrer"
																className="btn btn-sm btn-outline-primary"
															>
																<i className="bi bi-box-arrow-up-right"></i>
															</a>
														) : (
															<span className="text-muted">N/A</span>
														)}
													</td>
													<td>
														<small className="text-muted">
															{job.created_at ? formatTimeAgo(job.created_at) : "N/A"}
														</small>
													</td>
												</tr>
											))}
										</tbody>
									</Table>
								</div>
							)}
						</div>
					)}
				</Modal.Body>
				<Modal.Footer>
					<Button variant="secondary" onClick={handleCloseModal}>
						Close
					</Button>
				</Modal.Footer>
			</Modal>
		</Container>
	);
};

export default ServiceLogDashboard;
