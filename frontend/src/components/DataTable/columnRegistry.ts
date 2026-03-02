import { TableColumn, tableColumns } from "../rendering/view/TableColumns";

type EntityType = string;

let _cache: Record<EntityType, TableColumn[]> | null = null;

function getDefaultColumnsMap(): Record<EntityType, TableColumn[]> {
	if (_cache) return _cache;
	_cache = {
		job: [
			tableColumns.titleColumn(),
			tableColumns.companyBadgeColumn(),
			tableColumns.locationBadgeColumn(),
			tableColumns.urlGenericColumn(),
			tableColumns.salaryRangeColumn(),
			tableColumns.personalRatingColumn(),
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
		location: [
			tableColumns.nameColumn(),
			tableColumns.cityColumn(),
			tableColumns.postcodeColumn(),
			tableColumns.countryColumn(),
			tableColumns.jobCountLocationColumn(),
			tableColumns.interviewCountLocationColumn(),
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
		speculativeApplication: [
			tableColumns.companyBadgeColumn(),
			tableColumns.contactEmailColumn(),
			tableColumns.dateColumn(),
			tableColumns.contactBadgesColumn(),
			tableColumns.noteColumn(),
			tableColumns.createdAtColumn(),
		],
	};
	return _cache;
}

export function getDefaultColumns(entityType: EntityType): TableColumn[] {
	return getDefaultColumnsMap()[entityType] || [];
}

export function getDefaultColumnKeys(entityType: EntityType): string[] {
	return getDefaultColumns(entityType).map((col) => col.key);
}

export function getColumnByKey(entityType: EntityType, key: string): TableColumn | undefined {
	return getDefaultColumns(entityType).find((col) => col.key === key);
}

export function resolveColumns(entityType: EntityType, keys: string[]): TableColumn[] {
	const defaults = getDefaultColumns(entityType);
	return keys
		.map((key) => defaults.find((col) => col.key === key))
		.filter((col): col is TableColumn => col !== undefined);
}
