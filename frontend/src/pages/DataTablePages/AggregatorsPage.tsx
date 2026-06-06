import React from "react";
import { AggregatorModal } from "../../components/DataModal/AggregatorModal";
import { DataTable } from "../../components/DataTable/DataTable";
import { tableColumns } from "../../components/rendering/view/TableColumns";
import { AggregatorData } from "../../services/schemas/DataTables";

const AggregatorsPage = () => {
	const columns = [
		tableColumns.nameColumn<AggregatorData>(),
		tableColumns.urlColumn<AggregatorData>(),
		tableColumns.jobCountAggregatorColumn<AggregatorData>(),
		tableColumns.jobApplicationCountAggregatorColumn<AggregatorData>(),
		tableColumns.createdAtColumn<AggregatorData>(),
	];

	return (
		<DataTable<AggregatorData>
			entityType="aggregator"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Job Aggregators"
			columns={columns}
			Modal={AggregatorModal}
			enableColumnConfig={true}
		/>
	);
};

export default AggregatorsPage;
