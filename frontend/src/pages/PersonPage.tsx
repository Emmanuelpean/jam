import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable";
import { PersonModal } from "../components/modals/PersonModal";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

const PersonsPage = () => {
	const { showLoading, hideLoading } = useLoading();
	const {
		data: persons,
		setData: setPersons,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("persons", [], {}, { key: "created_at", direction: "desc" });

	const columns = [
		tableColumns.personName!(),
		tableColumns.company!(),
		tableColumns.role!(),
		tableColumns.email!(),
		tableColumns.phone!(),
		tableColumns.linkedinUrl!(),
		tableColumns.createdAt!(),
	];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Persons...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Persons"
			data={persons}
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={PersonModal}
			endpoint="persons"
			nameKey="name"
			itemType="Person"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setPersons}
		/>
	);
};

export default PersonsPage;
