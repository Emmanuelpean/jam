import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { EntityType, EntityTypeDataMap } from "../../contexts/DataContext";

type ColumnRegistry = { [K in keyof EntityTypeDataMap]?: TableColumn<EntityTypeDataMap[K]>[] };

function getDefaultColumnsMap(): ColumnRegistry {
	return {
		job: [
			tableColumns.titleColumn(),
			tableColumns.companyBadgeColumn(),
			tableColumns.locationBadgeColumn(),
			tableColumns.urlGenericColumn(),
			tableColumns.salaryRangeColumn(),
			tableColumns.personalRatingColumn(),
			tableColumns.isFavouriteColumn(),
			tableColumns.contactBadgesColumn(),
			tableColumns.applicationStatusColumn(),
			tableColumns.interviewCountColumn(),
			tableColumns.jobApplicationUpdateCountColumn(),
			tableColumns.applicationDeadline(),
			tableColumns.sourceAggregatorBadgeColumn(),
			tableColumns.sourceContactBadgeColumn(),
			tableColumns.attendanceTypeColumn(),
			tableColumns.descriptionColumn(),
			tableColumns.noteColumn(),
			tableColumns.createdAtColumn(),
			tableColumns.KeywordBadgeColumn(),
		],
		company: [
			tableColumns.nameColumn(),
			tableColumns.descriptionColumn(),
			tableColumns.urlColumn(),
			tableColumns.jobCountCompanyColumn(),
			tableColumns.personCountCompanyColumn(),
			tableColumns.recruitedJobCountCompanyColumn(),
			tableColumns.createdAtColumn(),
		],
		person: [
			tableColumns.personNameColumn(),
			tableColumns.companyBadgeColumn(),
			tableColumns.roleColumn(),
			tableColumns.emailColumn(),
			tableColumns.phoneColumn(),
			tableColumns.linkedinUrlColumn(),
			tableColumns.isRecruiterColumn(),
			tableColumns.createdAtColumn(),
		],
		interview: [
			tableColumns.jobBadgeColumn(),
			tableColumns.interviewerBadgesColumn(),
			tableColumns.dateColumn(),
			tableColumns.interviewTypeColumn(),
			tableColumns.locationBadgeColumn(),
			tableColumns.noteColumn(),
			tableColumns.createdAtColumn(),
		],
		aggregator: [
			tableColumns.nameColumn(),
			tableColumns.urlColumn(),
			tableColumns.jobCountAggregatorColumn(),
			tableColumns.jobApplicationCountAggregatorColumn(),
			tableColumns.createdAtColumn(),
		],
		keyword: [tableColumns.nameColumn(), tableColumns.jobCountKeywordColumn(), tableColumns.createdAtColumn()],
		jobApplicationUpdate: [
			tableColumns.jobBadgeColumn(),
			tableColumns.dateColumn(),
			tableColumns.updateTypeColumn(),
			tableColumns.noteColumn(),
			tableColumns.createdAtColumn(),
		],
		scrapedJob: [
			tableColumns.titleColumn(),
			tableColumns.scrapedCompanyColumn(),
			tableColumns.locationBadgeColumn(),
			tableColumns.salaryRangeColumn(),
			tableColumns.overallScore(),
			tableColumns.technicalScoreColumn(),
			tableColumns.experienceScoreColumn(),
			tableColumns.educationalScoreColumn(),
			tableColumns.interestScoreColumn(),
			tableColumns.urlGenericColumn(),
			tableColumns.platformColumn(),
			tableColumns.attendanceTypeColumn(),
			tableColumns.descriptionColumn(),
			tableColumns.applicationDeadline(),
			tableColumns.createdAtColumn({ label: "Date Received" }),
		],
		speculativeApplication: [
			tableColumns.companyBadgeColumn(),
			tableColumns.contactEmailColumn(),
			tableColumns.dateColumn(),
			tableColumns.contactBadgesColumn(),
			tableColumns.noteColumn(),
			tableColumns.createdAtColumn(),
		],
		jobEmail: [
			tableColumns.subjectColumn(),
			tableColumns.platformColumn(),
			tableColumns.alertNameColumn(),
			tableColumns.jobsFoundColumn(),
			tableColumns.dateReceivedColumn(),
		],
		user: [
			tableColumns.idColumn(),
			tableColumns.nameColumn(),
			tableColumns.emailColumn(),
			tableColumns.lastLoginColumn(),
			tableColumns.isAdminColumn(),
			tableColumns.isActiveColumn(),
			tableColumns.toastActiveColumn(),
			tableColumns.createdAtColumn(),
		],
		setting: [
			tableColumns.nameColumn(),
			tableColumns.valueColumn(),
			tableColumns.descriptionColumn(),
			tableColumns.isActiveColumn(),
			tableColumns.createdAtColumn(),
		],
	};
}

export function getDefaultColumns(entityType: EntityType | string): TableColumn[] {
	const map: ColumnRegistry = getDefaultColumnsMap();
	return (map[entityType as keyof ColumnRegistry] ?? []) as TableColumn[];
}

export function getDefaultColumnKeys(entityType: EntityType | string): string[] {
	return getDefaultColumns(entityType).map((col: TableColumn): string => col.key);
}

export function resolveColumns(entityType: EntityType | string, keys: string[]): TableColumn[] {
	const defaults: TableColumn[] = getDefaultColumns(entityType);
	return keys
		.map((key: string): TableColumn | undefined => defaults.find((col: TableColumn): boolean => col.key === key))
		.filter((col: TableColumn | undefined): col is TableColumn => col !== undefined);
}
