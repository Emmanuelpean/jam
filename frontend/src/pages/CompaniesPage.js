import React from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import CompanyFormModal from "../components/modals/company/CompanyFormModal";
import CompanyViewModal from "../components/modals/company/CompanyViewModal";
import { useTableData } from "../components/tables/Table";
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

	const tableColumns = [
		columns.name,
		columns.description,
		columns.url,
		columns.createdAt
	];

	return (
		<GenericTableWithModals
			title="Companies"
			data={companies}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			addButtonText="Add Company"
			loading={loading}
			error={error}
			emptyMessage="No companies found"
			FormModal={CompanyFormModal}
			ViewModal={CompanyViewModal}
			endpoint="companies"
			nameKey="name"
			itemType="Company"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setCompanies}
			selectable={true}
		/>
	);
};

export default CompaniesPage;