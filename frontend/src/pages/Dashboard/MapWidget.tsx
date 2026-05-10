import React, { useEffect, useMemo, useRef, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useDataContext } from "../../contexts/DataContext";
import { MapConfig, MapGranularity, MapMetric } from "./widgetRegistry";
import { DashboardCard } from "./DashboardCard";
import { EnrichedJobData, JobData } from "../../services/schemas/DataTables";
import { JobModal } from "../../components/DataModal/JobModal";
import { DataModalHandle } from "../../components/DataModal/DataModal";

interface MapDataPoint {
	key: string;
	lat: number;
	lng: number;
	label: string;
	value: number;
	jobCount: number;
	topKeywords: string[];
	jobs: EnrichedJobData[];
}

const MAP_TILES = {
	light: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
	dark: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
};
const ATTRIBUTION =
	'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

const lerp = (a: number, b: number, t: number): number => Math.round(a + (b - a) * t);

const salaryColor = (value: number, min: number, max: number): string => {
	if (min >= max) return "#6366f1";
	const t = (value - min) / (max - min);
	if (t < 0.5) {
		const tt = t * 2;
		return `rgb(${lerp(99, 34, tt)},${lerp(102, 197, tt)},${lerp(241, 94, tt)})`;
	}
	const tt = (t - 0.5) * 2;
	return `rgb(${lerp(34, 249, tt)},${lerp(197, 115, tt)},${lerp(94, 22, tt)})`;
};

const MapResizer: React.FC<{ trigger: unknown }> = ({ trigger }) => {
	const map = useMap();
	useEffect(() => {
		const id = setTimeout(() => map.invalidateSize(), 200);
		return () => clearTimeout(id);
	}, [trigger, map]);
	return null;
};

const MapCenterer: React.FC<{ point: MapDataPoint | null }> = ({ point }) => {
	const map = useMap();
	useEffect(() => {
		if (!point || !map) return;
		map.panTo([point.lat, point.lng], { animate: true });
	}, [point, map]);
	return null;
};

const MapFitter: React.FC<{ points: MapDataPoint[] }> = ({ points }) => {
	const map = useMap();
	useEffect(() => {
		if (!map || !map.getContainer() || !map.getPane("mapPane")) return;
		const frameId = requestAnimationFrame(() => {
			map.whenReady(() => {
				try {
					map.stop();
					if (points.length === 0) {
						map.setView([20, 0], 2, { animate: false });
					} else if (points.length === 1) {
						map.setView([points[0]!.lat, points[0]!.lng], 8, { animate: false });
					} else {
						const bounds = L.latLngBounds(points.map((p) => [p.lat, p.lng]));
						map.fitBounds(bounds, { padding: [20, 20], animate: false });
					}
				} catch (e) {
					console.warn("Map fit bounds failed:", e);
				}
			});
		});
		return () => cancelAnimationFrame(frameId);
	}, [points, map]);
	return null;
};

const METRIC_META: Record<MapMetric, { icon: string; title: string }> = {
	job_count: { icon: "pin-map-fill", title: "Jobs by Location" },
	avg_salary: { icon: "cash-stack", title: "Salary by Location" },
	keywords: { icon: "tags", title: "Keywords by Location" },
};

const STATUS_COLORS: Record<string, string> = {
	Applied: "primary",
	Interviewing: "info",
	Offered: "success",
	Rejected: "danger",
	Withdrawn: "secondary",
	Ghosted: "warning",
};

interface MapWidgetProps {
	config: MapConfig;
	onConfigChange?: (config: MapConfig) => void;
}

const MapWidget: React.FC<MapWidgetProps> = ({ config, onConfigChange }) => {
	const ctx = useDataContext();
	const jobModalRef = useRef<DataModalHandle<JobData>>(null);
	const [isDarkMode, setIsDarkMode] = useState<boolean>(
		document.documentElement.getAttribute("data-mode") === "dark"
	);
	const [selectedPoint, setSelectedPoint] = useState<MapDataPoint | null>(null);

	useEffect(() => {
		const observer = new MutationObserver(() => {
			setIsDarkMode(document.documentElement.getAttribute("data-mode") === "dark");
		});
		observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-mode"] });
		return () => observer.disconnect();
	}, []);

	const granularity: MapGranularity = config.granularity ?? "city";

	const companyLookup = useMemo(() => {
		const map = new Map<number, string>();
		for (const c of ctx.companies) map.set(c.id, c.name);
		return map;
	}, [ctx.companies]);

	const points = useMemo((): MapDataPoint[] => {
		const keywordLookup = new Map<number, string>();
		for (const kw of ctx.keywords) {
			keywordLookup.set(kw.id, kw.name);
		}

		const jobsByKey = new Map<string, EnrichedJobData[]>();
		for (const job of ctx.jobs) {
			const geo = job.geolocation;
			if (!geo) continue;
			const key = granularity === "city" ? geo.city : geo.country;
			if (!key) continue;
			const arr = jobsByKey.get(key) ?? [];
			arr.push(job);
			jobsByKey.set(key, arr);
		}

		return Array.from(jobsByKey.entries()).flatMap(([key, jobs]) => {
			const jobsWithGeo = jobs.filter(
				(j) => j.geolocation?.latitude != null && j.geolocation?.longitude != null
			);
			if (jobsWithGeo.length === 0) return [];

			const lat =
				jobsWithGeo.reduce((s, j) => s + j.geolocation!.latitude!, 0) / jobsWithGeo.length;
			const lng =
				jobsWithGeo.reduce((s, j) => s + j.geolocation!.longitude!, 0) / jobsWithGeo.length;

			let value = jobs.length;
			if (config.metric === "avg_salary") {
				const salaries = jobs
					.map((j) => {
						if (j.salary_min != null && j.salary_max != null)
							return (j.salary_min + j.salary_max) / 2;
						return j.salary_min ?? j.salary_max ?? null;
					})
					.filter((s): s is number => s != null);
				value = salaries.length > 0 ? salaries.reduce((a, b) => a + b, 0) / salaries.length : 0;
			}

			const kwCounts = new Map<string, number>();
			for (const job of jobs) {
				for (const kwId of job.keywords) {
					const name = keywordLookup.get(kwId);
					if (name) kwCounts.set(name, (kwCounts.get(name) ?? 0) + 1);
				}
			}
			const topKeywords = Array.from(kwCounts.entries())
				.sort((a, b) => b[1] - a[1])
				.slice(0, 5)
				.map(([name]) => name);

			return [{ key, lat, lng, label: key, value, jobCount: jobs.length, topKeywords, jobs }];
		});
	}, [ctx.jobs, ctx.keywords, config.metric, granularity]);

	const maxValue = Math.max(...points.map((p) => p.value), 1);
	const minValue = Math.min(...points.map((p) => p.value), 0);

	const getRadius = (value: number): number => {
		if (config.metric === "avg_salary") return 10;
		return 6 + Math.sqrt(value / maxValue) * 14;
	};

	const getColor = (value: number): string => {
		if (config.metric === "avg_salary") return salaryColor(value, minValue, maxValue);
		return "#6366f1";
	};

	const formatValue = (point: MapDataPoint): string => {
		if (config.metric === "avg_salary") {
			return point.value > 0 ? `~£${Math.round(point.value).toLocaleString()}` : "No salary data";
		}
		return `${point.jobCount} job${point.jobCount !== 1 ? "s" : ""}`;
	};

	const meta = METRIC_META[config.metric];
	const tileUrl = isDarkMode ? MAP_TILES.dark : MAP_TILES.light;

	const granularityToggle = onConfigChange ? (
		<div className="btn-group btn-group-sm map-granularity-toggle" role="group">
			<button
				type="button"
				className={`btn btn-sm ${granularity === "city" ? "btn-primary" : "btn-outline-secondary"}`}
				style={{ fontSize: "0.75rem", padding: "0.2rem 0.7rem" }}
				onClick={() => onConfigChange({ ...config, granularity: "city" })}
			>
				City
			</button>
			<button
				type="button"
				className={`btn btn-sm ${granularity === "country" ? "btn-primary" : "btn-outline-secondary"}`}
				style={{ fontSize: "0.75rem", padding: "0.2rem 0.7rem" }}
				onClick={() => onConfigChange({ ...config, granularity: "country" })}
			>
				Country
			</button>
		</div>
	) : undefined;

	return (
		<>
			<DashboardCard
				icon={meta.icon}
				title={meta.title}
				isEmpty={points.length === 0}
				emptyState={{
					icon: "geo-alt",
					title: "No location data",
					description: "Add locations to your jobs to see them on the map",
				}}
				bodyPadding={false}
				headerAction={granularityToggle}
			>
				<div style={{ flex: 1, minHeight: 0, overflow: "hidden", display: "flex", flexDirection: "row" }}>
					<MapContainer
						center={[20, 0]}
						zoom={2}
						style={{ height: "100%", flex: 1, minWidth: 0 }}
						scrollWheelZoom={false}
					>
						<TileLayer attribution={ATTRIBUTION} url={tileUrl} />
						<MapFitter points={points} />
						<MapCenterer point={selectedPoint} />
						<MapResizer trigger={selectedPoint?.key} />
						{points.map((point) => {
							const isSelected = selectedPoint?.key === point.key;
							return (
								<CircleMarker
									key={point.key}
									center={[point.lat, point.lng]}
									radius={isSelected ? getRadius(point.value) + 4 : getRadius(point.value)}
									pathOptions={{
										fillColor: getColor(point.value),
										color: isSelected ? "#f59e0b" : "white",
										weight: isSelected ? 3 : 1.5,
										opacity: 1,
										fillOpacity: isSelected ? 1 : 0.75,
									}}
									eventHandlers={{ click: () => setSelectedPoint(point) }}
								/>
							);
						})}
					</MapContainer>

					{selectedPoint && (
						<div className="map-jobs-panel">
							<div className="map-jobs-panel-header">
								<div className="map-jobs-panel-location">
									<div className="map-jobs-panel-location-icon-wrapper">
										<i className={`bi bi-${granularity === "city" ? "geo-alt-fill" : "globe2"}`} />
									</div>
									<div className="map-jobs-panel-location-text">
										<div className="map-jobs-panel-location-name">{selectedPoint.label}</div>
										<div className="map-jobs-panel-location-count">{formatValue(selectedPoint)}</div>
									</div>
								</div>
								<button
									className="btn-close map-jobs-panel-close"
									onClick={() => setSelectedPoint(null)}
									aria-label="Close"
								/>
							</div>
							{config.metric === "keywords" && selectedPoint.topKeywords.length > 0 && (
								<div className="map-jobs-panel-keywords">
									{selectedPoint.topKeywords.map((kw) => (
										<span key={kw} className="map-keyword-badge">
											{kw}
										</span>
									))}
								</div>
							)}
							<div className="map-jobs-panel-list">
								{selectedPoint.jobs.map((job) => {
									const company = job.company_id != null ? companyLookup.get(job.company_id) : null;
									const statusColor = job.application_status
										? (STATUS_COLORS[job.application_status] ?? "secondary")
										: null;
									return (
										<button
											key={job.id}
											className="map-job-item"
											onClick={() => jobModalRef.current?.showView(job)}
										>
											<div className="map-job-item-body">
												<div className="map-job-title" title={job.title}>
													{job.title}
												</div>
												<div className="map-job-meta">
													{company && (
														<span className="map-job-company">
															<i className="bi bi-building" />
															{company}
														</span>
													)}
													{statusColor && (
														<span className={`map-job-status map-job-status--${statusColor}`}>
															{job.application_status}
														</span>
													)}
												</div>
											</div>
											<i className="bi bi-chevron-right map-job-chevron" />
										</button>
									);
								})}
							</div>
						</div>
					)}
				</div>
			</DashboardCard>
			<JobModal ref={jobModalRef} />
		</>
	);
};

export default MapWidget;
