import React from "react";
import GenericTable from "../components/tables/GenericTable";
import { CompanyModal } from "../components/modals/CompanyModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const CompaniesPage = () => {
	const columns = [
		tableColumns.name(),
		tableColumns.description(),
		tableColumns.url(),
		tableColumns.jobCount(),
		tableColumns.personCount(),
		tableColumns.createdAt(),
	];

	return (
		<GenericTable
			mode="api"
			endpoint="companies"
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
