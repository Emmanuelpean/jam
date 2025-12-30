import React from "react";
import DataTable from "../components/tables/DataTable";
import { CompanyModal } from "../components/modals/CompanyModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const CompaniesPage = () => {
	const columns = [
		tableColumns.nameColumn(),
		tableColumns.descriptionColumn(),
		tableColumns.urlColumn(),
		tableColumns.jobCountCompanyColumn(),
		tableColumns.personCountCompanyColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="company"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Companies"
			columns={columns}
			Modal={CompanyModal}
			itemType="Company"
		/>
	);
};

export default CompaniesPage;
