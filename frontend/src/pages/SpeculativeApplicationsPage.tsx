import React, { JSX } from "react";
import { DataTable } from "../components/tables/DataTable";
import { TableColumn, tableColumns } from "../components/rendering/view/TableColumns";
import { SpeculativeApplicationModal } from "../components/modals/SpeculativeApplicationModal";

const SpeculativeApplicationsPage = (): JSX.Element => {
	const columns: TableColumn[] = [
		tableColumns.companyBadgeColumn(),
		tableColumns.contactEmailColumn(),
		tableColumns.dateColumn(),
		tableColumns.contactBadgesColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="speculativeApplication"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Speculative Applications"
			columns={columns}
			Modal={SpeculativeApplicationModal}
			nameKey="company_id"
			itemType="Speculative Application"
			modalSize="xl"
		/>
	);
};

export default SpeculativeApplicationsPage;
