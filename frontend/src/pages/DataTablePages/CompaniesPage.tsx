import React from "react";
import DataTable from "../../components/DataTable/DataTable";
import { CompanyModal } from "../../components/DataModal/CompanyModal";
import { tableColumns } from "../../components/rendering/view/TableColumns";
import { CompanyData } from "../../services/schemas/DataTables";

const CompaniesPage = () => {
	const columns = [
		tableColumns.nameColumn<CompanyData>(),
		tableColumns.descriptionColumn<CompanyData>(),
		tableColumns.urlColumn<CompanyData>(),
		tableColumns.jobCountCompanyColumn<CompanyData>(),
		tableColumns.personCountCompanyColumn<CompanyData>(),
		tableColumns.createdAtColumn<CompanyData>(),
	];

	return (
		<DataTable<CompanyData>
			entityType="company"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Companies"
			columns={columns}
			Modal={CompanyModal}
			enableColumnConfig={true}
		/>
	);
};

export default CompaniesPage;
