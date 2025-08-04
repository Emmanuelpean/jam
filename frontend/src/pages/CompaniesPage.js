import React from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/TableSystem";
import { CompanyFormModal, CompanyViewModal } from "../components/modals/CompanyModal";
import { columns } from "../components/rendering/ColumnRenders";

const CompaniesPage = () => {
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
	} = useTableData("companies");

	const tableColumns = [columns.name(), columns.description(), columns.url(), columns.createdAt()];

	return (
		<GenericTableWithModals
			title="Companies"
			data={companies}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={loading}
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
