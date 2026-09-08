import React, { JSX } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import DataTable from "../../components/DataTable/DataTable";
import { FileModal } from "../../components/DataModal/FileModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { useDataContext } from "../../contexts/DataContext";
import { FileData } from "../../services/schemas/DataTables";
import PageHeaderGroup, { PageHeaderTab } from "../PageHeader/PageHeaderGroup";
import { getPageIcon } from "../../components/rendering/view/Icons";

type FileTab = "cv" | "cover_letter";

const FilesPage = (): JSX.Element => {
	const { files } = useDataContext();
	const navigate = useNavigate();
	const location = useLocation();
	const activeTab: FileTab = location.pathname === "/files/cover-letters" ? "cover_letter" : "cv";

	const cvCount: number = files.filter((f: FileData): boolean => f.file_type === "cv").length;
	const coverLetterCount: number = files.filter((f: FileData): boolean => f.file_type === "cover_letter").length;

	const columns: TableColumn<FileData>[] = [
		tableColumns.filenameColumn<FileData>(),
		tableColumns.fileUsagesColumn<FileData>(),
		tableColumns.createdAtColumn<FileData>(),
	];

	const tabs: PageHeaderTab[] = [
		{ id: "cv", title: "CVs", icon: getPageIcon("cvFiles"), count: cvCount },
		{ id: "cover_letter", title: "Cover Letters", icon: getPageIcon("coverLetterFiles"), count: coverLetterCount },
	];

	const tabPaths: Record<FileTab, string> = { cv: "/files/cv", cover_letter: "/files/cover-letters" };

	return (
		<>
			<PageHeaderGroup
				tabs={tabs}
				activeId={activeTab}
				onSelect={(tab: PageHeaderTab): void => void navigate(tabPaths[tab.id as FileTab], { replace: true })}
			/>
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
