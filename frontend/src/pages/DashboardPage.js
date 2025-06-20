import React, { useEffect, useState } from "react";
import { Badge, Button, ButtonGroup, Card, Col, Container, ListGroup, Row } from "react-bootstrap";
import { ResponsiveBar } from "@nivo/bar";
import { ResponsivePie } from "@nivo/pie";
import { ResponsiveLine } from "@nivo/line";
import { api } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

const DashboardPage = () => {
	const { token } = useAuth();
	const [chartType, setChartType] = useState("bar");
	const [timeRange, setTimeRange] = useState("month"); // month or week
	const [applicationData, setApplicationData] = useState([]);
	const [recentActivity, setRecentActivity] = useState([]);
	const [timelineData, setTimelineData] = useState([]);
	const [upcomingDeadlines, setUpcomingDeadlines] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		fetchDashboardData();
	}, [token, timeRange]);

	const fetchDashboardData = async () => {
		try {
			setLoading(true);
			setError(null);

			// Fetch all required data
			const [applicationsRes, jobsRes, interviewsRes] = await Promise.all([
				api.get("jobapplications", token),
				api.get("jobs", token),
				api.get("interviews", token),
			]);

			// Process application status data
			processApplicationStatusData(applicationsRes);

			// Process recent activity
			processRecentActivity(applicationsRes, interviewsRes);

			// Process timeline data
			processTimelineData(applicationsRes);

			// Process upcoming deadlines
			processUpcomingDeadlines(jobsRes);
		} catch (err) {
			console.error("Error fetching dashboard data:", err);
			setError("Failed to load dashboard data");
		} finally {
			setLoading(false);
		}
	};

	const processApplicationStatusData = (applications) => {
		const filteredApps = applications.filter((app) => app.status.toLowerCase() !== "rejected");

		const statusCounts = filteredApps.reduce((acc, app) => {
			const status = app.status;
			acc[status] = (acc[status] || 0) + 1;
			return acc;
		}, {});

		const chartData = Object.entries(statusCounts).map(([status, count]) => ({
			id: status,
			label: status,
			value: count,
			status: status,
		}));

		setApplicationData(chartData);
	};

	const processRecentActivity = (applications, interviews) => {
		const activities = [];

		// Add recent applications
		applications.forEach((app) => {
			activities.push({
				id: `app-${app.id}`,
				type: "application",
				title: `Applied to ${app.job?.title || "Unknown Job"}`,
				company: app.job?.company?.name || "Unknown Company",
				date: new Date(app.date),
				status: app.status,
				icon: "bi-briefcase",
			});
		});

		// Add recent interviews
		interviews.forEach((interview) => {
			activities.push({
				id: `interview-${interview.id}`,
				type: "interview",
				title: `${interview.type} Interview`,
				company: interview.job_application?.job?.company?.name || "Unknown Company",
				date: new Date(interview.date),
				status: "scheduled",
				icon: "bi-people",
			});
		});

		// Sort by date (most recent first) and take top 10
		const sortedActivities = activities.sort((a, b) => b.date - a.date).slice(0, 10);

		setRecentActivity(sortedActivities);
	};

	const processTimelineData = (applications) => {
		const now = new Date();
		const dataPoints = [];

		if (timeRange === "month") {
			// Last 12 months
			for (let i = 11; i >= 0; i--) {
				const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
				const nextMonth = new Date(now.getFullYear(), now.getMonth() - i + 1, 1);

				const count = applications.filter((app) => {
					const appDate = new Date(app.date);
					return appDate >= date && appDate < nextMonth;
				}).length;

				dataPoints.push({
					x: date.toLocaleDateString("en-US", { month: "short", year: "2-digit" }),
					y: count,
				});
			}
		} else {
			// Last 12 weeks
			for (let i = 11; i >= 0; i--) {
				const weekEnd = new Date(now.getTime() - i * 7 * 24 * 60 * 60 * 1000);
				const weekStart = new Date(weekEnd.getTime() - 6 * 24 * 60 * 60 * 1000);

				const count = applications.filter((app) => {
					const appDate = new Date(app.date);
					return appDate >= weekStart && appDate <= weekEnd;
				}).length;

				const weekLabel = i === 0 ? "This Week" : i === 1 ? "Last Week" : `${i}w ago`;

				dataPoints.push({
					x: weekLabel,
					y: count,
				});
			}
		}

		setTimelineData([
			{
				id: "applications",
				color: "#3498db",
				data: dataPoints,
			},
		]);
	};

	const processUpcomingDeadlines = (jobs) => {
		const now = new Date();
		const upcomingThreshold = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds

		const upcoming = jobs
			.filter((job) => {
				if (!job.deadline) return false;
				const deadline = new Date(job.deadline);
				const timeUntilDeadline = deadline.getTime() - now.getTime();
				return timeUntilDeadline > 0 && timeUntilDeadline <= upcomingThreshold;
			})
			.map((job) => ({
				...job,
				daysUntilDeadline: Math.ceil(
					(new Date(job.deadline).getTime() - now.getTime()) / (24 * 60 * 60 * 1000),
				),
			}))
			.sort((a, b) => a.daysUntilDeadline - b.daysUntilDeadline);

		setUpcomingDeadlines(upcoming);
	};

	const getColor = (status) => {
		const colorMap = {
			Applied: "#3498db",
			Interview: "#f39c12",
			Offer: "#27ae60",
			Withdrawn: "#95a5a6",
		};
		return colorMap[status] || "#7f8c8d";
	};

	const getActivityIcon = (type) => {
		const iconMap = {
			application: "bi-briefcase",
			interview: "bi-people",
		};
		return iconMap[type] || "bi-circle";
	};

	const formatTimeAgo = (date) => {
		const now = new Date();
		const diffTime = Math.abs(now - date);
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

		if (diffDays === 1) return "1 day ago";
		if (diffDays < 7) return `${diffDays} days ago`;
		if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
		return `${Math.ceil(diffDays / 30)} months ago`;
	};

	const getDeadlineBadgeColor = (days) => {
		if (days <= 3) return "danger";
		if (days <= 7) return "warning";
		if (days <= 14) return "info";
		return "secondary";
	};

	// Enhanced chart theme
	const chartTheme = {
		fontSize: 14,
		fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
		textColor: "#2d3748",
		background: "transparent",
		grid: {
			line: {
				stroke: "#e2e8f0",
				strokeWidth: 1,
			},
		},
		axis: {
			domain: {
				line: {
					stroke: "#cbd5e0",
					strokeWidth: 2,
				},
			},
			ticks: {
				line: {
					stroke: "#cbd5e0",
					strokeWidth: 1,
				},
				text: {
					fontSize: 13,
					fontWeight: 500,
					fill: "#4a5568",
				},
			},
			legend: {
				text: {
					fontSize: 15,
					fontWeight: 600,
					fill: "#2d3748",
				},
			},
		},
		tooltip: {
			container: {
				background: "#ffffff",
				color: "#2d3748",
				fontSize: 13,
				borderRadius: 8,
				boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
				border: "1px solid #e2e8f0",
			},
		},
	};

	// Chart configurations with enhanced styling
	const barChartProps = {
		data: applicationData,
		keys: ["value"],
		indexBy: "status",
		theme: chartTheme,
		margin: { top: 30, right: 30, bottom: 70, left: 80 },
		padding: 0.2,
		colors: ({ indexValue }) => getColor(indexValue),
		borderRadius: 6,
		borderWidth: 2,
		borderColor: {
			from: "color",
			modifiers: [["darker", 0.2]],
		},
		axisBottom: {
			tickSize: 8,
			tickPadding: 8,
			tickRotation: 0,
			legend: "Application Status",
			legendPosition: "middle",
			legendOffset: 50,
		},
		axisLeft: {
			tickSize: 8,
			tickPadding: 8,
			tickRotation: 0,
			legend: "Number of Applications",
			legendPosition: "middle",
			legendOffset: -60,
		},
		enableLabel: true,
		labelSkipWidth: 12,
		labelSkipHeight: 12,
		labelTextColor: "#ffffff",
		labelStyle: {
			fontSize: 14,
			fontWeight: "bold",
		},
		animate: true,
		motionConfig: {
			mass: 1,
			tension: 120,
			friction: 14,
		},
		enableGridY: true,
		gridYValues: 5,
	};

	const pieChartProps = {
		data: applicationData,
		theme: chartTheme,
		margin: { top: 40, right: 80, bottom: 40, left: 80 },
		innerRadius: 0.6,
		padAngle: 1,
		cornerRadius: 4,
		activeOuterRadiusOffset: 12,
		colors: ({ data }) => getColor(data.status),
		borderWidth: 3,
		borderColor: "#ffffff",
		arcLinkLabelsSkipAngle: 5,
		arcLinkLabelsTextColor: "#2d3748",
		arcLinkLabelsThickness: 3,
		arcLinkLabelsColor: { from: "color", modifiers: [["darker", 0.3]] },
		arcLinkLabelsStraightLength: 15,
		arcLinkLabelsTextOffset: 8,
		arcLabelsSkipAngle: 8,
		arcLabelsTextColor: "#ffffff",
		arcLabelsRadiusOffset: 0.55,
		animate: true,
		motionConfig: {
			mass: 1,
			tension: 120,
			friction: 14,
		},
		legends: [
			{
				anchor: "bottom-right",
				direction: "column",
				justify: false,
				translateX: 0,
				translateY: 0,
				itemsSpacing: 8,
				itemWidth: 100,
				itemHeight: 20,
				itemTextColor: "#2d3748",
				itemDirection: "left-to-right",
				itemOpacity: 1,
				symbolSize: 16,
				symbolShape: "circle",
			},
		],
	};

	const lineChartProps = {
		data: timelineData,
		theme: chartTheme,
		margin: { top: 30, right: 30, bottom: 70, left: 80 },
		xScale: { type: "point" },
		yScale: { type: "linear", min: 0, max: "auto" },
		curve: "catmullRom",
		axisTop: null,
		axisRight: null,
		axisBottom: {
			tickSize: 8,
			tickPadding: 8,
			tickRotation: -45,
			legend: "Time Period",
			legendPosition: "middle",
			legendOffset: 55,
		},
		axisLeft: {
			tickSize: 8,
			tickPadding: 8,
			tickRotation: 0,
			legend: "Number of Applications",
			legendPosition: "middle",
			legendOffset: -60,
		},
		pointSize: 12,
		pointColor: "#ffffff",
		pointBorderWidth: 3,
		pointBorderColor: { from: "serieColor" },
		pointLabelYOffset: -16,
		enablePointLabel: true,
		pointLabel: "y",
		pointLabelStyle: {
			fontSize: 12,
			fontWeight: "bold",
		},
		useMesh: true,
		animate: true,
		motionConfig: {
			mass: 1,
			tension: 120,
			friction: 14,
		},
		enableArea: true,
		areaOpacity: 0.15,
		areaBaselineValue: 0,
		lineWidth: 4,
		enableGridX: false,
		enableGridY: true,
		gridYValues: 5,
		crosshairType: "cross",
	};

	const totalApplications = applicationData.reduce((sum, item) => sum + item.value, 0);

	if (loading) {
		return (
			<Container className="mt-4">
				<div className="text-center">
					<div
						className="spinner-border text-primary"
						role="status"
						style={{ width: "3rem", height: "3rem" }}
					>
						<span className="visually-hidden">Loading...</span>
					</div>
					<p className="mt-3 text-muted fs-5">Loading dashboard...</p>
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
			<Row>
				<Col>
					<h1 className="mb-4 fw-bold text-dark">
						<i className="bi bi-graph-up me-3 text-primary"></i>
						Job Applications Dashboard
					</h1>
				</Col>
			</Row>

			{/* Enhanced Summary Cards */}
			<Row className="mb-4">
				<Col md={3}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Body className="text-center p-4">
							<div className="mb-3">
								<i className="bi bi-briefcase-fill text-primary" style={{ fontSize: "2.5rem" }}></i>
							</div>
							<Card.Title className="text-muted fs-6 mb-2">Total Applications</Card.Title>
							<h2 className="text-primary fw-bold mb-2" style={{ fontSize: "2.5rem" }}>
								{totalApplications}
							</h2>
							<small className="text-muted">Excluding rejected</small>
						</Card.Body>
					</Card>
				</Col>
				{applicationData.slice(0, 3).map((item) => (
					<Col md={3} key={item.status}>
						<Card className="h-100 border-0 shadow-sm">
							<Card.Body className="text-center p-4">
								<div className="mb-3">
									<i
										className={`bi ${
											item.status === "Applied"
												? "bi-send-fill"
												: item.status === "Interview"
													? "bi-people-fill"
													: item.status === "Offer"
														? "bi-trophy-fill"
														: "bi-x-circle-fill"
										}`}
										style={{ fontSize: "2.5rem", color: getColor(item.status) }}
									></i>
								</div>
								<Card.Title className="text-muted fs-6 mb-2">{item.status}</Card.Title>
								<h2
									className="fw-bold mb-2"
									style={{ fontSize: "2.5rem", color: getColor(item.status) }}
								>
									{item.value}
								</h2>
								<small className="text-muted">
									{totalApplications > 0 ? Math.round((item.value / totalApplications) * 100) : 0}%
								</small>
							</Card.Body>
						</Card>
					</Col>
				))}
			</Row>

			{/* Main Content Row */}
			<Row className="mb-4">
				{/* Application Status Chart */}
				<Col lg={8}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 d-flex justify-content-between align-items-center p-4">
							<h5 className="mb-0 fw-semibold text-dark">Application Status Distribution</h5>
							<ButtonGroup>
								<Button
									variant={chartType === "bar" ? "primary" : "outline-primary"}
									onClick={() => setChartType("bar")}
									className="px-3"
								>
									<i className="bi bi-bar-chart me-2"></i>
									Bar Chart
								</Button>
								<Button
									variant={chartType === "pie" ? "primary" : "outline-primary"}
									onClick={() => setChartType("pie")}
									className="px-3"
								>
									<i className="bi bi-pie-chart me-2"></i>
									Pie Chart
								</Button>
							</ButtonGroup>
						</Card.Header>
						<Card.Body className="p-4">
							{applicationData.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-inbox text-muted" style={{ fontSize: "4rem" }}></i>
									<h4 className="mt-4 text-muted fw-semibold">No Application Data</h4>
									<p className="text-muted fs-6">Start applying to jobs to see your progress here.</p>
								</div>
							) : (
								<div style={{ height: "350px" }}>
									{chartType === "bar" ? (
										<ResponsiveBar {...barChartProps} />
									) : (
										<ResponsivePie {...pieChartProps} />
									)}
								</div>
							)}
						</Card.Body>
					</Card>
				</Col>

				{/* Recent Activity */}
				<Col lg={4}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 p-4">
							<h5 className="mb-0 fw-semibold text-dark">
								<i className="bi bi-clock-history me-2 text-info"></i>
								Recent Activity
							</h5>
						</Card.Header>
						<Card.Body className="p-0" style={{ maxHeight: "450px", overflowY: "auto" }}>
							{recentActivity.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-clock text-muted" style={{ fontSize: "3rem" }}></i>
									<p className="mt-3 text-muted fw-semibold">No recent activity</p>
								</div>
							) : (
								<ListGroup variant="flush">
									{recentActivity.map((activity) => (
										<ListGroup.Item key={activity.id} className="border-0 px-4 py-3">
											<div className="d-flex align-items-start">
												<div
													className="rounded-circle d-flex align-items-center justify-content-center me-3"
													style={{
														width: "40px",
														height: "40px",
														backgroundColor: getColor(activity.status) + "20",
														color: getColor(activity.status),
													}}
												>
													<i className={`${getActivityIcon(activity.type)} fs-5`}></i>
												</div>
												<div className="flex-grow-1">
													<div className="fw-semibold text-dark mb-1">{activity.title}</div>
													<div className="text-muted small mb-1">{activity.company}</div>
													<div className="text-muted small">
														{formatTimeAgo(activity.date)}
													</div>
												</div>
												<Badge
													className="px-2 py-1"
													style={{
														backgroundColor: getColor(activity.status) + "20",
														color: getColor(activity.status),
														border: `1px solid ${getColor(activity.status)}40`,
													}}
												>
													{activity.status}
												</Badge>
											</div>
										</ListGroup.Item>
									))}
								</ListGroup>
							)}
						</Card.Body>
					</Card>
				</Col>
			</Row>

			{/* Second Row */}
			<Row className="mb-4">
				{/* Applications Timeline */}
				<Col lg={8}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 d-flex justify-content-between align-items-center p-4">
							<h5 className="mb-0 fw-semibold text-dark">
								<i className="bi bi-graph-up me-2 text-success"></i>
								Applications Over Time
							</h5>
							<ButtonGroup>
								<Button
									variant={timeRange === "week" ? "success" : "outline-success"}
									onClick={() => setTimeRange("week")}
									className="px-3"
								>
									Weekly View
								</Button>
								<Button
									variant={timeRange === "month" ? "success" : "outline-success"}
									onClick={() => setTimeRange("month")}
									className="px-3"
								>
									Monthly View
								</Button>
							</ButtonGroup>
						</Card.Header>
						<Card.Body className="p-4">
							{timelineData.length === 0 || timelineData[0]?.data?.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-graph-up text-muted" style={{ fontSize: "4rem" }}></i>
									<h4 className="mt-4 text-muted fw-semibold">No Timeline Data</h4>
									<p className="text-muted fs-6">Start applying to jobs to see trends over time.</p>
								</div>
							) : (
								<div style={{ height: "350px" }}>
									<ResponsiveLine {...lineChartProps} />
								</div>
							)}
						</Card.Body>
					</Card>
				</Col>

				{/* Upcoming Deadlines */}
				<Col lg={4}>
					<Card className="h-100 border-0 shadow-sm">
						<Card.Header className="bg-transparent border-0 p-4">
							<h5 className="mb-0 fw-semibold text-dark">
								<i className="bi bi-calendar-check me-2 text-warning"></i>
								Upcoming Deadlines
								{upcomingDeadlines.length > 0 && (
									<Badge bg="warning" text="dark" className="ms-2">
										{upcomingDeadlines.length}
									</Badge>
								)}
							</h5>
						</Card.Header>
						<Card.Body className="p-0" style={{ maxHeight: "450px", overflowY: "auto" }}>
							{upcomingDeadlines.length === 0 ? (
								<div className="text-center py-5">
									<i className="bi bi-calendar-x text-muted" style={{ fontSize: "3rem" }}></i>
									<p className="mt-3 text-muted fw-semibold">No upcoming deadlines</p>
									<small className="text-muted">All deadlines are more than 30 days away</small>
								</div>
							) : (
								<ListGroup variant="flush">
									{upcomingDeadlines.map((job) => (
										<ListGroup.Item key={job.id} className="border-0 px-4 py-3">
											<div className="d-flex justify-content-between align-items-start">
												<div className="flex-grow-1">
													<div className="fw-semibold text-dark mb-1">{job.title}</div>
													<div className="text-muted small mb-1">
														{job.company?.name || "Unknown Company"}
													</div>
													<div className="text-muted small">
														<i className="bi bi-calendar3 me-1"></i>
														{new Date(job.deadline).toLocaleDateString()}
													</div>
												</div>
												<Badge
													bg={getDeadlineBadgeColor(job.daysUntilDeadline)}
													className="ms-2 px-2 py-1"
												>
													{job.daysUntilDeadline} day{job.daysUntilDeadline !== 1 ? "s" : ""}
												</Badge>
											</div>
										</ListGroup.Item>
									))}
								</ListGroup>
							)}
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
};

export default DashboardPage;
