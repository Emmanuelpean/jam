import React, { JSX } from "react";
import { Card } from "react-bootstrap";

interface StatCardProps {
	name: string;
	value: number;
	icon: string;
	variant: string;
	description?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
	name,
	value,
	icon,
	variant,
	description,
}: StatCardProps): JSX.Element => (
	<Card className="h-100 shadow-sm border-0">
		<Card.Body className="d-flex align-items-center">
			<div className="flex-grow-1">
				<div className="d-flex align-items-center mb-2">
					<i
						className={`bi bi-${icon} text-${variant} me-2`}
						style={{ fontSize: "1.5rem" }}
					></i>
					<h5 className="card-itemName mb-0">{name}</h5>
				</div>
				<div className={`display-6 fw-bold text-${variant}`}>{value}</div>
				{description && <small className="text-muted">{description}</small>}
			</div>
		</Card.Body>
	</Card>
);
