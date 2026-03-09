import React, { JSX, useLayoutEffect, useRef, useState } from "react";
import { Modal } from "react-bootstrap";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapingFilterModal } from "../DataModal/ScrapingFilterModal";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { ScrapingFilterData } from "../../services/schemas/Services";

interface ScrapingFilterTableProps extends DataTableProps {
	show: boolean;
	onHide: () => void;
}

type tabKeys = "active" | "inactive";

const ScrapingFilterTable: React.FC<ScrapingFilterTableProps> = ({
	columns = [],
	show,
	onHide,
}: ScrapingFilterTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const [activeTab, setActiveTab] = useState<tabKeys>("active");
	const [containerHeight, setContainerHeight] = useState("auto");
	const contentRef = useRef<HTMLDivElement>(null);

	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.filterTypeColumn(),
					tableColumns.filterOperatorColumn(),
					tableColumns.valueColumn({ type: "text" }),
					tableColumns.caseSensitiveColumn(),
					tableColumns.filteredJobCountColumn(),
				];

	const activeFilters: ScrapingFilterData[] = dataContext.scrapingFilters.filter(
		(filter: ScrapingFilterData): boolean => filter.is_active
	);

	const deactivatedFilters: ScrapingFilterData[] = dataContext.scrapingFilters.filter(
		(filter: ScrapingFilterData): boolean => !filter.is_active
	);

	const tabs: { key: tabKeys; title: string }[] = [
		{ key: "active" as const, title: `Active (${activeFilters.length})` },
		{ key: "inactive" as const, title: `Inactive (${deactivatedFilters.length})` },
	];

	const menuItems = (item: ScrapingFilterData): string[] => {
		if (item.filtered_jobs.length > 0) {
			if (item.is_active) {
				return ["view", "deactivate"];
			} else {
				return ["view", "activate"];
			}
		} else {
			if (item.is_active) {
				return ["view", "edit", "deactivate", "delete"];
			} else {
				return ["view", "edit", "activate", "delete"];
			}
		}
	};

	const renderBodyContent = (): JSX.Element => {
		const data: ScrapingFilterData[] = activeTab === "active" ? activeFilters : deactivatedFilters;
		const showAdd: boolean = activeTab === "active";

		return (
			<div className="modal-content-animated" style={{ height: containerHeight }}>
				<div className="modal-content-animated-inner">
					<div ref={contentRef} style={{ paddingTop: "4px" }}>
						<DataTable
							entityType="scrapingFilter"
							data={data}
							columns={defaultColumns}
							initialSortConfig={{ key: "type", direction: "asc" }}
							Modal={ScrapingFilterModal}
							modalSize="lg"
							showAllEntries={true}
							compact={true}
							initialData={{ is_active: true }}
							menuItems={menuItems}
							defaultModalMode={"view"}
							showAdd={showAdd}
						/>
					</div>
				</div>
			</div>
		);
	};

	useLayoutEffect(() => {
		if (!contentRef.current) return;

		const updateHeight = (): void => {
			if (contentRef.current?.scrollHeight) {
				setContainerHeight(String(Number(contentRef.current.scrollHeight) + 1) + "px");
			}
		};

		updateHeight();

		const resizeObserver = new ResizeObserver((): void => {
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
					)
				)}
			</div>
			<div className="custom-tab-content">{renderBodyContent()}</div>
		</>
	);

	return (
		<Modal
			show={show}
			onHide={onHide}
			size="xl"
			centered={true}
			backdrop={true}
			keyboard={true}
			id={"scraping-filters-modal"}
		>
			<Modal.Header closeButton>
				<Modal.Title>Scraped Job Filters</Modal.Title>
			</Modal.Header>

			<Modal.Body>
				<i style={{ margin: "0 9px 9px 9px", display: "block" }}>
					Filters allow you to filter out specific jobs from your job alerts. For example, if you do not want
					to view jobs from company "ABC Corp", you can create a filter with Type "Company", Operator
					"Equals", and Value "ABC Corp".
				</i>
				{renderTabs()}
			</Modal.Body>
		</Modal>
	);
};

export default ScrapingFilterTable;
