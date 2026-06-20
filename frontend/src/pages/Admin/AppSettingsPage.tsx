import React, { JSX, useContext, useState } from "react";
import DataTable from "../../components/DataTable/DataTable";
import { ModalHeaderSlotContext } from "../../contexts/ModalHeaderSlotContext";
import { SettingModal } from "../../components/DataModal/SettingModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { SettingData } from "../../services/schemas/Core";
import { getTableIcon } from "../../components/rendering/view/Icons";
import PageHeader from "../PageHeader/PageHeader";

export const AppSettingsPage: React.FC = (): JSX.Element => {
	const headerSlot: HTMLElement | null = useContext(ModalHeaderSlotContext);
	const [settingsCount, setSettingsCount] = useState<number>(0);

	const settingColumns: TableColumn<SettingData>[] = [
		tableColumns.nameColumn<SettingData>(),
		tableColumns.valueColumn<SettingData>(),
		tableColumns.descriptionColumn<SettingData>(),
		tableColumns.isActiveColumn<SettingData>(),
		tableColumns.createdAtColumn<SettingData>(),
	];

	return (
		<div>
			{!headerSlot && <PageHeader title="Settings" icon={getTableIcon("Settings")} count={settingsCount} />}
			<DataTable<SettingData>
				entityType="setting"
				initialSortConfig={{ key: "name", direction: "asc" }}
				columns={settingColumns}
				Modal={SettingModal}
				initialData={{ is_active: true }}
				onTotalCountChange={setSettingsCount}
				enableColumnConfig={true}
			/>
		</div>
	);
};

export default AppSettingsPage;
