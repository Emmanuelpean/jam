
import { useState } from 'react';

const useModalState = () => {
	const [showModal, setShowModal] = useState(false);
	const [showViewModal, setShowViewModal] = useState(false);
	const [showEditModal, setShowEditModal] = useState(false);
	const [selectedItem, setSelectedItem] = useState(null);

	const openAddModal = () => setShowModal(true);
	const closeAddModal = () => setShowModal(false);

	const openViewModal = (item) => {
		setSelectedItem(item);
		setShowViewModal(true);
	};

	const closeViewModal = () => {
		setShowViewModal(false);
		// Delay clearing the selected item to allow closing animation
		setTimeout(() => {
			setSelectedItem(null);
		}, 300); // Bootstrap modal animation duration is typically 300ms
	};

	const openEditModal = (item) => {
		setSelectedItem(item);
		setShowEditModal(true);
	};

	const closeEditModal = () => {
		setShowEditModal(false);
		// Delay clearing the selected item to allow closing animation
		setTimeout(() => {
			setSelectedItem(null);
		}, 300); // Bootstrap modal animation duration is typically 300ms
	};

	return {
		showModal,
		showViewModal,
		showEditModal,
		selectedItem,
		openAddModal,
		closeAddModal,
		openViewModal,
		closeViewModal,
		openEditModal,
		closeEditModal,
	};
};

export default useModalState;