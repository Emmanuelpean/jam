import React, { JSX } from "react";
import { DataTable } from "../../components/DataTable/DataTable";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { SpeculativeApplicationModal } from "../../components/DataModal/SpeculativeApplicationModal";

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
			modalSize="xl"
			enableColumnConfig={true}
		/>
	);
};

export default SpeculativeApplicationsPage;
