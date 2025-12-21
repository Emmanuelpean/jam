import React, { JSX, useState } from "react";
import { Button } from "react-bootstrap";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../modals/ScrapedJobModal";
import { JobData, JobDataTransform } from "../../services/Schemas";
import { convertToEndOfDay } from "../../utils/TimeUtils";
import { useDataContext } from "../../contexts/DataContext";
import ScrapedJobFilterTable from "./ScrapedJobFilterTable";

const ScrapedJobsTable: React.FC<DataTableProps> = ({ columns = [] }: DataTableProps): JSX.Element => {
	const [showFilters, setShowFilters] = useState(false);
	const { addEntity } = useDataContext();
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.scrapedCompanyColumn(),
					tableColumns.scrapedLocationColumn(),
					tableColumns.salaryRangeColumn(),
					tableColumns.overallScore(),
					tableColumns.urlGenericColumn(),
					tableColumns.platformColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	const onImportSuccess = (formData: JobData): Promise<any> => {
		const jobData: Partial<JobDataTransform> = {
			title: formData.title.trim(),
			description: formData.description?.trim() || null,
			note: formData.note?.trim() || null,
			url: formData.url?.trim() || null,
			salary_min: formData.salary_min || null,
			salary_max: formData.salary_max || null,
			personal_rating: formData.personal_rating || null,
			company_id: formData.company_id || null,
			location_id: formData.location_id || null,
			source_id: formData.source_id || null,
			deadline: formData.deadline ? convertToEndOfDay(formData.deadline) : null,
			keywords: formData.keywords || [],
			contacts: formData.contacts || [],
			attendance_type: formData.attendance_type?.trim() || null,
		};
		return addEntity("jobs", jobData);
	};

	return (
		<>
			<DataTable
				entityType="scrapedJobs"
				mode="import"
				columns={defaultColumns}
				initialSortConfig={{ key: "created_at", direction: "desc" }}
				Modal={ScrapedJobModal}
				endpoint="scraped_jobs"
				nameKey="title"
				itemType="Scraped Job"
				modalSize="xl"
				showAdd={false}
				showSearch={true}
				onImportSuccess={onImportSuccess}
				toolbarAddon={
					<Button size="sm" variant="outline-secondary" onClick={() => setShowFilters(true)}>
						Filters
					</Button>
				}
			/>
			<ScrapedJobFilterTable show={showFilters} onHide={() => setShowFilters(false)} />
		</>
	);
};

export default ScrapedJobsTable;
