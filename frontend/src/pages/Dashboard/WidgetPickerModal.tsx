import React, { useEffect, useRef, useState } from "react";
import { Modal, Button } from "react-bootstrap";
import {
	WIDGET_TYPE_DEFS,
	WidgetConfig,
	WidgetType,
	WidgetTypeDef,
	GraphField,
	MetricVariant,
	TableVariant,
	TimelineVariant,
	WidgetInstance,
	configToVariantKey,
} from "./widgetRegistry";
import { getSourceForField } from "./graphAggregations";

interface WidgetPickerModalProps {
	show: boolean;
	onHide: () => void;
	onAddWidget: (config: WidgetConfig) => void;
	isPremium: boolean;
	currentWidgets: WidgetInstance[];
}

const WidgetPickerModal: React.FC<WidgetPickerModalProps> = ({ show, onHide, onAddWidget, isPremium, currentWidgets }) => {
	const [selectedType, setSelectedType] = useState<WidgetType | null>(null);
	const contentRef = useRef<HTMLDivElement>(null);
	const [contentHeight, setContentHeight] = useState<number | "auto">("auto");
	const usedKeys = new Set(currentWidgets.map((w) => configToVariantKey(w.config)));

	useEffect(() => {
		if (!show) return;
		const el = contentRef.current;
		if (!el) return;
		setContentHeight(el.scrollHeight);
		const ro = new ResizeObserver(() => setContentHeight(el.scrollHeight));
		ro.observe(el);
		return () => ro.disconnect();
	}, [show]);

	const handleClose = () => {
		setSelectedType(null);
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
		}
		onAddWidget(config);
		handleClose();
	};

	const currentTypeDef = selectedType ? WIDGET_TYPE_DEFS.find((t) => t.type === selectedType) : null;

	const squareGrid = (count: number): React.CSSProperties => {
		const cols = Math.ceil(Math.sqrt(count));
		return { display: "grid", gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: "0.5rem" };
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

	return (
		<Modal show={show} onHide={handleClose} centered>
			<Modal.Header closeButton>
				<Modal.Title style={{ overflow: "visible" }}>
					{selectedType ? (
						<>
							<Button
								variant="link"
								size="sm"
								className="me-2"
								onClick={() => setSelectedType(null)}
								style={{
									color: "var(--bs-heading-color, var(--bs-body-color)) !important",
									fontSize: "1.2rem",
									padding: "2px 4px",
									margin: "-2px 0",
								}}
							>
								<i className="bi bi-arrow-left"></i>
							</Button>
							Add {currentTypeDef?.label} Widget
						</>
					) : (
						"Add Widget"
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
							<div style={squareGrid(WIDGET_TYPE_DEFS.length)}>
								{WIDGET_TYPE_DEFS.map((typeDef) => {
									const allPremium = !isPremium && typeDef.variants.every((v) => v.premiumOnly);
									return (
										<button
											key={typeDef.type}
											id={`widget-picker-type-${typeDef.type}`}
											style={allPremium ? cardDisabled : cardBase}
											className="widget-picker-card"
											onClick={() => !allPremium && setSelectedType(typeDef.type)}
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
						) : (
							<div style={squareGrid(currentTypeDef?.variants.length ?? 0)}>
								{currentTypeDef?.variants.map((variant) => {
									const locked = variant.premiumOnly && !isPremium;
									return (
										<button
											key={variant.key}
											id={`widget-picker-variant-${variant.key}`}
											style={locked ? cardDisabled : cardBase}
											className="widget-picker-card"
											onClick={() => !locked && handleAddVariant(currentTypeDef, variant.key)}
											disabled={locked}
										>
											<i
												className={`bi bi-${variant.icon}`}
												style={{ fontSize: "1.4rem", color: "var(--primary-mid)" }}
											></i>
											<div className="fw-semibold" style={{ fontSize: "0.85rem" }}>
												{variant.label}
											</div>
											{variant.description && (
												<small className="text-muted" style={{ fontSize: "0.72rem", lineHeight: 1.3 }}>
													{variant.description}
												</small>
											)}
											{locked && (
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
										{usedKeys.has(variant.key) && (
											<span className="badge bg-success" style={{ fontSize: "0.65rem" }}>
												<i className="bi bi-check2 me-1"></i>Added
											</span>
										)}
										</button>
									);
								})}
							</div>
						)}
					</div>
				</div>
			</Modal.Body>
		</Modal>
	);
};

export default WidgetPickerModal;
