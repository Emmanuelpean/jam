import React from "react";
import { ActionButton } from "../../components/rendering/form/ActionButton";

interface DashboardToolbarProps {
	isEditMode: boolean;
	isSaving: boolean;
	onEdit: () => void;
	onCancel: () => void;
	onSave: () => void;
	onAddWidget: () => void;
	onReset: () => void;
}

export const DashboardToolbar: React.FC<DashboardToolbarProps> = ({
	isEditMode,
	isSaving,
	onEdit,
	onCancel,
	onSave,
	onAddWidget,
	onReset,
}) => (
	<div className="dashboard-edit-toolbar">
		<div className="dashboard-edit-toolbar-inner">
			<button
				className={`sidebar-icon-btn ${isEditMode ? "btn btn-outline-secondary active-edit" : "dashboard-edit-trigger-inline"}`}
				onClick={isEditMode ? onCancel : onEdit}
				title={isEditMode ? "Cancel" : "Customise dashboard"}
			>
				<i className={`bi bi-${isEditMode ? "x-lg" : "pencil-square"}`}></i>
			</button>
			{isEditMode && (
				<>
					<ActionButton
						variant="primary"
						size="sm"
						fullWidth={false}
						className="sidebar-icon-btn"
						loading={isSaving}
						defaultIcon="bi bi-check-lg"
						style={{ width: 40 }}
						onClick={onSave}
						tooltip="Save layout"
						tooltipPlacement="left"
					/>
					<ActionButton
						variant="outline-primary"
						size="sm"
						fullWidth={false}
						className="sidebar-icon-btn"
						defaultIcon="bi bi-plus-lg"
						style={{ width: 36 }}
						onClick={onAddWidget}
						tooltip="Add widget"
						tooltipPlacement="left"
					/>
					<ActionButton
						variant="outline-danger"
						size="sm"
						fullWidth={false}
						className="sidebar-icon-btn"
						defaultIcon="bi bi-arrow-counterclockwise"
						style={{ width: 36 }}
						onClick={onReset}
						tooltip="Reset to default"
						tooltipPlacement="left"
					/>
				</>
			)}
		</div>
	</div>
);
