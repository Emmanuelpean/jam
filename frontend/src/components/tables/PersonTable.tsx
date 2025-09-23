import React from "react";
import { GenericTable, GenericTableProps, DataTableProps } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { PersonModal } from "../modals/PersonModal";

const PersonTable: React.FC<DataTableProps> = ({ data = [], onDataChange, error = null, columns = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.personName(),
					tableColumns.role(),
					tableColumns.email(),
					tableColumns.phone(),
					tableColumns.linkedinUrl(),
				];

	// Handle data changes and notify parent
	const handleDataChange = (newData: any[]) => {
		onDataChange?.(newData);
	};

	return (
		<GenericTable
			mode="controlled"
			data={data}
			onDataChange={handleDataChange}
			error={error}
			columns={defaultColumns}
			initialSortConfig={{ key: "name", direction: "asc" }}
			Modal={PersonModal}
			endpoint="persons"
			nameKey="name"
			itemType="Person"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={false}
			showSearch={true}
		/>
	);
};

export default PersonTable;
