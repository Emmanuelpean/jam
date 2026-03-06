import React from "react";
import DataTable from "../../components/DataTable/DataTable";
import { PersonModal } from "../../components/DataModal/PersonModal";
import { tableColumns } from "../../components/rendering/view/TableColumns";

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
			title="People"
			columns={columns}
			Modal={PersonModal}
			enableColumnConfig={true}
		/>
	);
};

export default PersonsPage;
