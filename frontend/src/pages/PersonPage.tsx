import React from "react";
import GenericTable from "../components/tables/GenericTable";
import { PersonModal } from "../components/modals/PersonModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const PersonsPage = () => {
	const columns = [
		tableColumns.personName(),
		tableColumns.company(),
		tableColumns.role(),
		tableColumns.email(),
		tableColumns.phone(),
		tableColumns.linkedinUrl(),
		tableColumns.createdAt(),
	];

	return (
		<GenericTable
			mode="api"
			endpoint="persons"
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
