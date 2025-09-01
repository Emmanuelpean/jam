import React, { useEffect } from "react";
import { AggregatorModal } from "../components/modals/AggregatorModal";
import { GenericTableWithModals, useTableData } from "../components/tables/GenericTable.tsx";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext.tsx";

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

	const tableColumns = [
		columns.name(),
		columns.url(),
		columns.jobCount(),
		columns.jobApplicationCount(),
		columns.createdAt(),
	];

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
			Modal={AggregatorModal}
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
