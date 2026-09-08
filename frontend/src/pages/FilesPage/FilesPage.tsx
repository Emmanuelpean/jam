import React, { JSX } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import DataTable from "../../components/DataTable/DataTable";
import { FileModal } from "../../components/DataModal/FileModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { useDataContext } from "../../contexts/DataContext";
import { FileData } from "../../services/schemas/DataTables";
import PageHeader from "../PageHeader/PageHeader";
import { useViewport } from "../../contexts/ViewportContext";
import { getEntityIcon, getTableIcon } from "../../components/rendering/view/Icons";

type FileTab = "cv" | "cover_letter";

const FilesPage = (): JSX.Element => {
	const { files } = useDataContext();
	const navigate = useNavigate();
	const location = useLocation();
	const activeTab: FileTab = location.pathname === "/files/cover-letters" ? "cover_letter" : "cv";
	const { isMobile } = useViewport();

	const cvCount: number = files.filter((f: FileData): boolean => f.file_type === "cv").length;
	const coverLetterCount: number = files.filter((f: FileData): boolean => f.file_type === "cover_letter").length;

	const columns: TableColumn<FileData>[] = [
		tableColumns.filenameColumn<FileData>(),
		tableColumns.fileUsagesColumn<FileData>(),
		tableColumns.createdAtColumn<FileData>(),
	];

	const switchTab = (tab: FileTab): void => {
		navigate(tab === "cv" ? "/files/cv" : "/files/cover-letters", { replace: true });
	};

	return (
		<>
			<div className="d-flex gap-3 page-headers-row">
				{(!isMobile || activeTab === "cv") && (
					<PageHeader
						title="CVs"
						icon={getTableIcon("Files")}
						count={cvCount}
						onClick={isMobile ? undefined : (): void => switchTab("cv")}
						active={activeTab === "cv"}
						className="flex-fill"
					/>
				)}
				{(!isMobile || activeTab === "cover_letter") && (
					<PageHeader
						title="Cover Letters"
						icon={getTableIcon("Cover Letters")}
						count={coverLetterCount}
						onClick={isMobile ? undefined : (): void => switchTab("cover_letter")}
						active={activeTab === "cover_letter"}
						className="flex-fill"
					/>
				)}
			</div>
			<DataTable
				entityType="file"
				data={files}
				Modal={FileModal}
				columns={columns}
				showAdd={false}
				initialSortConfig={{ key: "created_at", direction: "desc" }}
				rowFilter={(item: FileData): boolean => (item as FileData).file_type === activeTab}
			/>
		</>
	);
};

export default FilesPage;
