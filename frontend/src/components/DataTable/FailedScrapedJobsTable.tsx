import React, { JSX, useMemo, useState } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { RenderParams } from "../rendering/view/ViewRenders";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapedJobData } from "../../services/schemas/Services";
import { Badge } from "react-bootstrap";
import { TABLET_BREAKPOINT } from "../../utils/Breakpoints";

interface FailedScrapedJobsTableProps extends DataTableProps {
	dashboardMode?: boolean;
}

const FailedScrapedJobsTable: React.FC<FailedScrapedJobsTableProps> = ({
	title = undefined,
	onTotalCountChange,
	reloadTrigger,
	dashboardMode = false,
}: FailedScrapedJobsTableProps): JSX.Element => {
	const [windowWidth, setWindowWidth] = useState(window.innerWidth);

	React.useEffect(() => {
		const handleResize = (): void => setWindowWidth(window.innerWidth);
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

	const errorTypeColumn: TableColumn = useMemo(
		() => ({
			key: "is_failed",
			label: "Error Type",
			sortable: false,
			render: ({ item }: RenderParams): JSX.Element => {
				const job = item as ScrapedJobData;
				if (job.is_failed) {
					return <Badge bg="danger">Scrape Error</Badge>;
				}
				if (job.job_rating && job.job_rating.is_success === false) {
					return <Badge bg="warning" text="dark">Rating Error</Badge>;
				}
				return <Badge bg="secondary">Unknown</Badge>;
			},
		}),
		[]
	);

	let columns: TableColumn[] = [
		tableColumns.titleColumn(),
		tableColumns.scrapedCompanyColumn(),
		errorTypeColumn,
		tableColumns.platformColumn(),
		tableColumns.createdAtColumn({ label: "Date Received" }),
	];

	if (dashboardMode && windowWidth < TABLET_BREAKPOINT) {
		columns = columns.filter((col) => !["company"].includes(col.key));
	}

	const queryParams = useMemo(() => ({ errors_only: "true" }), []);

	return (
		<DataTable
			title={title}
			entityType="scrapedJob"
			onTotalCountChange={onTotalCountChange}
			mode="import"
			columns={columns}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			Modal={ScrapedJobModal}
			endpoint="scraped-jobs"
			modalSize="xl"
			showAdd={false}
			showSearch={true}
			smallSearch={dashboardMode}
			queryParams={queryParams}
			enableColumnConfig={false}
			reloadTrigger={reloadTrigger}
			enableMultiSelect={false}
			bulkActions={[]}
		/>
	);
};

export default FailedScrapedJobsTable;
