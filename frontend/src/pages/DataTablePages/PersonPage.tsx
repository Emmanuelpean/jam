import React from "react";
import DataTable from "../../components/DataTable/DataTable";
import { PersonModal } from "../../components/DataModal/PersonModal";
import { tableColumns } from "../../components/rendering/view/TableColumns";
import { PersonData } from "../../services/schemas/DataTables";

const PersonsPage = () => {
	const columns = [
		tableColumns.personNameColumn<PersonData>(),
		tableColumns.companyBadgeColumn<PersonData>(),
		tableColumns.roleColumn<PersonData>(),
		tableColumns.emailColumn<PersonData>(),
		tableColumns.phoneColumn<PersonData>(),
		tableColumns.linkedinUrlColumn<PersonData>(),
		tableColumns.createdAtColumn<PersonData>(),
	];

	return (
		<DataTable<PersonData>
			entityType="person"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Contacts"
			columns={columns}
			Modal={PersonModal}
			enableColumnConfig={true}
		/>
	);
};

export default PersonsPage;
