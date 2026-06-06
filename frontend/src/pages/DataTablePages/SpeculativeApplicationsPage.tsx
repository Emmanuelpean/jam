import React, { JSX } from "react";
import { DataTable } from "../../components/DataTable/DataTable";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { SpeculativeApplicationModal } from "../../components/DataModal/SpeculativeApplicationModal";
import { SpeculativeApplicationData } from "../../services/schemas/DataTables";

const SpeculativeApplicationsPage = (): JSX.Element => {
	const columns: TableColumn<SpeculativeApplicationData>[] = [
		tableColumns.companyBadgeColumn<SpeculativeApplicationData>(),
		tableColumns.contactEmailColumn<SpeculativeApplicationData>(),
		tableColumns.dateColumn<SpeculativeApplicationData>(),
		tableColumns.contactBadgesColumn<SpeculativeApplicationData>(),
		tableColumns.createdAtColumn<SpeculativeApplicationData>(),
	];

	return (
		<DataTable<SpeculativeApplicationData>
			entityType="speculativeApplication"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Speculative Applications"
			columns={columns}
			Modal={SpeculativeApplicationModal}
			modalSize="lg"
			enableColumnConfig={true}
		/>
	);
};

export default SpeculativeApplicationsPage;
