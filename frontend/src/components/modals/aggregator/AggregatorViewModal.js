import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../../rendering/ViewRenders";

const AggregatorViewModal = ({ show, onHide, aggregator, onEdit, onDelete, size }) => {
	if (!aggregator) return null;

	const fields = [[viewFields.name(), viewFields.url()]];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Aggregator"
			size={size}
			data={aggregator}
			fields={fields}
			onEdit={onEdit}
			onDelete={onDelete}
		/>
	);
};

export default AggregatorViewModal;
