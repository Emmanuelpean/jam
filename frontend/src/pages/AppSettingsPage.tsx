import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext";
import { SettingModal } from "../components/modals/SettingModal";

const SettingsPage = () => {
	const { showLoading, hideLoading } = useLoading();
	const {
		data: settings,
		setData: setSettings,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("settings", [], {}, { key: "name", direction: "desc" });

	const columns = [
		tableColumns.name!(),
		tableColumns.value!(),
		tableColumns.description!(),
		tableColumns.createdAt!(),
	];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Settings...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Settings"
			data={settings}
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={SettingModal}
			endpoint="settings"
			nameKey="quantity"
			itemType="Setting"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setSettings}
		/>
	);
};

export default SettingsPage;
