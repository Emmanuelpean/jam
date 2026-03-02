import React, { JSX, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button, Form } from "react-bootstrap";
import Select, { SingleValue } from "react-select";
import { DndContext, closestCenter, DragEndEvent, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { SortableContext, useSortable, verticalListSortingStrategy, arrayMove } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { TableColumn } from "../rendering/view/TableColumns";
import { SelectOption } from "../rendering/form/FormOptions";
import { SortConfig, Direction } from "./DataTable";
import "./ColumnConfigSidebar.scss";

interface SortableItemProps {
	column: TableColumn;
	isVisible: boolean;
	onToggle: (key: string) => void;
}

const SortableItem: React.FC<SortableItemProps> = ({ column, isVisible, onToggle }): JSX.Element => {
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
				onChange={() => onToggle(column.key)}
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
}): JSX.Element => {
	const [items, setItems] = useState<{ key: string; visible: boolean }[]>([]);
	const [saving, setSaving] = useState<boolean>(false);
	const [sortKey, setSortKey] = useState(currentSort.key);
	const [sortDirection, setSortDirection] = useState<Direction>(currentSort.direction);
	const initialised = useRef<boolean>(false);

	useEffect(() => {
		if (isOpen) {
			initialised.current = false;
			const visibleSet = new Set(columnOrder);
			const ordered: { key: string; visible: boolean }[] = columnOrder.map((key) => ({ key, visible: true }));
			allColumns.forEach((col) => {
				if (!visibleSet.has(col.key)) {
					ordered.push({ key: col.key, visible: false });
				}
			});
			setItems(ordered);
			setSortKey(currentSort.key);
			setSortDirection(currentSort.direction);
			requestAnimationFrame(() => {
				initialised.current = true;
			});
		}
	}, [isOpen]);

	const persistConfig = useCallback(
		async (currentItems: { key: string; visible: boolean }[]) => {
			const visibleKeys = currentItems.filter((item) => item.visible).map((item) => item.key);
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

	useEffect(() => {
		if (!initialised.current || items.length === 0) return;
		persistConfig(items);
	}, [items]);

	const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

	const handleDragEnd = (event: DragEndEvent) => {
		const { active, over } = event;
		if (!over || active.id === over.id) return;

		setItems((prev) => {
			const oldIndex = prev.findIndex((item) => item.key === active.id);
			const newIndex = prev.findIndex((item) => item.key === over.id);
			return arrayMove(prev, oldIndex, newIndex);
		});
	};

	const handleToggle = (key: string) => {
		setItems((prev) => {
			const updated = prev.map((item) => (item.key === key ? { ...item, visible: !item.visible } : item));
			if (!updated.some((item) => item.visible)) return prev;
			return updated;
		});
	};

	const handleSortKeyChange = (selected: SingleValue<SelectOption>) => {
		if (!selected) return;
		setSortKey(selected.value);
		onSortChange({ key: selected.value, direction: sortDirection });
	};

	const handleSortDirectionChange = (direction: Direction) => {
		setSortDirection(direction);
		onSortChange({ key: sortKey, direction });
	};

	const handleReset = async () => {
		setSaving(true);
		try {
			await onReset();
			onClose();
		} finally {
			setSaving(false);
		}
	};

	const sortableColumns = allColumns.filter(
		(col) => col.sortable && items.some((item) => item.key === col.key && item.visible)
	);

	const sortOptions: SelectOption[] = useMemo(
		() => sortableColumns.map((col) => ({ value: col.key, label: col.label })),
		[sortableColumns]
	);

	const selectedSortOption = sortOptions.find((opt) => opt.value === sortKey) || null;

	const visibleCount = items.filter((i) => i.visible).length;

	return (
		<>
			<div className={`column-config-sidebar${isOpen ? " open" : ""}`}>
				<div className="column-config-header">
					<h6 className="mb-0">
						<i className="bi bi-layout-three-columns me-2"></i>
						Column Configuration
					</h6>
					<button type="button" className="btn-close" onClick={onClose} aria-label="Close"></button>
				</div>
				<div className="column-config-body">
					<div className="column-config-section-label">
						Visibility &amp; Order
						<span className="ms-auto text-nowrap" style={{ fontSize: "0.7rem", opacity: 0.7 }}>
							{visibleCount} / {items.length}
						</span>
					</div>
					<DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
						<SortableContext items={items.map((i) => i.key)} strategy={verticalListSortingStrategy}>
							{items.map((item) => {
								const column = allColumns.find((col) => col.key === item.key);
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
						<Select<SelectOption>
							value={selectedSortOption}
							onChange={handleSortKeyChange}
							options={sortOptions}
							isSearchable={false}
							isClearable={false}
							menuPortalTarget={document.body}
							className="react-select-container column-config-sort-select"
							classNamePrefix="react-select"
						/>
						<Button
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
					<Button style={{ width: "100%" }} onClick={handleReset} disabled={saving || isDefault}>
						<i className="bi bi-arrow-counterclockwise me-1"></i>
						Reset to Defaults
					</Button>
				</div>
			</div>
		</>
	);
};

export default ColumnConfigSidebar;
