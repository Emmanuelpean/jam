import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../ViewRenders";

const KeywordViewModal = ({ show, onHide, keyword, onEdit }) => {
	if (!keyword) return null;

	const fields = [viewFields.name];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Keyword"
			size="md"
			data={keyword}
			viewFields={fields}
			onEdit={onEdit}
		/>
	);
};

export default KeywordViewModal;
