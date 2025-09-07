import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable.tsx";
import { CompanyModal } from "../components/modals/CompanyModal";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext.tsx";

const CompaniesPage = () => {
	const { showLoading, hideLoading } = useLoading();
	const {
		data: companies,
		setData: setCompanies,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("companies", [], {}, { key: "name", direction: "asc" });

	const columns = [
		tableColumns.name(),
		tableColumns.description(),
		tableColumns.url(),
		tableColumns.jobCount(),
		tableColumns.personCount(),
		tableColumns.createdAt(),
	];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Companies...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Companies"
			data={companies}
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={CompanyModal}
			endpoint="companies"
			nameKey="name"
			itemType="Company"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setCompanies}
		/>
	);
};

export default CompaniesPage;
