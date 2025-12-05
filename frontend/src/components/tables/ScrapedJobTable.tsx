import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../modals/ScrapedJobModal";
import { JobData, JobDataTransform } from "../../services/Schemas";
import { convertToEndOfDay } from "../../utils/TimeUtils";
import { useDataContext } from "../../contexts/DataContext";

const ScrapedJobsTable: React.FC<DataTableProps> = ({ columns = [] }: DataTableProps): JSX.Element => {
	const { addEntity } = useDataContext();
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.scrapedCompanyColumn(),
					tableColumns.scrapedLocationColumn(),
					tableColumns.salaryRangeColumn(),
					tableColumns.descriptionColumn(),
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
		/>
	);
};

export default ScrapedJobsTable;
