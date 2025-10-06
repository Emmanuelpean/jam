import React from "react";
import DataTable from "../components/tables/DataTable";
import { CompanyModal } from "../components/modals/CompanyModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const CompaniesPage = () => {
	const columns = [
		tableColumns.name(),
		tableColumns.description(),
		tableColumns.url(),
		tableColumns.jobCountCompany(),
		tableColumns.personCountCompany(),
		tableColumns.createdAt(),
	];

	return (
		<DataTable
			entityType="companies"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Companies"
			columns={columns}
			Modal={CompanyModal}
			nameKey="name"
			itemType="Company"
		/>
	);
};

export default CompaniesPage;
