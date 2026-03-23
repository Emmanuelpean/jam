import React, { JSX, useLayoutEffect, useRef, useState } from "react";
import { Modal } from "react-bootstrap";
import { ModalHeader } from "../ModalHeader/ModalHeader";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { FavouriteFilterModal } from "../DataModal/FavouriteFilterModal";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { ScrapingFilterData } from "../../services/schemas/Services";

interface FavouriteFilterTableProps extends DataTableProps {
	show: boolean;
	onHide: () => void;
}

type tabKeys = "active" | "inactive";

const FavouriteFilterTable: React.FC<FavouriteFilterTableProps> = ({
	columns = [],
	show,
	onHide,
}: FavouriteFilterTableProps): JSX.Element => {
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
				];

	const activeFilters: ScrapingFilterData[] = dataContext.scrapingFavouriteFilters.filter(
		(filter: ScrapingFilterData): boolean => filter.is_active
	);

	const deactivatedFilters: ScrapingFilterData[] = dataContext.scrapingFavouriteFilters.filter(
		(filter: ScrapingFilterData): boolean => !filter.is_active
	);

	const tabs: { key: tabKeys; title: string }[] = [
		{ key: "active" as const, title: `Active (${activeFilters.length})` },
		{ key: "inactive" as const, title: `Inactive (${deactivatedFilters.length})` },
	];

	const menuItems = (item: ScrapingFilterData): string[] => {
		if (item.is_active) {
			return ["view", "edit", "deactivate", "delete"];
		} else {
			return ["view", "edit", "activate", "delete"];
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
							entityType="scrapingFavouriteFilter"
							data={data}
							columns={defaultColumns}
							initialSortConfig={{ key: "type", direction: "asc" }}
							Modal={FavouriteFilterModal}
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
			id={"favourite-filters-modal"}
		>
			<ModalHeader onClose={onHide}>
				<Modal.Title>Favourite Filters</Modal.Title>
			</ModalHeader>

			<Modal.Body>
				<i style={{ margin: "0 9px 9px 9px", display: "block" }}>
					Favourite filters pin matching scraped job alerts to this widget. Jobs matching any active filter
					will appear here.
				</i>
				{renderTabs()}
			</Modal.Body>
		</Modal>
	);
};

export default FavouriteFilterTable;
