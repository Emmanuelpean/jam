import React, { JSX, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { DataTable, DataTableHandle } from "../../components/DataTable/DataTable";
import { JobModal } from "../../components/DataModal/JobModal";
import { ExtensionJobData, ExtensionJobModal } from "../../components/DataModal/ExtensionJobModal";
import { DataModalHandle } from "../../components/DataModal/DataModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { useDataContext } from "../../contexts/DataContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { ProgressOverlay } from "../../components/ProgressOverlay/ProgressOverlay";

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
	"ext_deadline",
];

const JobsPage = (): JSX.Element => {
	const [searchParams] = useSearchParams();
	const location = useLocation();
	const navigate = useNavigate();
	const extensionModalRef = useRef<DataModalHandle>(null);
	const tableRef = useRef<DataTableHandle>(null);
	const { deleteEntity, updateEntity } = useDataContext();
	const { showDelete, showConfirm } = useAlert();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [progress, setProgress] = useState<{ show: boolean; title: string; message: string }>({
		show: false,
		title: "",
		message: "",
	});

	const showProgress = (title: string, message: string) => setProgress({ show: true, title, message });
	const hideProgress = () => setProgress((p) => ({ ...p, show: false }));

	const n = (ids: string[]) => `${ids.length} job${ids.length > 1 ? "s" : ""}`;

	const handleBulkDelete = useCallback(
		async (ids: string[]) => {
			const confirmed = await showDelete({
				title: "Delete Jobs",
				message: `Are you sure you want to permanently delete ${n(ids)}? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});
			if (!confirmed) return;
			showProgress("Deleting jobs…", `Deleting ${n(ids)}, please wait.`);
			try {
				await Promise.all(ids.map((id) => deleteEntity("job", Number(id))));
				showToastSuccess(`${n(ids)} deleted.`);
				tableRef.current?.clearSelection();
			} catch {
				showToastError("Failed to delete some jobs. Please try again.");
			} finally {
				hideProgress();
			}
		},
		[deleteEntity, showDelete, showToastSuccess, showToastError]
	);

	const handleBulkSetStatus = useCallback(
		async (ids: string[], status: string | null) => {
			const label = status ? `"${status}"` : "cleared";
			const confirmed = await showConfirm({
				title: "Set Application Status",
				message: `Set status to ${label} for ${n(ids)}?`,
				confirmText: "Confirm",
				cancelText: "Cancel",
			});
			if (!confirmed) return;
			showProgress("Updating status…", `Setting status for ${n(ids)}, please wait.`);
			try {
				await Promise.all(ids.map((id) => updateEntity("job", Number(id), { application_status: status })));
				showToastSuccess(`Status set to ${label} for ${n(ids)}.`);
				tableRef.current?.clearSelection();
			} catch {
				showToastError("Failed to update status for some jobs. Please try again.");
			} finally {
				hideProgress();
			}
		},
		[updateEntity, showConfirm, showToastSuccess, showToastError]
	);

	const handleBulkSnooze = useCallback(
		async (ids: string[], weeks: number) => {
			const confirmed = await showConfirm({
				title: "Snooze Jobs",
				message: `Snooze ${n(ids)} for ${weeks} week${weeks > 1 ? "s" : ""}?`,
				confirmText: "Snooze",
				cancelText: "Cancel",
			});
			if (!confirmed) return;
			showProgress("Snoozing jobs…", `Snoozing ${n(ids)}, please wait.`);
			try {
				const snoozeDate = new Date();
				snoozeDate.setDate(snoozeDate.getDate() + weeks * 7);
				await Promise.all(
					ids.map((id) =>
						updateEntity("job", Number(id), { followup_snooze_datetime: snoozeDate.toISOString() })
					)
				);
				showToastSuccess(`${n(ids)} snoozed for ${weeks} week${weeks > 1 ? "s" : ""}.`);
				tableRef.current?.clearSelection();
			} catch {
				showToastError("Failed to snooze some jobs. Please try again.");
			} finally {
				hideProgress();
			}
		},
		[updateEntity, showConfirm, showToastSuccess, showToastError]
	);

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
			deadline: searchParams.get("ext_deadline") || null,
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
				ref={tableRef}
				entityType="job"
				initialSortConfig={{ key: "created_at", direction: "desc" }}
				title="Jobs"
				columns={columns}
				Modal={JobModal}
				modalSize="xl"
				menuItems={["view", "edit", "delete", "followup"]}
				enableColumnConfig={true}
			/>
			<ExtensionJobModal ref={extensionModalRef} />
			<ProgressOverlay show={progress.show} title={progress.title} message={progress.message} />
		</>
	);
};

export default JobsPage;
