import React, { JSX } from "react";
import DataTable from "../../components/DataTable/DataTable";
import { KeywordModal } from "../../components/DataModal/KeywordModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { KeywordData } from "../../services/schemas/DataTables";

const KeywordsPage = (): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const columns: TableColumn<KeywordData>[] = [
		tableColumns.nameColumn<KeywordData>(),
		tableColumns.jobCountKeywordColumn<KeywordData>(),
		tableColumns.createdAtColumn<KeywordData>(),
	];

	return (
		<DataTable<KeywordData>
			entityType="keyword"
			data={dataContext.keywords}
			endpoint="/keywords"
			columns={columns}
			Modal={KeywordModal}
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Tags"
			enableColumnConfig={true}
		/>
	);
};

export default KeywordsPage;
