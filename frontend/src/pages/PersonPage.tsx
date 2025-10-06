import React from "react";
import DataTable from "../components/tables/DataTable";
import { PersonModal } from "../components/modals/PersonModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const PersonsPage = () => {
	const columns = [
		tableColumns.personName(),
		tableColumns.companyBadge(),
		tableColumns.role(),
		tableColumns.email(),
		tableColumns.phone(),
		tableColumns.linkedinUrl(),
		tableColumns.createdAt(),
	];

	return (
		<DataTable
			entityType="persons"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Persons"
			columns={columns}
			Modal={PersonModal}
			nameKey="name"
			itemType="Person"
		/>
	);
};

export default PersonsPage;
