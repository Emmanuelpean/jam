import React, { JSX } from "react";
import { Dropdown } from "react-bootstrap";
import { BulkAction } from "./DataTable";

interface BulkActionsDropdownProps {
	selectedCount: number;
	filteredCount: number;
	actions: BulkAction[];
	onAction: (action: Extract<BulkAction, { type?: "action" }>) => void;
	onClearSelection: () => void;
	className?: string;
}

const BulkActionsDropdown = ({
	selectedCount,
	filteredCount,
	actions,
	onAction,
	onClearSelection,
	className,
}: BulkActionsDropdownProps): JSX.Element => {
	return (
		<Dropdown align="end" className={`bulk-actions-dropdown${className ? ` ${className}` : ""}`}>
			<Dropdown.Toggle
				id="bulk-actions-dropdown"
				variant={selectedCount > 0 ? "primary" : "outline-primary"}
				className="config-btn position-relative"
				style={{ minWidth: "unset" }}
			>
				<i className="bi bi-check2-square"></i>
				{selectedCount > 0 && (
					<span
						className="filter-button-count"
						style={{ position: "absolute", top: "-6px", left: "-6px", fontSize: "0.65rem" }}
					>
						{selectedCount}
					</span>
				)}
			</Dropdown.Toggle>
			<Dropdown.Menu>
				{actions.map((action: BulkAction, i: number): JSX.Element => {
					if (action.type === "divider") return <Dropdown.Divider key={i} />;
					if (action.type === "header") return <Dropdown.Header key={i}>{action.label}</Dropdown.Header>;
					return (
						<Dropdown.Item
							key={i}
							id={action.id}
							className={action.variant?.includes("danger") ? "text-danger" : ""}
							onClick={(): void => onAction(action)}
						>
							{action.icon && <i className={`bi bi-${action.icon} me-2`}></i>}
							{typeof action.label === "function"
								? action.label(selectedCount, filteredCount)
								: action.label}
						</Dropdown.Item>
					);
				})}
				<Dropdown.Divider />
				<Dropdown.Item onClick={onClearSelection}>
					<i className="bi bi-x-circle me-2"></i>Clear selection
				</Dropdown.Item>
			</Dropdown.Menu>
		</Dropdown>
	);
};

export default BulkActionsDropdown;
