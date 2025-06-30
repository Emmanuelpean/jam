import React from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/TableSystem";
import { KeywordFormModal, KeywordViewModal } from "../components/modals/keyword/KeywordModal";
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

	const tableColumns = [columns.name(), columns.createdAt()];

	return (
		<GenericTableWithModals
			title="Tags"
			data={keywords}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={loading}
			error={error}
			FormModal={KeywordFormModal}
			ViewModal={KeywordViewModal}
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
