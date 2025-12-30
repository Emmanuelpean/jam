import React from "react";
import DataTable from "../components/tables/DataTable";
import { PersonModal } from "../components/modals/PersonModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const PersonsPage = () => {
	const columns = [
		tableColumns.personNameColumn(),
		tableColumns.companyBadgeColumn(),
		tableColumns.roleColumn(),
		tableColumns.emailColumn(),
		tableColumns.phoneColumn(),
		tableColumns.linkedinUrlColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="person"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Persons"
			columns={columns}
			Modal={PersonModal}
			itemType="Person"
		/>
	);
};

export default PersonsPage;
