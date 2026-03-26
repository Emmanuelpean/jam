import React from "react";
import { Form, Spinner } from "react-bootstrap";

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
	return (
		<div className={`d-flex align-items-center ${className}`}>
			{loading && <Spinner animation="border" size="sm" className="me-2" aria-label="Loading toggle state" />}
			<Form.Check
				type="switch"
				id={id}
				label={label}
				checked={checked}
				onChange={onChange}
				disabled={disabled || loading}
				style={{ userSelect: "none" }}
			/>
		</div>
	);
};
