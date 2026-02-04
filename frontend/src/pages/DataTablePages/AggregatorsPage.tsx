import React from "react";
import { AggregatorModal } from "../../components/DataModal/AggregatorModal";
import { DataTable } from "../../components/DataTable/DataTable";
import { tableColumns } from "../../components/rendering/view/TableColumns";

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
		/>
	);
};

export default AggregatorsPage;
