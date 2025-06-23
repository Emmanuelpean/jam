import React from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import KeywordFormModal from "../components/modals/keyword/KeywordFormModal";
import KeywordViewModal from "../components/modals/keyword/KeywordViewModal";
import { useTableData } from "../components/tables/Table";
import { columns } from "../components/rendering/ColumnRenders";

const KeywordsPage = () => {
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
	} = useTableData("keywords");

	const tableColumns = [
		columns.name(),
		columns.description(),
		columns.createdAt(),
	];

	return (
		<GenericTableWithModals
			title="Keywords"
			data={keywords}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			addButtonText="Add Keyword"
			loading={loading}
			error={error}
			emptyMessage="No keywords found"
			FormModal={KeywordFormModal}
			ViewModal={KeywordViewModal}
			endpoint="keywords"
			nameKey="name"
			itemType="Keyword"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setKeywords}
		/>
	);
};

export default KeywordsPage;