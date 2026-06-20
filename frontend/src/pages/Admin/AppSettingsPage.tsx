import React, { JSX } from "react";
import DataTable from "../../components/DataTable/DataTable";
import { SettingModal } from "../../components/DataModal/SettingModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { SettingData } from "../../services/schemas/Core";

export const AppSettingsPage = (): JSX.Element => {
	const settingColumns: TableColumn<SettingData>[] = [
		tableColumns.nameColumn<SettingData>(),
		tableColumns.valueColumn<SettingData>(),
		tableColumns.descriptionColumn<SettingData>(),
		tableColumns.isActiveColumn<SettingData>(),
		tableColumns.createdAtColumn<SettingData>(),
	];

	return (
		<div>
			<DataTable<SettingData>
				entityType="setting"
				initialSortConfig={{ key: "name", direction: "asc" }}
				columns={settingColumns}
				Modal={SettingModal}
				initialData={{ is_active: true }}
				enableColumnConfig={true}
			/>
		</div>
	);
};

export default AppSettingsPage;
