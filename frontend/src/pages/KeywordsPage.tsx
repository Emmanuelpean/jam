import React, { JSX } from "react";
import DataTable from "../components/DataTable/DataTable";
import { KeywordModal } from "../components/DataModal/KeywordModal";
import { TableColumn, tableColumns } from "../components/rendering/view/TableColumns";
import { DataContextValue, useDataContext } from "../contexts/DataContext";

const KeywordsPage = (): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const columns: TableColumn[] = [
		tableColumns.nameColumn(),
		tableColumns.jobCountKeywordColumn(),
		tableColumns.createdAtColumn(),
	];

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
