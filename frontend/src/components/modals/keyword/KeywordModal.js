import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";

export const KeywordModal = ({
	show,
	onHide,
	keyword,
	onSuccess,
	onDelete,
	endpoint = "keywords",
	submode = "view",
	size = "md",
}) => {
	// Don't render if we're in view mode but have no keyword data
	if (submode === "view" && !keyword?.id) {
		return null;
	}

	// Form fields for editing
	const formFieldsArray = [[formFields.name({ required: true })]];

	// View fields for display
	const viewFieldsArray = [[viewFields.name()]];

	// Combine them in a way GenericModal can use based on mode
	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		return {
			...data,
			name: data.name?.trim(),
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="formview"
			submode={submode}
			title="Keyword"
			size={size}
			data={keyword || {}}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
		/>
	);
};

export const KeywordFormModal = (props) => {
	// Determine the submode based on whether we have keyword data with an ID
	const submode = props.isEdit || props.keyword?.id ? "edit" : "add";
	return <KeywordModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const KeywordViewModal = (props) => <KeywordModal {...props} submode="view" />;

// Add default export
export default KeywordFormModal;
