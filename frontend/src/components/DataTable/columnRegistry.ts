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
		scrapedJob: [
			tableColumns.titleColumn(),
			tableColumns.scrapedCompanyColumn(),
			tableColumns.scrapedLocationColumn(),
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
			tableColumns.titleColumn({ key: "subject", label: "Subject" }),
			tableColumns.senderColumn(),
			tableColumns.platformColumn(),
			tableColumns.alertNameColumn(),
			tableColumns.jobsFoundColumn(),
			tableColumns.dateReceivedColumn(),
		],
	};
	return _cache;
}

export function getDefaultColumns(entityType: EntityType): TableColumn[] {
	return getDefaultColumnsMap()[entityType] || [];
}

export function getDefaultColumnKeys(entityType: EntityType): string[] {
	return getDefaultColumns(entityType).map((col: TableColumn): string => col.key);
}

export function resolveColumns(entityType: EntityType, keys: string[]): TableColumn[] {
	const defaults: TableColumn[] = getDefaultColumns(entityType);
	return keys
		.map((key: string): TableColumn | undefined => defaults.find((col: TableColumn): boolean => col.key === key))
		.filter((col: TableColumn | undefined): col is TableColumn => col !== undefined);
}
