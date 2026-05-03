import React from "react";
import { Form, Spinner } from "react-bootstrap";
import { useDelayedLoading } from "../../../hooks/useDelayedLoading";

interface ActionToggleProps {
	id: string;
	label: string;
	checked: boolean;
	onChange: () => void;
	disabled?: boolean;
	loading?: boolean;
	className?: string;
}

export const ActionToggle: React.FC<ActionToggleProps> = ({
	id,
	label,
	checked,
	onChange,
	disabled = false,
	loading = false,
	className = "",
}) => {
	const visibleLoading = useDelayedLoading(loading);

	return (
		<div className={`d-flex align-items-center ${className}`}>
			{visibleLoading && (
				<Spinner animation="border" size="sm" className="me-2" aria-label="Loading toggle state" />
			)}
			<Form.Check
				type="switch"
				id={id}
				label={label}
				checked={checked}
				onChange={onChange}
				disabled={disabled || loading || visibleLoading}
				style={{ userSelect: "none" }}
			/>
		</div>
	);
};
