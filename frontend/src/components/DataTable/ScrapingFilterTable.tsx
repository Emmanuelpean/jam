import React, { JSX, useLayoutEffect, useRef, useState } from "react";
import { Modal } from "react-bootstrap";
import JamModal from "../JamModal/JamModal";
import { ModalHeader } from "../ModalHeader/ModalHeader";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapingFilterModal } from "../DataModal/ScrapingFilterModal";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { FilterVariant, ScrapingFilterData } from "../../services/schemas/Services";
import { ActionButton } from "../rendering/form/ActionButton";

interface ScrapingFilterTableProps extends DataTableProps {
	show: boolean;
	onHide: () => void;
	variant?: FilterVariant;
}

type tabKeys = "active" | "inactive";

const ScrapingFilterTable: React.FC<ScrapingFilterTableProps> = ({
	columns = [],
	show,
	onHide,
	variant = "exclusion",
}: ScrapingFilterTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const [activeTab, setActiveTab] = useState<tabKeys>("active");
	const [containerHeight, setContainerHeight] = useState("auto");
	const contentRef = useRef<HTMLDivElement>(null);
	const isExclusion = variant === "exclusion";

	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.filterTypeColumn(),
					tableColumns.filterOperatorColumn(),
					tableColumns.valueColumn({ type: "text" }),
					tableColumns.caseSensitiveColumn(),
					...(isExclusion ? [tableColumns.filteredJobCountColumn()] : []),
				];

	const filters = isExclusion ? dataContext.scrapingFilters : dataContext.scrapingFavouriteFilters;
	const activeFilters: ScrapingFilterData[] = filters.filter((f: ScrapingFilterData) => f.is_active);
	const deactivatedFilters: ScrapingFilterData[] = filters.filter((f: ScrapingFilterData) => !f.is_active);

	const tabs: { key: tabKeys; title: string }[] = [
		{ key: "active" as const, title: `Active (${activeFilters.length})` },
		{ key: "inactive" as const, title: `Inactive (${deactivatedFilters.length})` },
	];

	const menuItems = (item: ScrapingFilterData): string[] => {
		if (isExclusion && item.filtered_jobs.length > 0) {
			return item.is_active ? ["view", "deactivate"] : ["view", "activate"];
		}
		return item.is_active ? ["view", "edit", "deactivate", "delete"] : ["view", "edit", "activate", "delete"];
	};

	const renderBodyContent = (): JSX.Element => {
		const data: ScrapingFilterData[] = activeTab === "active" ? activeFilters : deactivatedFilters;
		const showAdd: boolean = activeTab === "active";

		return (
			<div className="modal-content-animated" style={{ height: containerHeight }}>
				<div className="modal-content-animated-inner">
					<div ref={contentRef} style={{ paddingTop: "4px" }}>
						<DataTable
							entityType={isExclusion ? "scrapingFilter" : "scrapingFavouriteFilter"}
							data={data}
							columns={defaultColumns}
							initialSortConfig={{ key: "type", direction: "asc" }}
							Modal={ScrapingFilterModal}
							modalProps={{ variant }}
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
		<div id={isExclusion ? "scraping-filters-tables" : "favourite-filters-tables"}>
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
		</div>
	);

	return (
		<JamModal
			show={show}
			onHide={onHide}
			size="xl"
			centered={true}
			backdrop={true}
			keyboard={true}
			className="data-modal"
		>
			<div id={isExclusion ? "scraping-filters-modal" : "favourite-filters-modal"}>
				<ModalHeader onClose={onHide}>
					<Modal.Title>{isExclusion ? "Scraped Job Filters" : "Favourite Filters"}</Modal.Title>
				</ModalHeader>

				<Modal.Body>
					<i style={{ margin: "0 9px 9px 9px", display: "block" }}>
						{isExclusion
							? 'Filters allow you to filter out specific jobs from your job alerts. For example, if you do not want to view jobs from company "ABC Corp", you can create a filter with Type "Company", Operator "Equals", and Value "ABC Corp".'
							: "Favourite filters pin matching scraped job alerts to this widget. Jobs matching any active filter will appear here."}
					</i>
					{renderTabs()}
				</Modal.Body>
				<Modal.Footer>
					<div className="modal-buttons-container">
						<ActionButton
							id="scraping-filter-modal-close-btn"
							variant="secondary"
							onClick={onHide}
							defaultText="Close"
						/>
					</div>
				</Modal.Footer>
			</div>
		</JamModal>
	);
};

export default ScrapingFilterTable;
