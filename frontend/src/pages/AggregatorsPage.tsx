import React from "react";
import { AggregatorModal } from "../components/modals/AggregatorModal";
import { DataTable } from "../components/tables/DataTable";
import { tableColumns } from "../components/rendering/view/TableColumns";

const AggregatorsPage = () => {
	const columns = [
		tableColumns.nameColumn(),
		tableColumns.urlColumn(),
		tableColumns.jobCountAggregatorColumn(),
		tableColumns.jobApplicationCountAggregatorColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="aggregator"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Job Aggregators"
			columns={columns}
			Modal={AggregatorModal}
			itemType="Aggregator"
		/>
	);
};

export default AggregatorsPage;
