import React, { JSX, useState } from "react";
import DataTable from "../../components/DataTable/DataTable";
import { FileModal } from "../../components/DataModal/FileModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { useDataContext } from "../../contexts/DataContext";
import { FileData } from "../../services/schemas/DataTables";
import PageHeader from "../PageHeader/PageHeader";

type FileTab = "cv" | "cover_letter";

const FilesPage = (): JSX.Element => {
	const { files } = useDataContext();
	const [activeTab, setActiveTab] = useState<FileTab>("cv");

	const cvCount: number = files.filter((f: FileData): boolean => f.file_type === "cv").length;
	const coverLetterCount: number = files.filter((f: FileData): boolean => f.file_type === "cover_letter").length;

	const columns: TableColumn<FileData>[] = [
		tableColumns.filenameColumn<FileData>(),
		tableColumns.fileUsagesColumn<FileData>(),
		tableColumns.createdAtColumn<FileData>(),
	];

	return (
		<>
			<div className="d-flex gap-3 page-headers-row">
				<PageHeader
					title="CVs"
					icon="file-earmark-person"
					count={cvCount}
					onClick={() => setActiveTab("cv")}
					active={activeTab === "cv"}
					className="flex-fill"
				/>
				<PageHeader
					title="Cover Letters"
					icon="envelope-paper"
					count={coverLetterCount}
					onClick={() => setActiveTab("cover_letter")}
					active={activeTab === "cover_letter"}
					className="flex-fill"
				/>
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
