import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable.tsx";
import { KeywordModal } from "../components/modals/KeywordModal";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext.tsx";

const KeywordsPage = () => {
	const { showLoading, hideLoading } = useLoading();
	const {
		data: keywords,
		setData: setKeywords,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("keywords", [], {}, { key: "name", direction: "asc" });

	const tableColumns = [columns.name(), columns.jobCount(), columns.createdAt()];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Tags...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Tags"
			data={keywords}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={KeywordModal}
			endpoint="keywords"
			nameKey="name"
			itemType="Tag"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setKeywords}
		/>
	);
};

export default KeywordsPage;
