import React from "react";
import DataTable from "../components/tables/DataTable";
import { tableColumns } from "../components/rendering/view/TableColumns";
import { SettingModal } from "../components/modals/SettingModal";

const SettingsPage = () => {
	const columns = [
		tableColumns.name(),
		tableColumns.value(),
		tableColumns.description(),
		tableColumns.isActive(),
		tableColumns.createdAt(),
	];

	return (
		<DataTable
			entityType="settings"
			initialSortConfig={{ key: "name", direction: "asc" }}
			title="Settings"
			columns={columns}
			Modal={SettingModal}
			nameKey="name"
			itemType="Setting"
		/>
	);
};

export default SettingsPage;
