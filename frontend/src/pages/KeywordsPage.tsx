import React from "react";
import DataTable from "../components/tables/DataTable";
import { KeywordModal } from "../components/modals/KeywordModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const KeywordsPage = () => {
	const columns = [tableColumns.name(), tableColumns.jobCountKeyword(), tableColumns.createdAt()];

	return (
		<DataTable
			entityType="keywords"
			endpoint="keywords"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Tags"
			columns={columns}
			Modal={KeywordModal}
			nameKey="name"
			itemType="Tag"
		/>
	);
};

export default KeywordsPage;
