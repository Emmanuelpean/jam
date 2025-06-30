import React from "react";
import { AggregatorFormModal, AggregatorViewModal } from "../components/modals/aggregator/AggregatorModal";
import { GenericTableWithModals, useTableData } from "../components/tables/TableSystem";
import { columns } from "../components/rendering/ColumnRenders";

const AggregatorsPage = () => {
	const {
		data: aggregators,
		setData: setAggregators,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("aggregators");

	const tableColumns = [columns.name(), columns.url(), columns.createdAt()];

	return (
		<GenericTableWithModals
			title="Job Aggregators"
			data={aggregators}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={loading}
			error={error}
			FormModal={AggregatorFormModal}
			ViewModal={AggregatorViewModal}
			endpoint="aggregators"
			nameKey="name"
			itemType="Aggregator"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setAggregators}
		/>
	);
};

export default AggregatorsPage;
