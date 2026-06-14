import React, { useEffect, useRef, useState, JSX } from "react";
import { Button, Modal } from "react-bootstrap";
import JamModal from "../../components/JamModal/JamModal";
import {
	WIDGET_TYPE_DEFS,
	WidgetConfig,
	WidgetType,
	WidgetTypeDef,
	GraphField,
	GraphConfig,
	GraphSource,
	MapMetric,
	MetricVariant,
	TableVariant,
	TimelineVariant,
	WidgetInstance,
	VariantDef,
	configToVariantKey,
	ChartType,
} from "./widgetRegistry";
import { getSourceForField, GRAPH_SOURCES, GraphFieldMeta } from "./graphAggregations";
import { CustomSelect } from "../../components/rendering/widgets/CustomSelect";
import { SelectOption } from "../../components/rendering/form/FormOptions";

interface WidgetPickerModalProps {
	show: boolean;
	onHide: () => void;
	onAddWidget: (config: WidgetConfig) => void;
	isPremium: boolean;
	currentWidgets: WidgetInstance[];
}

const WidgetPickerModal: React.FC<WidgetPickerModalProps> = ({
	show,
	onHide,
	onAddWidget,
	isPremium,
	currentWidgets,
}: WidgetPickerModalProps): JSX.Element => {
	const [selectedType, setSelectedType] = useState<WidgetType | null>(null);
	const [showCustomGraph, setShowCustomGraph] = useState(false);
	const [draftSource, setDraftSource] = useState<GraphSource>("jobs");
	const [draftField, setDraftField] = useState<GraphField | null>(null);
	const [draftChartType, setDraftChartType] = useState<"line" | "bar" | "pie" | undefined>(undefined);
	const [draftGranularity, setDraftGranularity] = useState<"week" | "month">("month");
	const [draftGroupBy, setDraftGroupBy] = useState<"platform" | "alert_name" | "platform_and_alert">("platform");

	const contentRef = useRef<HTMLDivElement>(null);
	const [contentHeight, setContentHeight] = useState<number | "auto">("auto");
	const usedKeys = new Set(currentWidgets.map((w: WidgetInstance): string => configToVariantKey(w.config)));

	useEffect(() => {
		if (!show) return;
		const el: HTMLDivElement | null = contentRef.current;
		if (!el) return;
		setContentHeight(el.scrollHeight);
		const ro = new ResizeObserver(() => setContentHeight(el.scrollHeight));
		ro.observe(el);
		return () => ro.disconnect();
	}, [show, selectedType, showCustomGraph]);

	const handleClose = () => {
		setSelectedType(null);
		setShowCustomGraph(false);
		setDraftSource("jobs");
		setDraftField(null);
		setDraftChartType(undefined);
		setDraftGranularity("month");
		setDraftGroupBy("platform");
		onHide();
	};

	const handleAddVariant = (typeDef: WidgetTypeDef, variantKey: string) => {
		let config: WidgetConfig;
		switch (typeDef.type) {
			case "metric":
				config = { type: "metric", metric: variantKey as MetricVariant };
				break;
			case "table":
				config = { type: "table", source: variantKey as TableVariant };
				break;
			case "timeline":
				config = { type: "timeline", feed: variantKey as TimelineVariant };
				break;
			case "graph": {
				const field = variantKey as GraphField;
				config = { type: "graph", source: getSourceForField(field), field };
				break;
			}
			case "map":
				config = { type: "map", metric: variantKey as MapMetric };
				break;
		}
		onAddWidget(config);
		handleClose();
	};

	const handleAddCustomGraph = () => {
		if (!draftField) return;
		const fieldMeta: GraphFieldMeta | undefined = GRAPH_SOURCES[draftSource].fields.find(
			(f: GraphFieldMeta): boolean => f.key === draftField
		);
		const config: GraphConfig = {
			type: "graph",
			source: draftSource,
			field: draftField,
			chartType: draftChartType ?? fieldMeta?.defaultChartType,
			...(fieldMeta?.supportsGranularity && { granularity: draftGranularity }),
			...(draftSource === "scraped_jobs" && { groupBy: draftGroupBy }),
		};
		onAddWidget(config);
		handleClose();
	};

	const handleSourceChange = (source: GraphSource): void => {
		setDraftSource(source);
		setDraftField(null);
		setDraftChartType(undefined);
	};

	const handleFieldChange = (field: GraphField): void => {
		setDraftField(field);
		const fieldMeta: GraphFieldMeta | undefined = GRAPH_SOURCES[draftSource].fields.find(
			(f: GraphFieldMeta): boolean => f.key === field
		);
		setDraftChartType(fieldMeta?.defaultChartType);
	};

	const currentTypeDef: WidgetTypeDef | null | undefined = selectedType
		? WIDGET_TYPE_DEFS.find((t: WidgetTypeDef): boolean => t.type === selectedType)
		: null;

	const grid3: React.CSSProperties = { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.5rem" };

	const renderVariantsGrouped = (typeDef: WidgetTypeDef, extraCards?: JSX.Element[]): JSX.Element => {
		const hasGroups = typeDef.variants.some((v) => v.group);
		const extraSection = extraCards?.length ? (
			<div key="__extra">
				<div className="widget-picker-group-label">Custom</div>
				<div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
					{extraCards.map((card, i) => <div key={i} style={{ width: "100%" }}>{card}</div>)}
				</div>
			</div>
		) : null;

		if (!hasGroups) {
			return (
				<div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
					<div style={grid3}>
						{typeDef.variants.map((v) => renderVariantCard(v, typeDef))}
					</div>
					{extraSection}
				</div>
			);
		}
		const groupMap = new Map<string, VariantDef[]>();
		for (const v of typeDef.variants) {
			const g = v.group ?? "";
			if (!groupMap.has(g)) groupMap.set(g, []);
			groupMap.get(g)!.push(v);
		}
		return (
			<div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
				{Array.from(groupMap.entries()).map(([groupName, variants]) => (
					<div key={groupName}>
						{groupName && <div className="widget-picker-group-label">{groupName}</div>}
						<div style={grid3}>
							{variants.map((v) => renderVariantCard(v, typeDef))}
						</div>
					</div>
				))}
				{extraSection}
			</div>
		);
	};

	const cardBase: React.CSSProperties = {
		display: "flex",
		flexDirection: "column",
		alignItems: "center",
		justifyContent: "center",
		gap: "0.5rem",
		padding: "0.75rem 0.5rem",
		borderRadius: "0.5rem",
		border: "1.5px solid var(--bs-border-color)",
		background: "transparent",
		cursor: "pointer",
		textAlign: "center",
		transition: "border-color 0.15s, background 0.15s",
		width: "100%",
		color: "inherit",
	};

	const cardDisabled: React.CSSProperties = {
		...cardBase,
		opacity: 0.45,
		cursor: "not-allowed",
	};

	const renderVariantCard = (variant: VariantDef, typeDef: WidgetTypeDef): JSX.Element => {
		const locked: boolean = variant.premiumOnly && !isPremium;
		return (
			<button
				key={variant.key}
				id={`widget-picker-variant-${variant.key}`}
				style={locked ? cardDisabled : cardBase}
				className="widget-picker-card"
				onClick={(): false | void => !locked && handleAddVariant(typeDef, variant.key)}
				disabled={locked}
			>
				<i className={`bi bi-${variant.icon}`} style={{ fontSize: "1.4rem", color: "var(--primary-mid)" }}></i>
				<div className="fw-semibold" style={{ fontSize: "0.85rem" }}>
					{variant.label}
				</div>
				{variant.description && (
					<small className="text-muted" style={{ fontSize: "0.72rem", lineHeight: 1.3 }}>
						{variant.description}
					</small>
				)}
				{locked && (
					<span className="badge" style={{ background: "var(--primary-gradient)", fontSize: "0.65rem" }}>
						<i className="bi bi-star-fill me-1"></i>Premium
					</span>
				)}
				{usedKeys.has(variant.key) && (
					<span className="badge bg-success" style={{ fontSize: "0.65rem" }}>
						<i className="bi bi-check2 me-1"></i>Added
					</span>
				)}
			</button>
		);
	};

	// Custom graph dropdown options
	const availableSources: GraphSource[] = (Object.keys(GRAPH_SOURCES) as GraphSource[]).filter(
		(src: GraphSource): boolean => isPremium || src !== "scraped_jobs"
	);
	const sourceOptions: SelectOption[] = availableSources.map(
		(src: GraphSource): SelectOption => ({
			value: src,
			label: GRAPH_SOURCES[src].label,
		})
	);
	const fieldOptions: SelectOption[] = GRAPH_SOURCES[draftSource].fields.map(
		(f: GraphFieldMeta): SelectOption => ({
			value: f.key,
			label: f.label,
		})
	);
	const draftFieldMeta: GraphFieldMeta | null | undefined = draftField
		? GRAPH_SOURCES[draftSource].fields.find((f: GraphFieldMeta): boolean => f.key === draftField)
		: null;
	const chartTypeOptions: SelectOption[] = (draftFieldMeta?.supportedChartTypes ?? []).map(
		(ct: ChartType): SelectOption => ({
			value: ct,
			label: ct.charAt(0).toUpperCase() + ct.slice(1),
		})
	);
	const granularityOptions: SelectOption[] = [
		{ value: "week", label: "Week" },
		{ value: "month", label: "Month" },
	];
	const groupByOptions: SelectOption[] = [
		{ value: "platform", label: "Platform" },
		{ value: "alert_name", label: "Alert Name" },
		{ value: "platform_and_alert", label: "Platform & Alert" },
	];

	const getTitle = (): string => {
		if (showCustomGraph) return "Custom Graph";
		if (selectedType) return `Add ${currentTypeDef?.label} Widget`;
		return "Add Widget";
	};

	const handleBack = (): void => {
		if (showCustomGraph) {
			setShowCustomGraph(false);
		} else {
			setSelectedType(null);
		}
	};

	const showBack: boolean = selectedType !== null;

	return (
		<JamModal show={show} onHide={handleClose} centered>
			<Modal.Header closeButton>
				<Modal.Title style={{ overflow: "visible" }}>
					{showBack ? (
						<>
							<Button
								variant="link"
								className="me-2"
								onClick={handleBack}
								style={{
									color: "var(--bs-heading-color, var(--bs-body-color)) !important",
									fontSize: "1.2rem",
									padding: "2px 4px",
									margin: "-2px 0",
								}}
							>
								<i className="bi bi-arrow-left" style={{ color: "white" }}></i>
							</Button>
							{getTitle()}
						</>
					) : (
						getTitle()
					)}
				</Modal.Title>
			</Modal.Header>
			<Modal.Body className="p-0">
				<div
					className="modal-content-animated"
					style={{ height: contentHeight !== "auto" ? contentHeight : undefined }}
				>
					<div ref={contentRef} className="p-3">
						{!selectedType ? (
							// Level 1: widget type picker
							<div style={grid3}>
								{WIDGET_TYPE_DEFS.map((typeDef: WidgetTypeDef): JSX.Element => {
									const allPremium: boolean =
										!isPremium && typeDef.variants.every((v: VariantDef): boolean => v.premiumOnly);
									return (
										<button
											key={typeDef.type}
											id={`widget-picker-type-${typeDef.type}`}
											style={allPremium ? cardDisabled : cardBase}
											className="widget-picker-card"
											onClick={(): false | void => !allPremium && setSelectedType(typeDef.type)}
											disabled={allPremium}
										>
											<div
												style={{
													width: 44,
													height: 44,
													borderRadius: 10,
													background: "var(--primary-gradient)",
													color: "white",
													fontSize: "1.25rem",
													display: "flex",
													alignItems: "center",
													justifyContent: "center",
													flexShrink: 0,
												}}
											>
												<i className={`bi bi-${typeDef.icon}`}></i>
											</div>
											<div className="fw-semibold" style={{ fontSize: "0.9rem" }}>
												{typeDef.label}
											</div>
											<small
												className="text-muted"
												style={{ fontSize: "0.75rem", lineHeight: 1.3 }}
											>
												{typeDef.description}
											</small>
											{allPremium && (
												<span
													className="badge"
													style={{
														background: "var(--primary-gradient)",
														fontSize: "0.65rem",
													}}
												>
													<i className="bi bi-star-fill me-1"></i>Premium
												</span>
											)}
										</button>
									);
								})}
							</div>
						) : showCustomGraph ? (
							// Level 3: custom graph configurator
							<div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
								<div>
									<label
										style={{
											fontSize: "0.78rem",
											fontWeight: 600,
											textTransform: "uppercase",
											letterSpacing: "0.05em",
											color: "var(--bs-secondary-color)",
											marginBottom: "0.3rem",
											display: "block",
										}}
									>
										Source
									</label>
									<CustomSelect
										id="custom-graph-source"
										value={
											sourceOptions.find((o: SelectOption): boolean => o.value === draftSource) ??
											null
										}
										onChange={(opt: SelectOption | SelectOption[] | null): false | void | null =>
											opt && !Array.isArray(opt) && handleSourceChange(opt.value as GraphSource)
										}
										options={sourceOptions}
										isSearchable={false}
										isClearable={false}
									/>
								</div>
								<div>
									<label
										style={{
											fontSize: "0.78rem",
											fontWeight: 600,
											textTransform: "uppercase",
											letterSpacing: "0.05em",
											color: "var(--bs-secondary-color)",
											marginBottom: "0.3rem",
											display: "block",
										}}
									>
										Display
									</label>
									<CustomSelect
										id="custom-graph-field"
										value={
											fieldOptions.find((o: SelectOption): boolean => o.value === draftField) ??
											null
										}
										onChange={(opt: SelectOption | SelectOption[] | null): false | void | null =>
											opt && !Array.isArray(opt) && handleFieldChange(opt.value as GraphField)
										}
										options={fieldOptions}
										isSearchable={false}
										isClearable={false}
										placeholder="Select a field…"
									/>
								</div>
								{draftFieldMeta && draftFieldMeta.supportedChartTypes.length > 1 && (
									<div>
										<label
											style={{
												fontSize: "0.78rem",
												fontWeight: 600,
												textTransform: "uppercase",
												letterSpacing: "0.05em",
												color: "var(--bs-secondary-color)",
												marginBottom: "0.3rem",
												display: "block",
											}}
										>
											Chart Type
										</label>
										<CustomSelect
											id="custom-graph-chart-type"
											value={
												chartTypeOptions.find(
													(o: SelectOption): boolean =>
														o.value === (draftChartType ?? draftFieldMeta.defaultChartType)
												) ?? null
											}
											onChange={(
												opt: SelectOption | SelectOption[] | null
											): false | void | null =>
												opt &&
												!Array.isArray(opt) &&
												setDraftChartType(opt.value as "line" | "bar" | "pie")
											}
											options={chartTypeOptions}
											isSearchable={false}
											isClearable={false}
										/>
									</div>
								)}
								{draftFieldMeta?.supportsGranularity && (
									<div>
										<label
											style={{
												fontSize: "0.78rem",
												fontWeight: 600,
												textTransform: "uppercase",
												letterSpacing: "0.05em",
												color: "var(--bs-secondary-color)",
												marginBottom: "0.3rem",
												display: "block",
											}}
										>
											Period
										</label>
										<CustomSelect
											id="custom-graph-granularity"
											value={
												granularityOptions.find(
													(o: SelectOption): boolean => o.value === draftGranularity
												) ?? null
											}
											onChange={(
												opt: SelectOption | SelectOption[] | null
											): false | void | null =>
												opt &&
												!Array.isArray(opt) &&
												setDraftGranularity(opt.value as "week" | "month")
											}
											options={granularityOptions}
											isSearchable={false}
											isClearable={false}
										/>
									</div>
								)}
								{draftSource === "scraped_jobs" && (
									<div>
										<label
											style={{
												fontSize: "0.78rem",
												fontWeight: 600,
												textTransform: "uppercase",
												letterSpacing: "0.05em",
												color: "var(--bs-secondary-color)",
												marginBottom: "0.3rem",
												display: "block",
											}}
										>
											Group By
										</label>
										<CustomSelect
											id="custom-graph-group-by"
											value={
												groupByOptions.find(
													(o: SelectOption): boolean => o.value === draftGroupBy
												) ?? null
											}
											onChange={(
												opt: SelectOption | SelectOption[] | null
											): false | void | null =>
												opt &&
												!Array.isArray(opt) &&
												setDraftGroupBy(
													opt.value as "platform" | "alert_name" | "platform_and_alert"
												)
											}
											options={groupByOptions}
											isSearchable={false}
											isClearable={false}
										/>
									</div>
								)}
								<Button
									variant="primary"
									disabled={!draftField}
									onClick={handleAddCustomGraph}
									style={{ marginTop: "0.25rem" }}
								>
									Add Widget
								</Button>
							</div>
						) : (
							// Level 2: show variants grouped; graphs show only featured ones + Custom card
							renderVariantsGrouped(
								selectedType === "graph"
									? { ...currentTypeDef!, variants: currentTypeDef!.variants.filter((v) => v.featured) }
									: currentTypeDef!,
								selectedType === "graph"
									? [
											<button
												key="custom-graph"
												id="widget-picker-variant-custom-graph"
												style={cardBase}
												className="widget-picker-card"
												onClick={(): void => setShowCustomGraph(true)}
											>
												<i
													className="bi bi-sliders"
													style={{ fontSize: "1.4rem", color: "var(--primary-mid)" }}
												></i>
												<div className="fw-semibold" style={{ fontSize: "0.85rem" }}>
													Custom
												</div>
												<small className="text-muted" style={{ fontSize: "0.72rem", lineHeight: 1.3 }}>
													Build your own chart
												</small>
											</button>,
										]
									: undefined
							)
						)}
					</div>
				</div>
			</Modal.Body>
		</JamModal>
	);
};

export default WidgetPickerModal;
