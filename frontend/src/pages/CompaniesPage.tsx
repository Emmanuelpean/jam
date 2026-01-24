import React from "react";
import DataTable from "../components/table/DataTable";
import { CompanyModal } from "../components/DataModal/CompanyModal";
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
		/>
	);
};

export default CompaniesPage;
