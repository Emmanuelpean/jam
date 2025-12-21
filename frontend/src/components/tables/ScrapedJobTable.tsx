import React, { JSX, useState, useEffect } from "react";
import { Button } from "react-bootstrap";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../modals/ScrapedJobModal";
import { JobData, JobDataTransform, ScrapedJobFilter } from "../../services/Schemas";
import { convertToEndOfDay } from "../../utils/TimeUtils";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import ScrapedJobFilterTable from "./ScrapedJobFilterTable";

const ScrapedJobsTable: React.FC<DataTableProps> = ({ columns = [] }: DataTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const [reloadFlag, setReloadFlag] = useState(0);
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

	const refetchMain = (): void => {
		setReloadFlag((prev: number): number => prev + 1);
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
				reloadTrigger={reloadFlag}
				onImportSuccess={onImportSuccess}
				toolbarAddon={
					<Button
						style={{ height: "100%" }}
						variant="outline-primary"
						onClick={(): void => setShowFilters(true)}
					>
						Filters (
						{
							dataContext.scrapedJobFilters.filter(
								(filter: ScrapedJobFilter): boolean => filter.is_active,
							).length
						}
						)
					</Button>
				}
				modalProps={{
					fetchTrigger: refetchMain,
				}}
			/>
			<ScrapedJobFilterTable
				show={showFilters}
				onHide={(): void => {
					setShowFilters(false);
					refetchMain();
				}}
			/>
		</>
	);
};

export default ScrapedJobsTable;
