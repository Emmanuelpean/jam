import React from "react";
import GenericTable from "../components/tables/GenericTable";
import { KeywordModal } from "../components/modals/KeywordModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const KeywordsPage = () => {
	const columns = [tableColumns.name(), tableColumns.jobCount(), tableColumns.createdAt()];

	return (
		<GenericTable
			mode="api"
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
