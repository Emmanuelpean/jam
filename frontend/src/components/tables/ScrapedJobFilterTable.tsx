import React, { JSX } from "react";
import { Modal } from "react-bootstrap";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobFilterModal } from "../modals/ScrapedJobFilterModal";

interface ScrapedJobFilterTableProps extends DataTableProps {
	show: boolean;
	onHide: () => void;
}

const ScrapedJobFilterTable: React.FC<ScrapedJobFilterTableProps> = ({
	columns = [],
	show,
	onHide,
}: ScrapedJobFilterTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.filterTypeColumn(),
					tableColumns.filterOperatorColumn(),
					tableColumns.valueColumn({ type: "text" }),
					tableColumns.isActiveColumn(),
					tableColumns.caseSensitiveColumn(),
				];

	return (
		<Modal show={show} onHide={onHide} size="xl" centered={true} backdrop={true} keyboard={true}>
			<Modal.Header closeButton>
				<Modal.Title>Scraped Job Filters</Modal.Title>
			</Modal.Header>

			<Modal.Body>
				<i style={{ margin: "0 10px 10px 10px", display: "block" }}>
					Filters allow you to filter out specific jobs from your job alerts. For example, if you do not want
					to view jobs from company "ABC Corp", you can create a filter with Type "Company", Operator
					"Equals", and Value "ABC Corp".
				</i>
				<DataTable
					entityType="scrapedJobFilters"
					columns={defaultColumns}
					initialSortConfig={{ key: "type", direction: "asc" }}
					Modal={ScrapedJobFilterModal}
					nameKey="name"
					itemType="Scraping Filters"
					modalSize="lg"
					showAllEntries={true}
					compact={true}
					showSearch={true}
					initialData={{ is_active: true }}
				/>
			</Modal.Body>
		</Modal>
	);
};

export default ScrapedJobFilterTable;
