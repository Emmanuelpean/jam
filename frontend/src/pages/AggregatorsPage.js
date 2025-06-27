import React from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import { AggregatorFormModal, AggregatorViewModal } from "../components/modals/aggregator/AggregatorModal";
import { useTableData } from "../components/tables/Table";
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
			addButtonText="Add Aggregator"
			loading={loading}
			error={error}
			emptyMessage="No job aggregators found"
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
