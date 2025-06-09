import React, { useState } from "react";
import GenericModal from "./GenericModal";

const GenericViewModal = ({
	// View modal props
	show,
	onHide,
	data,
	title,
	size,
	viewFields,
	customContent,
	showSystemFields = true,

	// Edit modal configuration
	FormModalComponent, // The form modal component to use for editing
	endpoint, // API endpoint for updates
	onUpdateSuccess, // Called when item is successfully updated
	formFields = [], // Fields for the form modal
	transformFormData = null,
	customValidation = null,

	// Additional props to pass to form modal
	formModalProps = {},
}) => {
	const [showEditModal, setShowEditModal] = useState(false);
	const [selectedData, setSelectedData] = useState(data);

	// Update selected data when data prop changes
	React.useEffect(() => {
		setSelectedData(data);
	}, [data]);

	// Handle edit button click
	const handleEdit = () => {
		setShowEditModal(true);
		// Don't close view modal
	};

	// Handle edit success
	const handleEditSuccess = (updatedData) => {
		setSelectedData(updatedData); // Update view modal with fresh data
		setShowEditModal(false); // Close edit modal

		// Call parent's update handler if provided
		if (onUpdateSuccess) {
			onUpdateSuccess(updatedData);
		}
	};

	// Handle edit modal close
	const handleEditModalClose = () => {
		setShowEditModal(false);
		// Keep view modal data intact
	};

	// Handle view modal close
	const handleViewModalClose = () => {
		setShowEditModal(false); // Close edit modal if open
		setSelectedData(null);
		onHide();
	};

	if (!selectedData) return null;

	return (
		<>
			{/* View Modal */}
			<GenericModal
				show={show}
				onHide={handleViewModalClose}
				mode="view"
				title={title}
				size={size}
				data={selectedData}
				viewFields={viewFields}
				onEdit={handleEdit}
				showEditButton={true}
				showSystemFields={showSystemFields}
				customContent={customContent}
			/>

			{/* Edit Modal - conditionally rendered */}
			{FormModalComponent && (
				<FormModalComponent
					show={showEditModal}
					onHide={handleEditModalClose}
					onSuccess={handleEditSuccess}
					initialData={selectedData}
					isEdit={true}
					size={size}
					{...formModalProps}
				/>
			)}
		</>
	);
};

export default GenericViewModal;
