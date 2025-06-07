import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";

const renderCellContent = (column, row) => {
	if (column.render) {
		const renderedContent = column.render(row);

		// Check if the rendered content is empty or falsy
		if (
			!renderedContent ||
			(React.isValidElement(renderedContent) && !renderedContent.props.children) ||
			(typeof renderedContent === "string" && renderedContent.trim() === "")
		) {
			return <span className="text-muted">/</span>;
		}

		return renderedContent;
	}

	// Fallback to the raw value or empty indicator
	return row[column.key] || <span className="text-muted">/</span>;
};

// Generic delete function for table items
export const createGenericDeleteHandler = ({
	endpoint,
	token,
	showConfirm, // Use showConfirm instead of showConfirmation
	showError,
	removeItem,
	setData,
	getItemDisplayName = (item) => `item #${item.id}`,
	itemType = "item",
}) => {
	return async (item) => {
		const itemName = getItemDisplayName(item);

		try {
			await showConfirm({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			// If we reach here, user confirmed
			try {
				const response = await fetch(`http://localhost:8000/${endpoint}/${item.id}/`, {
					method: "DELETE",
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});

				if (response.ok) {
					// Try removeItem first, then setData, then reload as fallback
					if (typeof removeItem === "function") {
						removeItem(item.id);
					} else if (typeof setData === "function") {
						setData((prevData) => prevData.filter((dataItem) => dataItem.id !== item.id));
					} else {
						window.location.reload();
					}
				} else {
					await showError({
						message: `Failed to delete ${itemType.toLowerCase()}. Please try again.`,
					});
				}
			} catch (error) {
				console.error(`Error deleting ${itemType.toLowerCase()}:`, error);
				await showError({
					message: `Failed to delete ${itemType.toLowerCase()}. Please check your connection and try again.`,
				});
			}
		} catch (error) {
			// User cancelled the confirmation
			console.log(`${itemType} deletion cancelled`);
		}
	};
};

// Predefined display name functions for common item types
export const displayNameFunctions = {
	location: (location) => {
		return location.city
			? `${location.city}${location.country ? `, ${location.country}` : ""}`
			: `location #${location.id}`;
	},
	user: (user) => {
		return user.name || user.email || user.username || `user #${user.id}`;
	},
	company: (company) => {
		return company.name || `company #${company.id}`;
	},
	job: (job) => {
		return job.title || `job #${job.id}`;
	},
	project: (project) => {
		return project.name || project.title || `project #${project.id}`;
	},
	task: (task) => {
		return task.title || task.name || `task #${task.id}`;
	},
	category: (category) => {
		return category.name || `category #${category.id}`;
	},
	product: (product) => {
		return product.name || product.title || `product #${product.id}`;
	},
	order: (order) => {
		return order.order_number || `order #${order.id}`;
	},
	invoice: (invoice) => {
		return invoice.invoice_number || `invoice #${invoice.id}`;
	},
	contact: (contact) => {
		const name =
			contact.first_name && contact.last_name
				? `${contact.first_name} ${contact.last_name}`
				: contact.name || contact.email;
		return name || `contact #${contact.id}`;
	},
	article: (article) => {
		return article.title || `article #${article.id}`;
	},
	event: (event) => {
		return event.name || event.title || `event #${event.id}`;
	},
	generic: (item) => `item #${item.id}`,
};

// Utility function to create standardized action buttons
export const createTableAction = (type, onClick, customTitle = null) => {
	const actionTypes = {
		view: {
			label: "View",
			icon: "bi bi-eye",
			className: "btn-action-view",
			title: "View details",
		},
		edit: {
			label: "Edit",
			icon: "bi bi-pencil",
			className: "btn-action-edit",
			title: "Edit item",
		},
		delete: {
			label: "Delete",
			icon: "bi bi-trash",
			className: "btn-action-delete",
			title: "Delete item",
		},
		duplicate: {
			label: "Duplicate",
			icon: "bi bi-copy",
			className: "btn-action-duplicate",
			title: "Duplicate item",
		},
		download: {
			label: "Download",
			icon: "bi bi-download",
			className: "btn-action-download",
			title: "Download item",
		},
		archive: {
			label: "Archive",
			icon: "bi bi-archive",
			className: "btn-action-archive",
			title: "Archive item",
		},
		restore: {
			label: "Restore",
			icon: "bi bi-arrow-counterclockwise",
			className: "btn-action-restore",
			title: "Restore item",
		},
		settings: {
			label: "Settings",
			icon: "bi bi-gear",
			className: "btn-action-settings",
			title: "Item settings",
		},
	};

	const actionConfig = actionTypes[type];
	if (!actionConfig) {
		throw new Error(`Unknown action type: ${type}. Available types: ${Object.keys(actionTypes).join(", ")}`);
	}

	return {
		...actionConfig,
		onClick,
		title: customTitle || actionConfig.title,
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
	filterComponent = null,
	loading = false,
	error = null,
	emptyMessage = "No items found",
	actions = null,
	defaultDisplayText = "/",
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

	// Get sorted and filtered data
	const getSortedData = () => {
		let filteredData = [...data];

		// Filter by search term if provided
		if (searchTerm && columns.some((col) => col.searchable)) {
			const searchTermLower = searchTerm.toLowerCase();
			filteredData = filteredData.filter((item) => {
				return columns.some((column) => {
					if (!column.searchable) return false;
					const value = column.accessor ? column.accessor(item) : item[column.key];
					return value?.toString().toLowerCase().includes(searchTermLower);
				});
			});
		}

		// Sort data
		if (sortConfig.key) {
			filteredData.sort((a, b) => {
				const column = columns.find((col) => col.key === sortConfig.key);
				let aValue, bValue;

				if (column?.accessor) {
					aValue = column.accessor(a);
					bValue = column.accessor(b);
				} else {
					aValue = a[sortConfig.key];
					bValue = b[sortConfig.key];
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
							onClick={() => action.onClick(item)}
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

	// Pagination calculations
	const totalPages = Math.ceil(sortedData.length / pageSize);
	const startIndex = currentPage * pageSize;
	const endIndex = startIndex + pageSize;
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
		setCurrentPage(0); // Reset to first page when changing page size
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
			<div className="d-flex justify-content-between mb-3">
				<div className="d-flex align-items-center gap-3">
					<input
						type="text"
						className="form-control"
						placeholder="Search..."
						value={searchTerm}
						onChange={(e) => onSearchChange(e.target.value)}
						style={{ width: "300px" }}
					/>
					<span className="text-muted small">Showing {sortedData.length} Entries</span>
				</div>

				<Button variant="primary" onClick={onAddClick}>
					{addButtonText}
				</Button>
			</div>

			{/* Filter component if provided */}
			{filterComponent && <div className="mb-3">{filterComponent}</div>}

			{/* Table with rounded corners */}
			<div className="table-responsive">
				<table className="table table-striped table-hover rounded-3 overflow-hidden">
					<thead className="table-dark">
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
							<tr key={item.id || index}>
								{tableColumns.map((column) => (
									<td key={column.key} className="align-middle">
										{renderCellContent(column, item)}
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

			{/* Pagination with reduced spacing */}
			<div className="d-flex justify-content-between align-items-center mt-0ds">
				<div className="d-flex align-items-center gap-1">
					<Button
						variant="outline-secondary"
						size="sm"
						className="py-0 px-2"
						onClick={goToFirstPage}
						disabled={currentPage === 0}
						hidden={currentPage === 0}
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
						hidden={currentPage === 0}
						aria-label="Previous page"
					>
						<i className="bi bi-chevron-left" aria-hidden="true"></i>
					</Button>
					<Button
						variant="outline-secondary"
						size="sm"
						className="py-0 px-2"
						onClick={goToNextPage}
						disabled={currentPage >= totalPages - 1}
						hidden={totalPages === 1}
						aria-label="Next page"
					>
						<i className="bi bi-chevron-right" aria-hidden="true"></i>
					</Button>
					<Button
						variant="outline-secondary"
						size="sm"
						className="py-0 px-2"
						onClick={goToLastPage}
						disabled={currentPage >= totalPages - 1}
						hidden={totalPages === 1}
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
								Show {size} entries
							</option>
						))}
					</Form.Select>
				</div>
			</div>
		</div>
	);
};

export default GenericTable;
