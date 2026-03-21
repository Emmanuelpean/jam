import React, { JSX, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { CustomSelect } from "../rendering/widgets/CustomSelect";
import { DndContext, closestCenter, DragEndEvent, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { SortableContext, useSortable, verticalListSortingStrategy, arrayMove } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { TableColumn } from "../rendering/view/TableColumns";
import { SelectOption } from "../rendering/form/FormOptions";
import "./ColumnConfigSidebar.scss";
import { Direction, SortConfig } from "../../services/schemas/Core";

interface SortableItemProps {
	column: TableColumn;
	isVisible: boolean;
	onToggle: (key: string) => void;
}

const SortableItem: React.FC<SortableItemProps> = ({ column, isVisible, onToggle }: SortableItemProps): JSX.Element => {
	const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: column.key });

	const style = {
		transform: CSS.Transform.toString(transform),
		transition,
	};

	return (
		<div ref={setNodeRef} style={style} className="column-config-item">
			<div className="column-config-drag" {...attributes} {...listeners}>
				<i className="bi bi-grip-vertical"></i>
			</div>
			<Form.Check
				type="checkbox"
				checked={isVisible}
				onChange={(): void => onToggle(column.key)}
				label={column.label}
				id={`col-toggle-${column.key}`}
			/>
		</div>
	);
};

interface ColumnConfigSidebarProps {
	isOpen: boolean;
	onClose: () => void;
	allColumns: TableColumn[];
	columnOrder: string[];
	isDefault: boolean;
	onSave: (keys: string[]) => Promise<void>;
	onReset: () => Promise<void>;
	currentSort: SortConfig;
	onSortChange: (sort: SortConfig) => Promise<void>;
}

interface ColumnState {
	key: string;
	visible: boolean;
}

const ColumnConfigSidebar: React.FC<ColumnConfigSidebarProps> = ({
	isOpen,
	onClose,
	allColumns,
	columnOrder,
	isDefault,
	onSave,
	onReset,
	currentSort,
	onSortChange,
}: ColumnConfigSidebarProps): JSX.Element => {
	const [items, setItems] = useState<ColumnState[]>([]);
	const [saving, setSaving] = useState<boolean>(false);
	const [sortKey, setSortKey] = useState(currentSort.key);
	const [sortDirection, setSortDirection] = useState<Direction>(currentSort.direction);
	const initialised = useRef<boolean>(false);

	useEffect((): void => {
		if (isOpen) {
			initialised.current = false;
			const visibleSet = new Set(columnOrder);
			const ordered: ColumnState[] = columnOrder.map(
				(key: string): ColumnState => ({
					key,
					visible: true,
				})
			);
			allColumns.forEach((col: TableColumn): void => {
				if (!visibleSet.has(col.key)) {
					ordered.push({ key: col.key, visible: false });
				}
			});
			setItems(ordered);
			setSortKey(currentSort.key);
			setSortDirection(currentSort.direction);
			requestAnimationFrame((): void => {
				initialised.current = true;
			});
		}
	}, [isOpen]);

	const persistConfig = useCallback(
		async (currentItems: ColumnState[]): Promise<void> => {
			const visibleKeys: string[] = currentItems
				.filter((item: ColumnState): boolean => item.visible)
				.map((item: ColumnState): string => item.key);
			if (visibleKeys.length === 0) return;
			setSaving(true);
			try {
				await onSave(visibleKeys);
			} finally {
				setSaving(false);
			}
		},
		[onSave]
	);

	useEffect((): void => {
		if (!initialised.current || items.length === 0) return;
		persistConfig(items);
	}, [items]);

	const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

	const handleDragEnd = (event: DragEndEvent): void => {
		const { active, over } = event;
		if (!over || active.id === over.id) return;

		setItems((prev: ColumnState[]): ColumnState[] => {
			const oldIndex: number = prev.findIndex((item: ColumnState): boolean => item.key === active.id);
			const newIndex: number = prev.findIndex((item: ColumnState): boolean => item.key === over.id);
			return arrayMove(prev, oldIndex, newIndex);
		});
	};

	const handleToggle = (key: string): void => {
		setItems((prev: ColumnState[]): ColumnState[] => {
			const updated: ColumnState[] = prev.map(
				(item: ColumnState): ColumnState => (item.key === key ? { ...item, visible: !item.visible } : item)
			);
			if (!updated.some((item: ColumnState): boolean => item.visible)) return prev;
			return updated;
		});
	};

	const handleSortKeyChange = (selected: SelectOption | null): void => {
		if (!selected) return;
		setSortKey(selected.value);
		void onSortChange({ key: selected.value, direction: sortDirection });
	};

	const handleSortDirectionChange = (direction: Direction): void => {
		setSortDirection(direction);
		void onSortChange({ key: sortKey, direction });
	};

	const handleReset = async (): Promise<void> => {
		setSaving(true);
		try {
			await onReset();
			onClose();
		} finally {
			setSaving(false);
		}
	};

	const sortableColumns: TableColumn[] = allColumns.filter(
		(col: TableColumn): boolean | undefined =>
			col.sortable && items.some((item: ColumnState): boolean => item.key === col.key && item.visible)
	);

	const sortOptions: SelectOption[] = useMemo(
		(): SelectOption[] =>
			sortableColumns.map((col: TableColumn): SelectOption => ({ value: col.key, label: col.label })),
		[sortableColumns]
	);

	const selectedSortOption: SelectOption | null =
		sortOptions.find((opt: SelectOption): boolean => opt.value === sortKey) || null;

	const visibleCount: number = items.filter((i: ColumnState): boolean => i.visible).length;

	return (
		<>
			<div id="column-config-sidebar" className={`column-config-sidebar${isOpen ? " open" : ""}`}>
				<div className="column-config-header">
					<h6 className="mb-0">
						<i className="bi bi-layout-three-columns me-2"></i>
						Column Configuration
					</h6>
					<button
						type="button"
						id="column-config-close-btn"
						className="btn-close"
						onClick={onClose}
						aria-label="Close"
					></button>
				</div>
				<div className="column-config-body">
					<div className="column-config-section-label">
						Visibility &amp; Order
						<span className="ms-auto text-nowrap" style={{ fontSize: "0.7rem", opacity: 0.7 }}>
							{visibleCount} / {items.length}
						</span>
					</div>
					<DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
						<SortableContext
							items={items.map((i: ColumnState): string => i.key)}
							strategy={verticalListSortingStrategy}
						>
							{items.map((item: ColumnState): JSX.Element | null => {
								const column: TableColumn | undefined = allColumns.find(
									(col: TableColumn): boolean => col.key === item.key
								);
								if (!column) return null;
								return (
									<SortableItem
										key={item.key}
										column={column}
										isVisible={item.visible}
										onToggle={handleToggle}
									/>
								);
							})}
						</SortableContext>
					</DndContext>

					<div className="column-config-section-label mt-3">Default Sort</div>
					<div className="column-config-sort">
						<CustomSelect
							id="column-config-sort"
							value={selectedSortOption}
							onChange={(selected) => handleSortKeyChange(selected as SelectOption | null)}
							options={sortOptions}
							isSearchable={false}
							isClearable={false}
							size="sm"
							className="mb-2"
						/>
						<Button
							id="column-config-sort-direction-btn"
							variant="outline-primary"
							className="column-config-sort-btn"
							onClick={() => handleSortDirectionChange(sortDirection === "asc" ? "desc" : "asc")}
							title={sortDirection === "asc" ? "Ascending" : "Descending"}
						>
							<i className={`bi bi-sort-${sortDirection === "asc" ? "up" : "down"}`}></i>
							{sortDirection === "asc" ? " Asc" : " Desc"}
						</Button>
					</div>
				</div>
				<div className="column-config-footer">
					<Button
						id="column-config-reset-btn"
						style={{ width: "100%" }}
						onClick={handleReset}
						disabled={saving || isDefault}
					>
						<i className="bi bi-arrow-counterclockwise me-1"></i>
						Reset to Defaults
					</Button>
				</div>
			</div>
		</>
	);
};

export default ColumnConfigSidebar;
