import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../ViewRenders";

const KeywordViewModal = ({ show, onHide, keyword, onEdit }) => {
	if (!keyword) return null;

	const fields = [viewFields.name];

	// Custom content for additional keyword information
	const customContent = (
		<div className="mt-4">
			<div className="row">
				<div className="col-12">
					<div className="card bg-light">
						<div className="card-body text-center">
							<h6 className="card-title mb-2">Keyword</h6>
							<span className="badge bg-secondary fs-6">{keyword.name}</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	);

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
			customContent={customContent}
		/>
	);
};

export default KeywordViewModal;
