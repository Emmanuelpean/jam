import React, { useEffect } from "react";
import { AggregatorFormModal, AggregatorViewModal } from "../components/modals/AggregatorModal";
import { GenericTableWithModals, useTableData } from "../components/tables/TableSystem";
import { columns } from "../components/rendering/ColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

const AggregatorsPage = () => {
	const { showLoading, hideLoading } = useLoading();
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
	} = useTableData("aggregators", [], {}, { key: "name", direction: "asc" });

	const tableColumns = [columns.name(), columns.url(), columns.createdAt()];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Aggregators...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Job Aggregators"
			data={aggregators}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
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
