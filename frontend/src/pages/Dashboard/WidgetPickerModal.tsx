import React, { useState } from "react";
import { Modal, Button } from "react-bootstrap";
import { WIDGET_TYPE_DEFS, WidgetConfig, WidgetType, WidgetTypeDef, GraphField } from "./widgetRegistry";
import { getSourceForField } from "./graphAggregations";

interface WidgetPickerModalProps {
	show: boolean;
	onHide: () => void;
	onAddWidget: (config: WidgetConfig) => void;
	isPremium: boolean;
}

const WidgetPickerModal: React.FC<WidgetPickerModalProps> = ({ show, onHide, onAddWidget, isPremium }) => {
	const [selectedType, setSelectedType] = useState<WidgetType | null>(null);

	const handleClose = () => {
		setSelectedType(null);
		onHide();
	};

	const handleBack = () => setSelectedType(null);

	const handleAddVariant = (typeDef: WidgetTypeDef, variantKey: string) => {
		let config: WidgetConfig;
		switch (typeDef.type) {
			case "metric":
				config = { type: "metric", metric: variantKey as WidgetConfig & { type: "metric" } extends { metric: infer M } ? M : never };
				break;
			case "table":
				config = { type: "table", source: variantKey as WidgetConfig & { type: "table" } extends { source: infer S } ? S : never };
				break;
			case "timeline":
				config = { type: "timeline", feed: variantKey as WidgetConfig & { type: "timeline" } extends { feed: infer F } ? F : never };
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

	return (
		<Modal show={show} onHide={handleClose} centered>
			<Modal.Header closeButton>
				<Modal.Title>
					{selectedType ? (
						<>
							<Button variant="link" size="sm" className="p-0 me-2" onClick={handleBack}>
								<i className="bi bi-arrow-left"></i>
							</Button>
							Add {currentTypeDef?.label} Widget
						</>
					) : (
						"Add Widget"
					)}
				</Modal.Title>
			</Modal.Header>
			<Modal.Body>
				{!selectedType ? (
					<div className="d-flex flex-column gap-2">
						{WIDGET_TYPE_DEFS.map((typeDef) => {
							const availableVariants = typeDef.variants.filter((v) => !v.premiumOnly || isPremium);
							if (availableVariants.length === 0) return null;
							return (
								<button
									key={typeDef.type}
									className="btn btn-outline-secondary text-start d-flex align-items-center gap-3 p-3"
									onClick={() => setSelectedType(typeDef.type)}
								>
									<div
										className="d-flex align-items-center justify-content-center rounded-3"
										style={{
											width: 44,
											height: 44,
											background: "var(--primary-gradient)",
											color: "white",
											fontSize: "1.2rem",
											flexShrink: 0,
										}}
									>
										<i className={`bi bi-${typeDef.icon}`}></i>
									</div>
									<div>
										<div className="fw-semibold">{typeDef.label}</div>
										<small className="text-muted">{typeDef.description}</small>
									</div>
								</button>
							);
						})}
					</div>
				) : (
					<div className="d-flex flex-column gap-2">
						{currentTypeDef?.variants
							.filter((v) => !v.premiumOnly || isPremium)
							.map((variant, i, arr) => {
								const showGroup = variant.group && (i === 0 || arr[i - 1]?.group !== variant.group);
								return (
									<React.Fragment key={variant.key}>
										{showGroup && (
											<div className="fw-semibold text-muted small mt-2 mb-1">{variant.group}</div>
										)}
										<div className="d-flex align-items-center justify-content-between p-2 border rounded">
											<span className="d-flex align-items-center gap-2">
												<i className={`bi bi-${variant.icon}`}></i>
												{variant.label}
											</span>
											<Button
												variant="primary"
												size="sm"
												onClick={() => handleAddVariant(currentTypeDef, variant.key)}
											>
												Add
											</Button>
										</div>
									</React.Fragment>
								);
							})}
					</div>
				)}
			</Modal.Body>
		</Modal>
	);
};

export default WidgetPickerModal;
