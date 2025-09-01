import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable.tsx";
import { PersonModal } from "../components/modals/PersonModal";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext.tsx";

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

	const tableColumns = [
		columns.personName(),
		columns.company(),
		columns.role(),
		columns.email(),
		columns.phone(),
		columns.linkedinUrl(),
		columns.createdAt(),
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
			columns={tableColumns}
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
