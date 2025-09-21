import React from "react";
import { AggregatorModal } from "../components/modals/AggregatorModal";
import { GenericTable } from "../components/tables/GenericTable";
import { tableColumns } from "../components/rendering/view/TableColumns";

const AggregatorsPage = () => {
	const columns = [
		tableColumns.name(),
		tableColumns.url(),
		tableColumns.jobCount(),
		tableColumns.jobApplicationCount(),
		tableColumns.createdAt(),
	];

	return (
		<GenericTable
			mode="api"
			endpoint="aggregators"
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
