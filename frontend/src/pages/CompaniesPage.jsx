import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable";
import { CompanyFormModal, CompanyViewModal } from "../components/modals/CompanyModal";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

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

	const tableColumns = [columns.name(), columns.description(), columns.url(), columns.createdAt()];

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
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			FormModal={CompanyFormModal}
			ViewModal={CompanyViewModal}
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
