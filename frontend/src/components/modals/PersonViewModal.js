import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../rendering/ViewRenders";
import Select from "react-select";

const PersonViewModal = ({ person, show, onHide, onEdit, size }) => {
	if (!person) return null;

	// Define the fields to display in the view modal
	const fields = [
		viewFields.personName,
		viewFields.company,
		viewFields.email,
		viewFields.phone,
		viewFields.linkedinUrl,
	];

	return (
		<GenericModal
			mode="view"
			title="Person"
			viewFields={fields}
			show={show}
			onHide={onHide}
			size={size}
			data={person}
			onEdit={onEdit}
		/>
	);
};

export default PersonViewModal;
