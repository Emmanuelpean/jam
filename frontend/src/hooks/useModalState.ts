import { useState } from "react";

// Define a generic type for items that can be selected
// This allows the hook to work with any type of data
interface UseModalStateReturn<T = any> {
	showModal: boolean;
	showViewModal: boolean;
	showEditModal: boolean;
	selectedItem: T | null;
	openAddModal: () => void;
	closeAddModal: () => void;
	openViewModal: (item: T) => void;
	closeViewModal: () => void;
	openEditModal: (item: T) => void;
	closeEditModal: () => void;
}

const useModalState = <T = any>(): UseModalStateReturn<T> => {
	const [showModal, setShowModal] = useState<boolean>(false);
	const [showViewModal, setShowViewModal] = useState<boolean>(false);
	const [showEditModal, setShowEditModal] = useState<boolean>(false);
	const [selectedItem, setSelectedItem] = useState<T | null>(null);

	const openAddModal = (): void => setShowModal(true);
	const closeAddModal = (): void => setShowModal(false);

	const openViewModal = (item: T): void => {
		setSelectedItem(item);
		setShowViewModal(true);
	};

	const closeViewModal = (): void => {
		setShowViewModal(false);
		// Delay clearing the selected item to allow closing animation
		setTimeout(() => {
			setSelectedItem(null);
		}, 300); // Bootstrap modal animation duration is typically 300ms
	};

	const openEditModal = (item: T): void => {
		setSelectedItem(item);
		setShowEditModal(true);
	};

	const closeEditModal = (): void => {
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
