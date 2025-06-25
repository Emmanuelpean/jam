import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../../rendering/ViewRenders";

const PersonViewModal = ({ person, show, onHide, onEdit, size }) => {
	if (!person) return null;

	// Define the fields to display in the view modal
	const fields = [
		[viewFields.personName(), viewFields.linkedinUrl()],
		[viewFields.company(), viewFields.role()],
		[viewFields.email(), viewFields.phone()],
	];

	return (
		<GenericModal
			mode="view"
			title="Person"
			fields={fields}
			show={show}
			onHide={onHide}
			size={size}
			data={person}
			onEdit={onEdit}
		/>
	);
};

export default PersonViewModal;
