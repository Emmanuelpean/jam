import React from "react";
import DataTable from "../components/tables/DataTable";
import { tableColumns } from "../components/rendering/view/TableColumns";
import { SettingModal } from "../components/DataModal/SettingModal";

const SettingsPage = () => {
	const columns = [
		tableColumns.nameColumn(),
		tableColumns.valueColumn(),
		tableColumns.descriptionColumn(),
		tableColumns.isActiveColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="setting"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Settings"
			columns={columns}
			Modal={SettingModal}
		/>
	);
};

export default SettingsPage;
