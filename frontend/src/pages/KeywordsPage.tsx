import React from "react";
import DataTable from "../components/tables/DataTable";
import { KeywordModal } from "../components/modals/KeywordModal";
import { tableColumns } from "../components/rendering/view/TableColumns";
import { useDataContext } from "../contexts/DataContext";

const KeywordsPage = () => {
	const dataContext = useDataContext();
	const columns = [tableColumns.nameColumn(), tableColumns.jobCountKeywordColumn(), tableColumns.createdAtColumn()];

	return (
		<DataTable
			entityType="keyword"
			data={dataContext.keywords}
			endpoint="/keywords"
			columns={columns}
			Modal={KeywordModal}
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Tags"
		/>
	);
};

export default KeywordsPage;
