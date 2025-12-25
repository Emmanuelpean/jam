import React, { JSX, useState, useLayoutEffect, useRef } from "react";
import { Modal } from "react-bootstrap";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobFilterModal } from "../modals/ScrapedJobFilterModal";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { ScrapedJobFilterData } from "../../services/Schemas";

interface ScrapedJobFilterTableProps extends DataTableProps {
	show: boolean;
	onHide: () => void;
}

const ScrapedJobFilterTable: React.FC<ScrapedJobFilterTableProps> = ({
	columns = [],
	show,
	onHide,
}: ScrapedJobFilterTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const [activeTab, setActiveTab] = useState<"active" | "deleted">("active");
	const [containerHeight, setContainerHeight] = useState("auto");
	const contentRef = useRef<HTMLDivElement>(null);

	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.filterTypeColumn(),
					tableColumns.filterOperatorColumn(),
					tableColumns.valueColumn({ type: "text" }),
					tableColumns.isEnabledColumn(),
					tableColumns.caseSensitiveColumn(),
				];

	const activeFilters: ScrapedJobFilterData[] = dataContext.scrapedJobFilters.filter(
		(filter: ScrapedJobFilterData): boolean => filter.is_active,
	);

	const deletedFilters: ScrapedJobFilterData[] = dataContext.scrapedJobFilters.filter(
		(filter: ScrapedJobFilterData): boolean => !filter.is_active,
	);

	const tabs = [
		{ key: "active" as const, title: `Active (${activeFilters.length})` },
		{ key: "deleted" as const, title: `Deleted (${deletedFilters.length})` },
	];

	const menuItems = (item: ScrapedJobFilterData): string[] => {
		if (item.filtered_jobs.length > 0) {
			return ["detail", "delete"];
		} else {
			return ["detail", "edit", "delete"];
		}
	};

	const canDeactivate = (item: ScrapedJobFilterData): string | null => {
		if (item.filtered_jobs.length > 0) {
			return "it having been used to filter scraped jobs";
		} else {
			return null;
		}
	};

	const renderBodyContent = (): JSX.Element => {
		switch (activeTab) {
			case "active":
				return (
					<div className="modal-content-animated" style={{ height: containerHeight }}>
						<div className="modal-content-animated-inner">
							<div ref={contentRef} style={{ paddingTop: "5px" }}>
								<DataTable
									entityType="scrapedJobFilters"
									data={activeFilters}
									columns={defaultColumns}
									initialSortConfig={{ key: "type", direction: "asc" }}
									Modal={ScrapedJobFilterModal}
									nameKey="name"
									itemType="Scraping Filters"
									modalSize="lg"
									showAllEntries={true}
									compact={true}
									initialData={{ is_enabled: true }}
									menuItems={menuItems}
									defaultModalMode={"detail"}
									canDeactivate={canDeactivate}
								/>
							</div>
						</div>
					</div>
				);
			case "deleted":
				return (
					<div className="modal-content-animated" style={{ height: containerHeight }}>
						<div className="modal-content-animated-inner">
							<div ref={contentRef} style={{ paddingTop: "5px" }}>
								<DataTable
									entityType="scrapedJobFilters"
									data={deletedFilters}
									columns={defaultColumns}
									initialSortConfig={{ key: "type", direction: "asc" }}
									Modal={ScrapedJobFilterModal}
									nameKey="name"
									itemType="Scraping Filters"
									modalSize="lg"
									showAllEntries={true}
									compact={true}
									showAdd={false}
									menuItems={menuItems}
									defaultModalMode={"detail"}
									canDeactivate={canDeactivate}
								/>
							</div>
						</div>
					</div>
				);
			default:
				return <></>;
		}
	};

	useLayoutEffect(() => {
		if (!contentRef.current) return;

		const updateHeight = (): void => {
			if (contentRef.current?.scrollHeight) {
				setContainerHeight(String(Number(contentRef.current.scrollHeight) + 1) + "px");
			}
		};

		updateHeight();

		const resizeObserver = new ResizeObserver(() => {
			updateHeight();
		});

		resizeObserver.observe(contentRef.current);

		const childElements = contentRef.current.querySelectorAll("*");
		childElements.forEach((el: Element) => {
			resizeObserver.observe(el);
		});

		return () => {
			resizeObserver.disconnect();
		};
	}, [activeTab, show]);

	const renderTabs = (): JSX.Element => (
		<>
			<div className="custom-tab-nav">
				{tabs.map(
					(tab): JSX.Element => (
						<button
							key={tab.key}
							id={tab.key + "-tab"}
							type="button"
							className={`custom-tab-button ${activeTab === tab.key ? "active" : ""}`}
							onClick={() => setActiveTab(tab.key)}
						>
							{tab.title}
						</button>
					),
				)}
			</div>
			<div className="custom-tab-content">{renderBodyContent()}</div>
		</>
	);

	return (
		<Modal show={show} onHide={onHide} size="xl" centered={true} backdrop={true} keyboard={true}>
			<Modal.Header closeButton>
				<Modal.Title>Scraped Job Filters</Modal.Title>
			</Modal.Header>

			<Modal.Body>
				<i style={{ margin: "0 10px 10px 10px", display: "block" }}>
					Filters allow you to filter out specific jobs from your job alerts. For example, if you do not want
					to view jobs from company "ABC Corp", you can create a filter with Type "Company", Operator
					"Equals", and Value "ABC Corp".
				</i>
				{renderTabs()}
			</Modal.Body>
		</Modal>
	);
};

export default ScrapedJobFilterTable;
