import React, { JSX, useEffect, useMemo, useRef } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { DataTable } from "../../components/DataTable/DataTable";
import { JobModal } from "../../components/DataModal/JobModal";
import { ExtensionJobData, ExtensionJobModal } from "../../components/DataModal/ExtensionJobModal";
import { DataModalHandle } from "../../components/DataModal/DataModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";

const EXT_PARAMS = [
	"ext_title",
	"ext_url",
	"ext_description",
	"ext_salary_min",
	"ext_salary_max",
	"ext_attendance_type",
	"ext_company",
	"ext_location",
	"ext_platform",
	"ext_application_status",
];

const JobsPage = (): JSX.Element => {
	const [searchParams] = useSearchParams();
	const location = useLocation();
	const navigate = useNavigate();
	const extensionModalRef = useRef<DataModalHandle>(null);

	// Pure computation — no side effects. Captures ext_* params on the initial render.
	const autoOpenWith: ExtensionJobData | null = useMemo((): ExtensionJobData | null => {
		const title: string | null = searchParams.get("ext_title");
		if (!title) return null;

		return {
			title,
			url: searchParams.get("ext_url") || null,
			description: searchParams.get("ext_description") || null,
			salary_min: searchParams.get("ext_salary_min") ? Number(searchParams.get("ext_salary_min")) : null,
			salary_max: searchParams.get("ext_salary_max") ? Number(searchParams.get("ext_salary_max")) : null,
			attendance_type: searchParams.get("ext_attendance_type") || null,
			source_type: "aggregator",
			company: searchParams.get("ext_company") || null,
			location: searchParams.get("ext_location") || null,
			platform: searchParams.get("ext_platform") || null,
			application_status: searchParams.get("ext_application_status") || null,
		};
	}, []);

	useEffect((): void => {
		if (!autoOpenWith) return;
		extensionModalRef.current?.showAdd(autoOpenWith);
		const cleaned = new URLSearchParams(searchParams);
		EXT_PARAMS.forEach((k: string): void => cleaned.delete(k));
		const qs: string = cleaned.toString();
		window.history.replaceState(null, "", `${window.location.pathname}${qs ? `?${qs}` : ""}`);
	}, []);

	// Handle job data sent via postMessage from the extension (existing-tab case — no reload)
	useEffect((): void => {
		const extJob = location.state?.extJob as ExtensionJobData | undefined;
		if (!extJob) return;
		extensionModalRef.current?.showAdd(extJob);
		navigate(location.pathname, { replace: true, state: {} });
	}, [location.state?.extJob]); // eslint-disable-line react-hooks/exhaustive-deps

	const columns: TableColumn[] = [
		tableColumns.titleColumn(),
		tableColumns.companyBadgeColumn(),
		tableColumns.locationBadgeColumn(),
		tableColumns.urlGenericColumn(),
		tableColumns.salaryRangeColumn(),
		tableColumns.personalRatingColumn(),
		tableColumns.applicationStatusColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<>
			<DataTable
				entityType="job"
				initialSortConfig={{ key: "created_at", direction: "desc" }}
				title="Jobs"
				columns={columns}
				Modal={JobModal}
				modalSize="xl"
				menuItems={["view", "edit", "delete", "followup"]}
			/>
			<ExtensionJobModal ref={extensionModalRef} />
		</>
	);
};

export default JobsPage;
