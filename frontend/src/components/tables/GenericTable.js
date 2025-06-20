import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";
import { renderFieldValue } from "../rendering/Renders";
import { api } from "../../services/api";

export const createGenericDeleteHandler = ({
	endpoint,
	token,
	showConfirm,
	showError,
	removeItem,
	setData,
	nameKey,
	itemType = "item",
}) => {
	return async (item) => {
		console.log(nameKey, item);
		const itemName = item[nameKey];

		try {
			await showConfirm({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			// If we reach here, user confirmed
			try {
				await api.delete(`${endpoint}/${item.id}`, token);

				// Try removeItem first, then setData, then reload as fallback
				if (typeof removeItem === "function") {
					removeItem(item.id);
				} else if (typeof setData === "function") {
					setData((prevData) => prevData.filter((dataItem) => dataItem.id !== item.id));
				} else {
					window.location.reload();
				}
			} catch (error) {
				console.error(`Error deleting ${itemType}:`, error);
				await showError({
					message: `Failed to delete ${itemType}. Please check your connection and try again.`,
				});
			}
		} catch (error) {
			console.log(`${itemType} deletion cancelled`);
		}
	};
};

// Utility function to create standardized action buttons
export const createTableAction = (type, onClick) => {
	const actionTypes = {
		view: {
			label: "View",
			icon: "bi bi-eye",
			className: "btn-action-view",
		},
		edit: {
			label: "Edit",
			icon: "bi bi-pencil",
			className: "btn-action-edit",
		},
		delete: {
			label: "Delete",
			icon: "bi bi-trash",
			className: "btn-action-delete",
		},
		duplicate: {
			label: "Duplicate",
			icon: "bi bi-copy",
			className: "btn-action-duplicate",
		},
		download: {
			label: "Download",
			icon: "bi bi-download",
			className: "btn-action-download",
		},
		archive: {
			label: "Archive",
			icon: "bi bi-archive",
			className: "btn-action-archive",
		},
		restore: {
			label: "Restore",
			icon: "bi bi-arrow-counterclockwise",
			className: "btn-action-restore",
		},
	};

	const actionConfig = actionTypes[type];
	if (!actionConfig) {
		throw new Error(`Unknown action type: ${type}. Available types: ${Object.keys(actionTypes).join(", ")}`);
	}

	return {
		...actionConfig,
		onClick,
	};
};

// Utility function to create multiple actions at once
export const createTableActions = (actionConfigs) => {
	return actionConfigs.map((config) => {
		if (typeof config === "string") {
			throw new Error(
				'Action config must include onClick function. Use: { type: "view", onClick: yourFunction }',
			);
		}

		const { type, onClick, title } = config;
		return createTableAction(type, onClick, title);
	});
};

const GenericTable = ({
	data,
	columns,
	sortConfig,
	onSort,
	searchTerm,
	onSearchChange,
	onAddClick,
	addButtonText = "Add Item",
	loading = false,
	error = null,
	emptyMessage = "No items found",
	actions = null,
	onRowClick = null,
	showAllEntries = false,
}) => {
	const [currentPage, setCurrentPage] = useState(0);
	const [pageSize, setPageSize] = useState(10);

	// Handle sorting
	const handleSort = (key) => {
		let direction = "asc";
		if (sortConfig.key === key && sortConfig.direction === "asc") {
			direction = "desc";
		}
		onSort({ key, direction });
	};

	// Handle row click with interactive element check
	const handleRowClick = (event, item) => {
		// Check if the clicked element or any parent is an interactive element
		const isInteractiveElement = (element) => {
			if (!element) return false;

			const tagName = element.tagName?.toLowerCase();
			const isButton = tagName === "button";
			const isLink = tagName === "a";
			const isInput = ["input", "select", "textarea"].includes(tagName);
			const hasOnClick = element.onclick || element.getAttribute("onclick");
			const isClickable =
				element.classList?.contains("clickable-badge") ||
				element.classList?.contains("btn") ||
				element.style?.cursor === "pointer";

			return isButton || isLink || isInput || hasOnClick || isClickable;
		};

		// Check the clicked element and its parents
		let currentElement = event.target;
		while (currentElement && currentElement !== event.currentTarget) {
			if (isInteractiveElement(currentElement)) {
				return; // Don't trigger row click if interactive element was clicked
			}
			currentElement = currentElement.parentElement;
		}

		// If we reach here, it's safe to trigger the row click
		if (onRowClick) {
			onRowClick(item);
		}
	};

	const getSortedData = () => {
		let filteredData = [...data];

		// Filter by search term if provided
		if (searchTerm && columns.some((col) => col.searchable)) {
			const searchTermLower = searchTerm.toLowerCase();
			filteredData = filteredData.filter((item) => {
				return columns.some((column) => {
					if (!column.searchable) return false;

					let value;
					if (column.accessor) {
						value = column.accessor(item);
					} else if (column.searchFields) {
						// Handle nested field searching
						value = column.searchFields
							.map((field) => {
								const parts = field.split(".");
								let obj = item;
								for (const part of parts) {
									obj = obj?.[part];
									if (obj === null || obj === undefined) break;
								}
								return obj;
							})
							.join(" ");
					} else {
						value = item[column.key];
					}

					return value?.toString().toLowerCase().includes(searchTermLower);
				});
			});
		}

		// Sort data
		if (sortConfig.key) {
			filteredData.sort((a, b) => {
				const column = columns.find((col) => col.key === sortConfig.key);
				let aValue, bValue;

				// Enhanced sorting: Check sortFunction first, then sortField, then accessor, then fallback to key
				if (column?.sortFunction && typeof column.sortFunction === "function") {
					// Use custom sorting function
					aValue = column.sortFunction(a);
					bValue = column.sortFunction(b);
				} else if (column?.sortField) {
					// Handle nested field sorting using string path
					if (typeof column.sortField === "string") {
						const parts = column.sortField.split(".");
						aValue = parts.reduce((obj, part) => obj?.[part], a);
						bValue = parts.reduce((obj, part) => obj?.[part], b);
					} else if (typeof column.sortField === "function") {
						// sortField can also be a function
						aValue = column.sortField(a);
						bValue = column.sortField(b);
					}
				} else if (column?.accessor) {
					aValue = column.accessor(a);
					bValue = column.accessor(b);
				} else {
					aValue = a[sortConfig.key];
					bValue = b[sortConfig.key];
				}

				// Handle null/undefined values - always place them at the bottom
				if (aValue == null && bValue == null) return 0;
				if (aValue == null) return 1; // Always place null values at the bottom
				if (bValue == null) return -1; // Always place null values at the bottom

				// Convert to strings for comparison if needed
				if (typeof aValue === "string" && typeof bValue === "string") {
					aValue = aValue.toLowerCase();
					bValue = bValue.toLowerCase();
				}

				if (aValue < bValue) {
					return sortConfig.direction === "asc" ? -1 : 1;
				}
				if (aValue > bValue) {
					return sortConfig.direction === "asc" ? 1 : -1;
				}
				return 0;
			});
		}

		return filteredData;
	};

	// Create columns with actions if provided
	const tableColumns = [...columns];
	if (actions) {
		tableColumns.push({
			key: "actions",
			label: "Actions",
			sortable: false,
			filterable: false,
			render: (item) => (
				<div className="d-flex gap-2">
					{actions.map((action, index) => (
						<button
							key={index}
							className={`btn btn-action ${action.className || ""}`}
							onClick={(event) => {
								event.stopPropagation(); // Add this line
								action.onClick(item, event);
							}}
							title={action.title}
						>
							{action.icon && <i className={action.icon}></i>}
							{action.label}
						</button>
					))}
				</div>
			),
		});
	}

	const sortedData = getSortedData();

	// ----------------------------------------------------- PAGES -----------------------------------------------------

	const totalPages = Math.ceil(sortedData.length / pageSize);
	const startIndex = showAllEntries ? 0 : currentPage * pageSize;
	const endIndex = showAllEntries ? sortedData.length : startIndex + pageSize;
	const currentPageData = sortedData.slice(startIndex, endIndex);

	// Reset to first page when data changes
	React.useEffect(() => {
		setCurrentPage(0);
	}, [searchTerm, data]);

	// Pagination handlers
	const goToFirstPage = () => setCurrentPage(0);
	const goToPreviousPage = () => setCurrentPage(Math.max(0, currentPage - 1));
	const goToNextPage = () => setCurrentPage(Math.min(totalPages - 1, currentPage + 1));
	const goToLastPage = () => setCurrentPage(totalPages - 1);

	const handlePageSizeChange = (newPageSize) => {
		setPageSize(newPageSize);
		setCurrentPage(0);
	};

	if (loading) {
		return (
			<div className="d-flex justify-content-center mt-5">
				<div className="spinner-border" role="status">
					<span className="visually-hidden">Loading...</span>
				</div>
			</div>
		);
	}

	if (error) {
		return <div className="alert alert-danger mt-3">{error}</div>;
	}

	return (
		<div>
			{/* Header with search and add button */}
			<div className="d-flex justify-content-between mb-3" style={{ gap: "1rem" }}>
				<div className="d-flex align-items-center gap-3" style={{ width: "40%" }}>
					<input
						type="text"
						className="form-control"
						placeholder="Search..."
						value={searchTerm}
						onChange={(e) => onSearchChange(e.target.value)}
					/>
					<span className="text-muted small" style={{ whiteSpace: "nowrap" }}>
						Showing {sortedData.length} Entries
					</span>
				</div>

				<Button variant="primary" onClick={onAddClick} style={{ width: "60%" }}>
					{addButtonText}
				</Button>
			</div>

			{/* Table with rounded corners */}
			<div className="table-responsive">
				<table className="table table-striped table-hover rounded-3 overflow-hidden">
					<thead className="custom-header">
						<tr>
							{tableColumns.map((column) => (
								<th key={column.key}>
									<div className="d-flex align-items-center justify-content-between">
										<div
											className={column.sortable ? "cursor-pointer user-select-none" : ""}
											onClick={() => column.sortable && handleSort(column.key)}
										>
											{column.label}
											{column.sortable && (
												<span className="ms-1">
													{sortConfig.key === column.key &&
														sortConfig.direction === "asc" && (
															<i className="bi bi-arrow-up"></i>
														)}
													{sortConfig.key === column.key &&
														sortConfig.direction === "desc" && (
															<i className="bi bi-arrow-down"></i>
														)}
													{sortConfig.key !== column.key && (
														<i className="bi bi-arrow-down-up"></i>
													)}
												</span>
											)}
										</div>
									</div>
								</th>
							))}
						</tr>
					</thead>
					<tbody>
						{currentPageData.map((item, index) => (
							<tr
								key={item.id || index}
								onClick={(event) => handleRowClick(event, item)}
							>
								{tableColumns.map((column, columnIndex) => (
									<td
										key={column.key}
										className="align-middle"
										style={columnIndex === 0 ? { fontWeight: "bold" } : {}}
									>
										{renderFieldValue(column, item)}
									</td>
								))}
							</tr>
						))}
						{currentPageData.length === 0 && (
							<tr>
								<td colSpan={tableColumns.length} className="text-center py-4 text-muted">
									{emptyMessage}
								</td>
							</tr>
						)}
					</tbody>
				</table>
			</div>

			{/* Page controls - Hidden when showAllEntries is true */}
			{!showAllEntries && (
			<div className="d-flex justify-content-between align-items-center mt-0ds">
				<div className="d-flex align-items-center gap-1">
					<Button
						variant="outline-secondary"
						size="sm"
						className="py-0 px-2"
						onClick={goToFirstPage}
						disabled={currentPage === 0}
						hidden={currentPage <= 1}
						aria-label="First page"
					>
						<i className="bi bi-chevron-double-left" aria-hidden="true"></i>
					</Button>
					<Button
						variant="outline-secondary"
						size="sm"
						className="py-0 px-2"
						onClick={goToPreviousPage}
						disabled={currentPage === 0}
						hidden={currentPage <= 1}
						aria-label="Previous page"
					>
						<i className="bi bi-chevron-left" aria-hidden="true"></i>
					</Button>
					<Button
						variant="outline-secondary"
						size="sm"
						className="py-0 px-2"
						onClick={goToNextPage}
						disabled={currentPage >= totalPages - 2}
						hidden={totalPages <= 1}
						aria-label="Next page"
					>
						<i className="bi bi-chevron-right" aria-hidden="true"></i>
					</Button>
					<Button
						variant="outline-secondary"
						size="sm"
						className="py-0 px-2"
						onClick={goToLastPage}
						disabled={currentPage >= totalPages - 2}
						hidden={totalPages <= 1}
						aria-label="Last page"
					>
						<i className="bi bi-chevron-double-right" aria-hidden="true"></i>
					</Button>
				</div>

				<div className="d-flex align-items-center gap-2">
					<span className="small text-muted">
						Page {currentPage + 1} of {totalPages || 1}
					</span>
					<Form.Select
						size="sm"
						style={{ width: "auto", padding: "0.25rem 0.5rem", textAlign: "center" }}
						value={pageSize}
						onChange={(e) => handlePageSizeChange(Number(e.target.value))}
					>
						{[10, 20, 30, 40, 50, 100].map((size) => (
							<option key={size} value={size}>
								Show {size} Entries
							</option>
						))}
					</Form.Select>
				</div>
			</div>
			)}
		</div>
	);
};

export default GenericTable;
