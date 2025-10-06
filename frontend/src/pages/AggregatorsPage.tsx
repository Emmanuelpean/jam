import React from "react";
import { AggregatorModal } from "../components/modals/AggregatorModal";
import { DataTable } from "../components/tables/DataTable";
import { tableColumns } from "../components/rendering/view/TableColumns";

const AggregatorsPage = () => {
	const columns = [
		tableColumns.name(),
		tableColumns.url(),
		tableColumns.jobCountAggregator(),
		tableColumns.jobApplicationCountAggregator(),
		tableColumns.createdAt(),
	];

	return (
		<DataTable
			entityType="aggregators"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Job Aggregators"
			columns={columns}
			Modal={AggregatorModal}
			nameKey="name"
			itemType="Aggregator"
		/>
	);
};

export default AggregatorsPage;
