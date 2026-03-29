import React, { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useDataContext } from "../../contexts/DataContext";
import { MapConfig, MapMetric } from "./widgetRegistry";
import { DashboardCard } from "./DashboardCard";

interface MapDataPoint {
	locationId: number;
	lat: number;
	lng: number;
	label: string;
	value: number;
	jobCount: number;
	topKeywords: string[];
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

interface MapWidgetProps {
	config: MapConfig;
}

const MapWidget: React.FC<MapWidgetProps> = ({ config }) => {
	const ctx = useDataContext();
	const [isDarkMode, setIsDarkMode] = useState<boolean>(
		document.documentElement.getAttribute("data-mode") === "dark"
	);

	useEffect(() => {
		const observer = new MutationObserver(() => {
			setIsDarkMode(document.documentElement.getAttribute("data-mode") === "dark");
		});
		observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-mode"] });
		return () => observer.disconnect();
	}, []);

	const points = useMemo((): MapDataPoint[] => {
		const locationLookup = new Map<number, { lat: number; lng: number; label: string }>();
		for (const loc of ctx.locations) {
			const geo = loc.geolocation;
			if (geo?.latitude != null && geo?.longitude != null) {
				locationLookup.set(loc.id, {
					lat: geo.latitude,
					lng: geo.longitude,
					label: loc.name || loc.city || loc.country || "Unknown",
				});
			}
		}

		const keywordLookup = new Map<number, string>();
		for (const kw of ctx.keywords) {
			keywordLookup.set(kw.id, kw.name);
		}

		const jobsByLocation = new Map<number, typeof ctx.jobs>();
		for (const job of ctx.jobs) {
			if (job.location_id == null || !locationLookup.has(job.location_id)) continue;
			const arr = jobsByLocation.get(job.location_id) ?? [];
			arr.push(job);
			jobsByLocation.set(job.location_id, arr);
		}

		return Array.from(jobsByLocation.entries()).map(([locId, jobs]) => {
			const loc = locationLookup.get(locId)!;
			const jobCount = jobs.length;

			let value = jobCount;
			if (config.metric === "avg_salary") {
				const salaries = jobs
					.map((j) => {
						if (j.salary_min != null && j.salary_max != null) return (j.salary_min + j.salary_max) / 2;
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

			return { locationId: locId, lat: loc.lat, lng: loc.lng, label: loc.label, value, jobCount, topKeywords };
		});
	}, [ctx.jobs, ctx.locations, ctx.keywords, config.metric]);

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

	return (
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
		>
			<MapContainer
				center={[20, 0]}
				zoom={2}
				style={{ height: "100%", width: "100%", flex: 1 }}
				scrollWheelZoom={false}
			>
				<TileLayer attribution={ATTRIBUTION} url={tileUrl} />
				<MapFitter points={points} />
				{points.map((point) => (
					<CircleMarker
						key={point.locationId}
						center={[point.lat, point.lng]}
						radius={getRadius(point.value)}
						pathOptions={{
							fillColor: getColor(point.value),
							color: "white",
							weight: 1.5,
							opacity: 0.9,
							fillOpacity: 0.75,
						}}
					>
						<Popup>
							<div style={{ minWidth: 140 }}>
								<strong>{point.label}</strong>
								<div style={{ marginTop: 4 }}>{formatValue(point)}</div>
								{config.metric === "keywords" && point.topKeywords.length > 0 && (
									<div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 4 }}>
										{point.topKeywords.map((kw) => (
											<span
												key={kw}
												style={{
													background: "#6366f120",
													border: "1px solid #6366f140",
													borderRadius: 4,
													padding: "1px 6px",
													fontSize: 11,
												}}
											>
												{kw}
											</span>
										))}
									</div>
								)}
							</div>
						</Popup>
					</CircleMarker>
				))}
			</MapContainer>
		</DashboardCard>
	);
};

export default MapWidget;
